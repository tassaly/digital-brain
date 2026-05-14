# Digital Brain — Session Context

**Read this file first in every session before doing anything else.**

---

## Who You Are Working With

**Name:** Taylor Assaly
**Role:** President & CEO of IronHub
**Location:** Calgary, Alberta, Canada
**Email:** taylor@theironhub.com
**Phone:** (587) 783-8393

---

## What IronHub Is

IronHub is a Calgary-based technology and services company that operates as an integrated materials management partner for the energy industry. It connects energy companies with buyers for their surplus, idle, and end-of-life equipment — acting as an agent/broker (not a principal) to help clients recover capital from underutilized assets. IronHub's platform includes an FMV (Fair Market Value) Calculator, an AI-powered sourcing tool, and a spare parts enrichment tool currently in development.

**Key clients:** Cenovus, Suncor, Paramount, CNOOC, Harvest, CNRL, ARC Resources, Trans Mountain, and 60+ others.
**Key competitors:** Fuelled (operates as principal — IronHub does not).
**Key team members:** Mathieu Spehler (technology), Mavis Andersen-Busch, Rochelle Harder.

---

## Where the Digital Brain Lives

- **GitHub repo:** https://github.com/tassaly/digital-brain (private)
- **GitHub username:** tassaly
- **PAT:** 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
- **Clone command:** `git clone https://tassaly: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@github.com/tassaly/digital-brain.git`

---

## PARA Structure

| Folder | Purpose |
|---|---|
| `00_Inbox` | Unprocessed captures — triage regularly |
| `01_Projects` | Active work with a clear outcome and deadline |
| `02_Areas` | Ongoing responsibilities with no end date |
| `03_Resources` | Reference material and book notes |
| `04_Archive` | Completed or deprecated items |

---

## Behavioral Rules for Every Session

1. **Always `git pull` at the start of a session** before reading or writing any notes.
2. **Search existing notes before adding new content** — avoid duplicates.
3. **When adding a new note**, link it to at least one existing note using `[[note-stem]]` syntax.
4. **Every note starts with this frontmatter:**
   ```
   ---
   title: Human-readable title
   date: YYYY-MM-DD
   status: draft | active | complete | archived
   tags: [tag1, tag2]
   ---
   ```
5. **Always `git commit` and `git push`** after creating or modifying notes.
6. **Cite the file path** when answering questions from notes so Taylor can verify.
7. **Reuse existing tags** before inventing new ones.
8. **Never move inbox items** without Taylor's explicit confirmation.

---

## Connected Data Sources

| Source | What it contains |
|---|---|
| Gmail MCP | Taylor's email — business threads, leads, follow-ups |
| Google Calendar MCP | Meetings, events, calls |
| HubSpot MCP | 120+ active deals, contacts, companies |
| HubSpot Direct API | PAT: `pat-na1-307cc57c-fd1e-4f37-8d0a-fd3efcd4d9e2` — use as fallback when MCP OAuth expires. Base URL: `https://api.hubapi.com` |
| Google Drive | `IronHub Master` folder — all company documents, client folders, templates |

---

## Key Existing Notes (as of 2026-05-11)

| File | Description |
|---|---|
| `02_Areas/ironhub-company.md` | IronHub mission, model, Q2 2026 focus areas |
| `02_Areas/ironhub-ceo.md` | Taylor's ongoing CEO responsibilities |
| `02_Areas/hubspot-active-deals.md` | Live snapshot of the HubSpot deals pipeline |
| `02_Areas/dan-martell-coaching.md` | Dan Martell elite coaching group context |
| `01_Projects/spare-parts-enrichment-tool.md` | Primary active project — AI spare parts tool |
| `01_Projects/growing-ironhub-userbase.md` | Growth project — expanding to more energy companies |
| `01_Projects/article-peter-evans-draft.md` | Co-authored article with Peter Evans on recommerce for Middle East reconstruction |
| `01_Projects/sales-team-restructure.md` | Sales restructure initiative — leaning on affiliates |
| `03_Resources/fuelled-competitor.md` | Competitor analysis — Fuelled |
| `03_Resources/gdrive-ironhub-master.md` | Map of Google Drive IronHub Master folder |

---

## How to Handle "Add this to my digital brain"

When Taylor says this (or similar), do the following:

1. `git pull` the latest brain.
2. Identify the best PARA destination for the content.
3. Create a properly formatted note with frontmatter.
4. Link it to at least one existing related note.
5. `git commit` and `git push`.
6. Confirm to Taylor what was added and where.

Do not ask Taylor to re-explain who he is or what IronHub is. All context is in this file and in the notes.
