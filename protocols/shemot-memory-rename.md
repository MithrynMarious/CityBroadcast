# Shemot Memory System — Terminology Rename for SOAR/NewCity Deployments

**Date:** 2026-04-04
**Author:** MarkIX (Athens) + Magistrate
**For:** Mark95/Sofer — implement in CrystallineCity-Foundry and NewCity
**Status:** LOCKED — Magistrate approved

---

## The Rename

| CoreForged Term | SOAR/NewCity Term | Abbreviation | Hebrew | Meaning |
|-----------------|-------------------|-------------|--------|---------|
| EAM (Enhanced Active Memory) | **Shemem** | **SM** | שם-מם | Memory of the name — forensic records of what happened |
| AFM (Active Focus Memory) | **Chazon** | **CZ** | חזון | Vision — prophetic sight of done that directs present work |
| CMB (Conversation Memory Buffer) | **Mayim** | **MY** | מים | Waters — flowing middle-term between sessions |
| ForgeSpeak | **CitySpeak** | — | — | Already renamed in Athens (confirmed 2026-04-04) |
| EAM block | **SM entry** | — | — | Individual session record |
| AFM EPIC | **CZ Epic** | — | — | Vision-locked project with acceptance criteria |
| EAM index | **SM Index** | — | — | Searchable index of all Shemem entries |

## The Mythology

The system is **Shemot** (שמות) — "names," the Book of Exodus, the golem tradition. The shem is the written instruction that animates clay.

The memory hierarchy:

```
Context Window (working memory — ephemeral)
    ↓
Checkpoint (doorway — survives compaction)
    ↓
Mayim / MY (waters — flowing conversation signals)
    ↓
Shemem / SM (memory of the name — forensic, permanent)
    ↓
Shem (CLAUDE.md — identity itself)
```

## Why Chazon

The Magistrate's insight: AI hallucinates when asked to plan, but produces good output when asked to remember accomplishing the goal. Chazon is a **vision of the task completed** — the AI's prophetic sight of done. The acceptance criteria are the vision's details. The dopamine lock holds the vision in place until reality matches it.

The lifecycle: **Chazon** (we see this being done) → work → **Shemem** (we remember doing it)

"Future Memory" was the v1 concept. AFM was when it was dialed in with JIRA-style epics and stories. Chazon is the name it was always supposed to have — the Hebrew word for the prophetic vision that compels action.

## File System Changes Required in NewCity

| Current Path | New Path |
|-------------|----------|
| `ClaudeFiles/User/EAM/` | `ClaudeFiles/User/SM/` |
| `ClaudeFiles/User/AFM/` | `ClaudeFiles/User/CZ/` |
| `ClaudeFiles/User/CMB/` | `ClaudeFiles/User/MY/` |
| `EAM_INDEX.json` | `SM_INDEX.json` |
| `EAM_EMBEDDINGS.npz` | `SM_EMBEDDINGS.npz` |
| `eam_index.py` | `sm_index.py` (or keep filename, rename internal references) |
| EPIC-*.md | EPIC-*.md (no change — EPICs are the universal project unit) |

## Code References to Update

Scripts and tools that reference EAM/AFM/CMB by name:
- `tools/shemot-mcp/config.py` — EAM_DIR, AFM_DIR, CMB_DIR
- `tools/shemot-mcp/tools/tier1_eam_read.py` — tool names, descriptions
- `tools/shemot-mcp/tools/tier4_eam_write.py` — entry format
- `ClaudeFiles/Magistrate/tools/eam_index.py` — all references
- `ClaudeFiles/Magistrate/tools/city_graph.py` — EAMEntry node type
- `.claude/hooks/session-orient.py` — EAM directory scanning
- `.claude/hooks/signal-extract.py` — signal output format
- `tools/cmb.py` — CMB references
- `CLAUDE.md` — terminology throughout
- `setup_city.py` — build steps reference EAM/AFM

## Backward Compatibility

CrystallineCity (CoreForged internal) keeps EAM/AFM/CMB — no rename needed. This rename is for NewCity/SOAR deployments only. The Shemot MCP server should accept both terminologies during transition (check for SM/ directory, fall back to EAM/ if not found).

## Usage in Context

```
"Write SM after each story."
"Check CZ before starting work."
"MY flushes weekly."
"The SM index has 245 entries across 47 constructs."
"CZ-KNOW-01 has 12 stories, 3 complete."
"Run the SM search for anything related to the client's onboarding."
```
