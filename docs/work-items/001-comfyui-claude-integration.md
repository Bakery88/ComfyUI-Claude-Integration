# Work Item 001: ComfyUI + Claude Code Integration

## Summary

Build a ComfyUI integration for Claude Code by combining **shawnrushefsky/comfyui-mcp** (tool layer) with architectural patterns borrowed from **MCKRUZ/ComfyUI-Expert** (knowledge/orchestration layer). The MCP server gives Claude the ability to interact with ComfyUI; the knowledge layer tells Claude what to do, when, and how.

## Motivation

ComfyUI is a powerful node-based UI for Stable Diffusion workflows. Existing solutions either provide raw MCP tools without guidance (shawnrushefsky) or markdown-based orchestration without proper tool abstraction (ComfyUI-Expert). Neither is complete alone. Combining them produces an integration where Claude can intelligently drive ComfyUI workflows with domain knowledge, validation, and structured decision-making.

## Architecture

```
┌─────────────────────────────────────────────┐
│  Knowledge Layer (CLAUDE.md + skills/)       │
│  Routing table, authority matrix, skills     │
├─────────────────────────────────────────────┤
│  Tool Layer (shawnrushefsky/comfyui-mcp)     │
│  40 MCP tools, API client, job tracking      │
├─────────────────────────────────────────────┤
│  Execution Layer (ComfyUI on :8188)          │
│  Diffusion models, node graph execution      │
└─────────────────────────────────────────────┘
```

### Target Directory Structure

```
ComfyUI-Claude-Integration/
├── CLAUDE.md                          # Orchestrator: routing table, authority matrix, foundation context
├── .mcp.json                          # MCP server config (shawnrushefsky/comfyui-mcp via Docker)
│
├── foundation/                        # Tier 1: always-loaded, <2K tokens total
│   ├── hardware-profile.md            # Local GPU specs, ComfyUI launch flags
│   ├── model-landscape.md             # Top models per category (timestamped)
│   ├── skill-registry.md              # Skill dependency graph
│   └── api-quick-ref.md               # MCP tool cheat sheet (replaces raw API ref)
│
├── skills/                            # Tier 2: read on demand per routing table
│   ├── comfyui-inventory/
│   │   └── SKILL.md                   # Discover models/nodes via list_models + list_nodes
│   ├── comfyui-prompt-engineer/
│   │   └── SKILL.md                   # Model-specific prompt crafting (FLUX, SDXL, SD1.5)
│   ├── comfyui-workflow-builder/
│   │   └── SKILL.md                   # Build workflows using MCP tools, not curl
│   ├── comfyui-troubleshooter/
│   │   └── SKILL.md                   # Error patterns, quality issue decision trees
│   └── comfyui-generation/
│       └── SKILL.md                   # End-to-end generation orchestration
│
├── state/                             # Runtime state (gitignored)
│   └── inventory.json                 # Cached output of list_models + list_nodes
│
├── workflows/                         # Reusable workflow templates (ComfyUI API format JSON)
│   └── .gitkeep
│
└── docs/
    └── work-items/
        └── 001-comfyui-claude-integration.md
```

## Tasks

### Phase 1: Foundation

#### 1.1 Install and configure shawnrushefsky/comfyui-mcp
- Pull Docker image `ghcr.io/shawnrushefsky/comfyui-mcp:latest`
- Create `.mcp.json` pointing to the MCP server
- Verify connectivity to a local ComfyUI instance
- Test basic tool calls: `get_status`, `list_models`, `run_workflow`

#### 1.2 Write CLAUDE.md orchestrator
- **Routing table**: Map user intents to skills
  - "Generate an image" -> `comfyui-generation`
  - "What models do I have?" -> `comfyui-inventory`
  - "Help me write a prompt" -> `comfyui-prompt-engineer`
  - "Build a workflow" -> `comfyui-workflow-builder`
  - "Something went wrong" -> `comfyui-troubleshooter`
- **Authority matrix**: Define autonomous vs. user-confirmation boundaries
  - Autonomous: workflow validation, inventory checks, parameter selection
  - Requires confirmation: running generations (GPU cost), saving/deleting templates, installing models
- **Foundation context**: Inline hardware profile and model landscape summary (<2K tokens)
- **Invariant**: "Always call `list_models` or check `state/inventory.json` before building any workflow"

#### 1.3 Write foundation files
- `hardware-profile.md` — detect and document local GPU, VRAM, ComfyUI version
- `model-landscape.md` — top 3 models per category (txt2img, img2img, inpainting, ControlNet, LoRA) with VRAM requirements and `<!-- Updated: DATE -->` timestamps
- `skill-registry.md` — dependency graph showing which skills chain into which
- `api-quick-ref.md` — cheat sheet of the MCP tool names (not raw HTTP endpoints) with one-line descriptions

