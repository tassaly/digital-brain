#!/usr/bin/env python3
"""
Digital Brain MCP Server
Exposes three tools to Claude via the Model Context Protocol (JSON-RPC over stdio):
  • search_notes(query)       — semantic search using local sentence embeddings
  • link_notes(source, target) — add bidirectional [[WikiLink]] between two files
  • summarize_inbox()          — triage 00_Inbox and propose PARA destinations

Dependencies:
    pip install sentence-transformers numpy pyyaml
"""

import json
import sys
import os
import re
import logging
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("brain-mcp")

# ── lazy imports so the server starts fast and logs a clear error if missing ──

def _require(pkg: str, install: str):
    try:
        return __import__(pkg)
    except ImportError:
        log.error("Missing dependency: pip install %s", install)
        sys.exit(1)


BRAIN_ROOT = Path(__file__).parent
PARA_DIRS = ["00_Inbox", "01_Projects", "02_Areas", "03_Resources", "04_Archive"]
PARA_DESCRIPTIONS = {
    "01_Projects": "Active work with a clear outcome and deadline.",
    "02_Areas": "Ongoing responsibilities with no end date.",
    "03_Resources": "Reference material on topics of interest.",
    "04_Archive": "Completed or no-longer-active items.",
}

WIKILINK_RE = re.compile(r"\[\[([^\[\]|]+?)(?:\|[^\[\]]+?)?\]\]")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# ── helpers ───────────────────────────────────────────────────────────────────

def all_markdown_files() -> list[Path]:
    files = []
    for d in PARA_DIRS:
        folder = BRAIN_ROOT / d
        if folder.exists():
            files.extend(sorted(folder.rglob("*.md")))
    return files


def read_note(path: Path) -> tuple[str, str]:
    """Return (frontmatter_block, body)."""
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if m:
        return m.group(1), text[m.end():]
    return "", text


def note_text_for_embedding(path: Path) -> str:
    _, body = read_note(path)
    # combine path stem + body for richer context
    return f"{path.stem.replace('-', ' ')}\n{body}"


def resolve_note_path(name: str) -> Path | None:
    """Find a note file given a stem or partial path."""
    stem = Path(name).stem
    for path in all_markdown_files():
        if path.stem == stem:
            return path
    return None


# ── embedding layer ───────────────────────────────────────────────────────────

_model = None
_embeddings: list[Any] = []
_paths: list[Path] = []


def _load_model():
    global _model
    if _model is None:
        SentenceTransformer = _require("sentence_transformers", "sentence-transformers").SentenceTransformer
        log.info("Loading embedding model (all-MiniLM-L6-v2)…")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        log.info("Model loaded.")
    return _model


def _build_index():
    global _embeddings, _paths
    np = _require("numpy", "numpy")
    model = _load_model()
    _paths = all_markdown_files()
    if not _paths:
        log.warning("No markdown files found — index is empty.")
        _embeddings = []
        return
    texts = [note_text_for_embedding(p) for p in _paths]
    log.info("Encoding %d notes…", len(texts))
    _embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    log.info("Index ready.")


