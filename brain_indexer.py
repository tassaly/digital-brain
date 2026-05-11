#!/usr/bin/env python3
"""
Digital Brain Indexer
Scans all Markdown files, extracts YAML frontmatter, and builds a JSON knowledge graph
including WikiLink [[connections]] between notes.
"""

import os
import re
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    raise SystemExit("Run: pip install pyyaml")


BRAIN_ROOT = Path(__file__).parent
PARA_DIRS = ["00_Inbox", "01_Projects", "02_Areas", "03_Resources", "04_Archive"]
INDEX_OUTPUT = BRAIN_ROOT / "brain_index.json"
GRAPH_OUTPUT = BRAIN_ROOT / "knowledge_graph.json"

WIKILINK_RE = re.compile(r"\[\[([^\[\]|]+?)(?:\|[^\[\]]+?)?\]\]")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def file_id(path: Path) -> str:
    # use folder/stem so README in different PARA dirs get unique IDs
    folder = para_folder(path)
    return f"{folder}/{path.stem}" if folder != "unknown" else path.stem


def extract_frontmatter(text: str) -> tuple[dict, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        meta = {}
    body = text[match.end():]
    return meta, body


def extract_wikilinks(text: str) -> list[str]:
    return WIKILINK_RE.findall(text)


def para_folder(path: Path) -> str:
    for part in path.parts:
        if part in PARA_DIRS:
            return part
    return "unknown"


def content_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:8]


def scan_notes() -> list[dict]:
    notes = []
    for para_dir in PARA_DIRS:
        folder = BRAIN_ROOT / para_dir
        if not folder.exists():
            continue
        for md_file in sorted(folder.rglob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            meta, body = extract_frontmatter(text)
            links = extract_wikilinks(body)

            notes.append({
                "id": file_id(md_file),
                "path": str(md_file.relative_to(BRAIN_ROOT)),
                "folder": para_folder(md_file),
                "title": meta.get("title", md_file.stem.replace("-", " ").replace("_", " ").title()),
                "date": str(meta.get("date", "")),
                "status": meta.get("status", ""),
                "tags": meta.get("tags", []),
                "source": meta.get("source", ""),
                "links_to": links,
                "hash": content_hash(text),
                "indexed_at": datetime.now(timezone.utc).isoformat(),
                # keep first 500 chars of body as preview
                "preview": body.strip()[:500],
            })
    return notes


def build_graph(notes: list[dict]) -> dict[str, Any]:
    # node map: id -> metadata (without full preview to keep graph lean)
    nodes = {
        n["id"]: {
            "title": n["title"],
            "folder": n["folder"],
            "tags": n["tags"],
            "status": n["status"],
        }
        for n in notes
    }

    # edges: every [[WikiLink]] becomes a directed edge; we also collect backlinks
    edges: list[dict] = []
    backlinks: dict[str, list[str]] = {n["id"]: [] for n in notes}

    for note in notes:
        for target in note["links_to"]:
            # WikiLinks may include path segments — normalise to stem
            target_id = Path(target).stem
            edges.append({"source": note["id"], "target": target_id})
            if target_id in backlinks:
                backlinks[target_id].append(note["id"])
            else:
                backlinks[target_id] = [note["id"]]

    return {"nodes": nodes, "edges": edges, "backlinks": backlinks}


def write_index(notes: list[dict]) -> None:
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_notes": len(notes),
        "by_folder": {},
        "notes": notes,
    }
    for note in notes:
        data["by_folder"].setdefault(note["folder"], []).append(note["id"])

    INDEX_OUTPUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[index] Wrote {len(notes)} notes → {INDEX_OUTPUT.name}")


def write_graph(graph: dict) -> None:
    GRAPH_OUTPUT.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")
    node_count = len(graph["nodes"])
    edge_count = len(graph["edges"])
    print(f"[graph] {node_count} nodes, {edge_count} edges → {GRAPH_OUTPUT.name}")


def print_summary(notes: list[dict]) -> None:
    print("\n── Digital Brain Index Summary ──")
    by_folder: dict[str, int] = {}
    for note in notes:
        by_folder[note["folder"]] = by_folder.get(note["folder"], 0) + 1
    for folder in PARA_DIRS:
        count = by_folder.get(folder, 0)
        print(f"  {folder}: {count} note(s)")
    print(f"\n  Total: {len(notes)} notes")

    all_tags: dict[str, int] = {}
    for note in notes:
        for tag in note["tags"]:
            all_tags[tag] = all_tags.get(tag, 0) + 1
    if all_tags:
        top = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:10]
        print("\n  Top tags: " + ", ".join(f"{t}({c})" for t, c in top))
    print()


if __name__ == "__main__":
    notes = scan_notes()
    write_index(notes)
    graph = build_graph(notes)
    write_graph(graph)
    print_summary(notes)