### Phase 2: Skills (adapted from ComfyUI-Expert)

#### 2.1 comfyui-inventory
- Adapted from Expert's inventory skill
- Calls `list_models` and `list_nodes` MCP tools instead of curl/filesystem scan
- Caches results to `state/inventory.json` with 1-hour TTL
- Provides a "what can I do?" summary based on installed models and nodes

#### 2.2 comfyui-prompt-engineer
- Ported from Expert's prompt engineering skill
- Model-specific rules:
  - FLUX: natural language, CFG 3.5, no negative prompt
  - SDXL: quality tags, CFG 7-9, negative prompt matters
  - SD 1.5: tag-based, CFG 7-11
- References `get_prompting_guide` MCP tool as a fallback
- Decision tree for model selection based on task

#### 2.3 comfyui-workflow-builder
- Adapted from Expert's workflow builder
- Uses MCP tools instead of raw JSON construction:
  - `get_node_info` to verify node inputs/outputs
  - `find_nodes_by_type` to discover available nodes
  - `build_node` to generate valid node JSON
  - `validate_workflow` before execution
  - `search_templates` / `get_template` for starting points
- Embeds common workflow patterns as decision trees, not hardcoded JSON
- VRAM estimation table for pipeline planning

#### 2.4 comfyui-troubleshooter
- Ported from Expert's troubleshooter skill
- Error pattern matching (CUDA OOM, missing nodes, model load failures)
- Quality issue decision trees (artifacts, color issues, composition problems)
- References `get_status` and `get_queue` for diagnostic info

#### 2.5 comfyui-generation
- New skill combining Expert's pipeline pattern with MCP tools
- 5-step process:
  1. **Gather context**: read inventory, understand user intent
  2. **Plan**: select model, build prompt (via prompt-engineer skill), choose workflow
  3. **Validate**: `validate_workflow`, check VRAM estimate
  4. **Execute**: `run_workflow` (async), monitor via `get_task`
  5. **Review**: retrieve output via `get_image`, assess quality, suggest refinements
- Retry strategy: seed randomization -> parameter adjustment -> model fallback

### Phase 3: Polish

#### 3.1 Eval framework
- Per-skill `eval/` directories with test cases
- Assertions: workflow JSON validity, required nodes present, parameter ranges correct
- Baseline comparison: with-skill vs. without-skill generation quality

#### 3.2 Online/offline dual mode
- Online: MCP tools talk to running ComfyUI
- Offline: skills generate workflow JSON saved to `workflows/` for manual import
- Inventory falls back to last cached `state/inventory.json`

#### 3.3 Staleness tracking
- `model-landscape.md` and `inventory.json` get `<!-- Updated: DATE -->` timestamps
- CLAUDE.md checks freshness at session start
- Configurable thresholds: models 3 months, nodes 2 months, inventory 1 hour

## What We Take from Each Source

### From shawnrushefsky/comfyui-mcp (use as-is)
- The MCP server (40 tools, Docker deployment)
- ComfyUI API client (REST + WebSocket)
- Async job tracking with SQLite
- Workflow validation engine
- Capability detection from `/object_info`
- Auto-discovery of ComfyUI instances
- Custom template save/search/delete

### From MCKRUZ/ComfyUI-Expert (adapt patterns)
- 3-tier context system (foundation / working / reference)
- CLAUDE.md routing table and authority matrix
- Skill file structure (decision tree -> steps -> settings tables -> integration points)
- Inventory-first validation invariant
- Model-specific prompt engineering rules
- Troubleshooting decision trees
- Eval framework structure
- Staleness tracking with timestamps
- Online/offline dual mode

### Discarded
- Expert's raw curl calls (MCP server handles API interaction)
- Expert's PowerShell scripts (platform-specific, replaced by MCP tools)
- Expert's OpenClaw compatibility layer (unnecessary)
- Expert's video/voice/YouTube skills (out of scope unless needed later)
- shawnrushefsky's SVG/font tools (unlikely to need)
- shawnrushefsky's `recommend_workflow` (routing table is more flexible)

## Open Questions

1. **Docker vs. local Node.js for MCP server?** Docker is more reproducible but adds latency. Local npx is simpler for development.
2. **Which ComfyUI-Expert skills to port first?** Prompt engineer and workflow builder have the highest value. Inventory is the dependency.
3. **Template strategy**: Use shawnrushefsky's built-in 70+ examples as a starting library, or curate a smaller focused set?
4. **Workflow storage**: Save custom workflows in the repo's `workflows/` dir, or rely on the MCP server's SQLite template storage?
5. **Multi-GPU / remote ComfyUI**: The MCP server supports `COMFYUI_URL` env var. Worth documenting a remote setup path?