def _cosine_similarity(a, b):
    np = _require("numpy", "numpy")
    a, b = np.array(a), np.array(b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom else 0.0


# ── tool implementations ──────────────────────────────────────────────────────

def search_notes(query: str, top_k: int = 5) -> dict:
    """Semantic search across all notes using cosine similarity."""
    np = _require("numpy", "numpy")
    if not _embeddings:
        _build_index()
    if not _paths:
        return {"results": [], "message": "No notes found in digital_brain."}

    model = _load_model()
    q_vec = model.encode([query], convert_to_numpy=True)[0]

    scored = [
        (_cosine_similarity(q_vec, emb), path)
        for emb, path in zip(_embeddings, _paths)
    ]
    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, path in scored[:top_k]:
        _, body = read_note(path)
        results.append({
            "score": round(score, 4),
            "id": path.stem,
            "path": str(path.relative_to(BRAIN_ROOT)),
            "preview": body.strip()[:300],
        })

    return {"query": query, "results": results}


def link_notes(source: str, target: str) -> dict:
    """Add a bidirectional [[WikiLink]] between two notes."""
    src_path = resolve_note_path(source)
    tgt_path = resolve_note_path(target)

    if not src_path:
        return {"error": f"Source note not found: {source!r}"}
    if not tgt_path:
        return {"error": f"Target note not found: {target!r}"}

    def _add_link(path: Path, link_target: str) -> bool:
        text = path.read_text(encoding="utf-8")
        tag = f"[[{link_target}]]"
        if tag in text:
            return False  # already linked
        # append to end of file
        separator = "\n" if text.endswith("\n") else "\n\n"
        path.write_text(text + separator + tag + "\n", encoding="utf-8")
        return True

    added_fwd = _add_link(src_path, tgt_path.stem)
    added_bwd = _add_link(tgt_path, src_path.stem)

    # invalidate embedding index so next search re-encodes
    global _embeddings, _paths
    _embeddings, _paths = [], []

    return {
        "source": src_path.stem,
        "target": tgt_path.stem,
        "forward_link_added": added_fwd,
        "backward_link_added": added_bwd,
        "message": "Links updated." if (added_fwd or added_bwd) else "Both links already existed.",
    }


def summarize_inbox() -> dict:
    """
    Read all notes in 00_Inbox and propose a PARA destination for each,
    with a one-line rationale. Uses keyword heuristics + embedding similarity
    against the PARA descriptions.
    """
    inbox = BRAIN_ROOT / "00_Inbox"
    files = sorted(inbox.glob("*.md")) if inbox.exists() else []
    if not files:
        return {"inbox_count": 0, "proposals": [], "message": "Inbox is empty."}

    np = _require("numpy", "numpy")
    model = _load_model()

    para_labels = list(PARA_DESCRIPTIONS.keys())
    para_desc_vecs = model.encode(list(PARA_DESCRIPTIONS.values()), convert_to_numpy=True)

    proposals = []
    for path in files:
        _, body = read_note(path)
        note_vec = model.encode([body[:1000]], convert_to_numpy=True)[0]

        scores = {
            label: _cosine_similarity(note_vec, desc_vec)
            for label, desc_vec in zip(para_labels, para_desc_vecs)
        }
        best = max(scores, key=lambda k: scores[k])

        proposals.append({
            "file": path.name,
            "suggested_folder": best,
            "confidence": round(scores[best], 4),
            "scores": {k: round(v, 4) for k, v in scores.items()},
            "rationale": PARA_DESCRIPTIONS[best],
            "preview": body.strip()[:200],
        })

    proposals.sort(key=lambda x: x["confidence"], reverse=True)
    return {
        "inbox_count": len(files),
        "proposals": proposals,
        "note": "Move files manually or call link_notes() after deciding.",
    }


# ── MCP JSON-RPC dispatcher ───────────────────────────────────────────────────

TOOLS = {
    "search_notes": {
        "description": "Semantic search across all notes in the digital brain.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language search query"},
                "top_k": {"type": "integer", "description": "Number of results (default 5)", "default": 5},
            },
            "required": ["query"],
        },
    },
    "link_notes": {
        "description": "Add a bidirectional [[WikiLink]] between two notes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Source note name or stem"},
                "target": {"type": "string", "description": "Target note name or stem"},
            },
            "required": ["source", "target"],
        },
    },
    "summarize_inbox": {
        "description": "Triage all notes in 00_Inbox and propose which PARA folder each belongs to.",
        "inputSchema": {"type": "object", "properties": {}},
    },
}


def handle_request(req: dict) -> dict:
    method = req.get("method", "")
    req_id = req.get("id")

    def ok(result):
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    def err(code, msg):
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": msg}}

    if method == "initialize":
        return ok({
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "digital-brain", "version": "1.0.0"},
        })

    if method == "tools/list":
        return ok({"tools": [{"name": k, **v} for k, v in TOOLS.items()]})

    if method == "tools/call":
        params = req.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})
        try:
            if name == "search_notes":
                result = search_notes(**args)
            elif name == "link_notes":
                result = link_notes(**args)
            elif name == "summarize_inbox":
                result = summarize_inbox(**args)
            else:
                return err(-32601, f"Unknown tool: {name}")
            return ok({"content": [{"type": "text", "text": json.dumps(result, indent=2)}]})
        except Exception as exc:
            log.exception("Tool error")
            return err(-32000, str(exc))

    if method == "notifications/initialized":
        return None  # no response for notifications

    return err(-32601, f"Method not found: {method}")


def run_stdio():
    log.info("Digital Brain MCP Server started (stdio transport).")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError as exc:
            resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}
            print(json.dumps(resp), flush=True)
            continue

        resp = handle_request(req)
        if resp is not None:
            print(json.dumps(resp), flush=True)


if __name__ == "__main__":
    run_stdio()
