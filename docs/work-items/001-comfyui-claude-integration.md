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

### Phase 4: Advanced Skills (adapted from ComfyUI-Expert)

Additional skills ported from ComfyUI-Expert's broader skill set. These cover the advanced image workflows that the core 5 skills don't address directly.

#### 4.1 comfyui-upscale
- Dedicated upscaling skill extracted from Expert's character-gen pipeline
- Tile-based upscaling for large images (Ultimate SD Upscale pattern)
- Model-based upscaling (4x-UltraSharp, 4x-Foolhardy-Remacri, SUPIR)
- Latent upscaling (hires fix pattern: generate small, upscale, re-denoise)
- VRAM-aware: tile size selection based on available memory
- Decision tree: when to use model upscale vs. latent upscale vs. SUPIR

#### 4.2 comfyui-controlnet
- Dedicated ControlNet skill extracted from Expert's character-gen pipeline
- Supported control types: Canny, Depth, OpenPose, Tile, Lineart, Scribble
- Architecture-specific guidance: SD 1.5, SDXL, and FLUX ControlNet variants
- Multi-ControlNet stacking (combining pose + depth, etc.)
- Preprocessor node selection (Canny edge detector, DWPose, MiDaS depth, etc.)
- Strength and start/end step tuning per control type

#### 4.3 comfyui-face-id
- Identity preservation skill adapted from Expert's character-gen
- Methods ranked by quality: InfiniteYou > FLUX Kontext > PuLID Flux 2 > IP-Adapter FaceID > InstantID > ReActor
- Face detail restoration: FaceDetailer, CodeFormer, GFPGAN
- Consistent character generation across multiple images
- Reference image requirements and preparation
- VRAM requirements per method (some need 24GB+)

#### 4.4 comfyui-lora-training
- End-to-end LoRA training guide adapted from Expert
- Dataset preparation: 10-30 images, captioning strategy, trigger words
- FLUX LoRA training: AI-Toolkit, rank 16, 1500 steps, 4e-4 lr (24GB or 9GB with NF4)
- SDXL LoRA training: Kohya_ss, rank 32, 10 epochs
- Evaluation protocol for overfitting detection
- Post-training integration into ComfyUI workflows (strength 0.7-0.9)
- Decision tree: when to train LoRA vs. use zero-shot methods (IP-Adapter, InstantID)

#### 4.5 comfyui-prompt-interview
- Interactive prompt discovery for vague/exploratory requests
- Guided 4-7 question conversational flow
- Branching paths by creation type: portrait, scene, product, abstract, concept art
- Outputs: positive/negative prompts + settings table + pipeline recommendation
- Complements prompt-engineer (direct refinement) with interview (guided discovery)

#### 4.6 comfyui-inpaint
- Dedicated inpainting and outpainting skill
- Mask creation guidance (manual mask, SAM auto-mask, text-guided mask)
- Architecture-specific inpainting: FLUX inpaint models, SDXL inpainting, SD 1.5 inpainting
- Denoise strength tuning (low for small edits, high for full replacement)
- Outpainting / image extension workflows
- Iterative refinement: inpaint → evaluate → re-inpaint cycle

#### 4.7 comfyui-research
- Self-updating knowledge base monitor for the ComfyUI ecosystem
- Monitors key sources for new models, nodes, techniques, and best practices:
  - **GitHub repos**: ComfyUI core, comfyui-mcp, popular custom node repos (ComfyUI-Manager, etc.)
  - **HuggingFace**: Trending models, newly released checkpoints/LoRAs
  - **Community channels**: Notable tutorial creators, workflow-sharing communities
- Scan procedure:
  1. Check monitored sources for updates since last scan
  2. Extract relevant knowledge (new model releases, node updates, technique discoveries)
  3. Update foundation files: `model-landscape.md`, `skill-registry.md` (with user confirmation)
  4. Generate staleness report for all tracked resources
- Integrates with staleness tracking: flags model-landscape.md entries older than 3 months
- Outputs structured update summaries: what's new, what's deprecated, what needs attention
- User-triggered (not automatic) — runs when explicitly asked or when staleness warnings fire
- Can recommend model upgrades (e.g., "FLUX.2-dev is now available, replaces FLUX.1-dev")
- Updates `state/research-log.json` with scan history and findings

#### Dependency Updates

```
comfyui-inventory (foundation)
    │
    ├── comfyui-prompt-engineer
    ├── comfyui-prompt-interview (new — feeds into prompt-engineer)
    │
    ├── comfyui-workflow-builder
    │   ├── comfyui-upscale (new — specialized workflow pattern)
    │   ├── comfyui-controlnet (new — specialized workflow pattern)
    │   ├── comfyui-face-id (new — specialized workflow pattern)
    │   └── comfyui-inpaint (new — specialized workflow pattern)
    │
    ├── comfyui-lora-training (new — independent, references inventory for model info)
    │
    └── comfyui-generation (orchestrates all above)

comfyui-troubleshooter (independent)
comfyui-research (independent — updates foundation files, triggers staleness checks)
```

#### Routing Table Additions

| User Intent | Skill | Pre-Check |
|---|---|---|
| "Upscale this image" / "Make it higher resolution" | `comfyui-upscale` | Inventory |
| "Use ControlNet" / "Match this pose" / "Follow this outline" | `comfyui-controlnet` | Inventory |
| "Keep the same face" / "Use this person's face" | `comfyui-face-id` | Inventory |
| "Train a LoRA" / "Fine-tune on these images" | `comfyui-lora-training` | Inventory |
| "I want to make something but I'm not sure what" | `comfyui-prompt-interview` | Inventory |
| "Fix this part of the image" / "Extend the image" | `comfyui-inpaint` | Inventory |
| "What's new in ComfyUI?" / "Any model updates?" | `comfyui-research` | — |

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
- Expert's `comfyui-api` skill (covered by MCP tools + generation skill)
- Expert's `project-manager` skill (video-production-oriented)
- Expert's `comfyui-research` skill (adapted in Phase 4 as comfyui-research — ecosystem knowledge monitor)
- shawnrushefsky's SVG/font tools (unlikely to need)
- shawnrushefsky's `recommend_workflow` (routing table is more flexible)

## Open Questions

1. **Docker vs. local Node.js for MCP server?** Docker is more reproducible but adds latency. Local npx is simpler for development.
2. **Which ComfyUI-Expert skills to port first?** Prompt engineer and workflow builder have the highest value. Inventory is the dependency.
3. **Template strategy**: Use shawnrushefsky's built-in 70+ examples as a starting library, or curate a smaller focused set?
4. **Workflow storage**: Save custom workflows in the repo's `workflows/` dir, or rely on the MCP server's SQLite template storage?
5. **Multi-GPU / remote ComfyUI**: The MCP server supports `COMFYUI_URL` env var. Worth documenting a remote setup path?
