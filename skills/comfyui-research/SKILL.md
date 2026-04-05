# Skill: ComfyUI Research

> Monitor the ComfyUI ecosystem for new models, custom nodes, techniques, and best practices. Keep foundation knowledge current through structured source scanning and staleness tracking.

## When to Use

- User asks "What's new in ComfyUI?" / "Any new models?" / "What should I update?"
- Staleness warnings fire for `foundation/model-landscape.md` (>3 months old)
- User asks about a model, node, or technique not in current foundation files
- Before a major project to ensure knowledge is current
- Periodically (user-triggered) to maintain knowledge freshness

## Dependencies

- None — this is an independent knowledge maintenance skill
- **Outputs feed into**: `foundation/model-landscape.md`, `foundation/skill-registry.md`, `state/research-log.json`

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `get_capabilities` | Check what the current ComfyUI instance supports |
| `list_models` | Compare installed models against latest recommendations |
| `list_nodes` | Compare installed nodes against recommended nodes |
| `get_download_url` | Get download links for recommended models |
| `save_note` | Save research findings as persistent notes |
| `search_notes` | Check if a finding was already noted |

Additionally, this skill uses **web search** (when available) to check external sources.

## Procedure

### Step 1: Assess Current Knowledge State

Check freshness of all tracked resources:

1. Read `foundation/model-landscape.md` → check `<!-- Updated: DATE -->` timestamp
2. Read `foundation/skill-registry.md` → check if new skill categories are missing
3. Read `state/research-log.json` → check when last scan was performed
4. Read `state/inventory.json` → compare installed models against known recommendations

Generate a freshness report:

```
## Knowledge Freshness Report

| Resource | Last Updated | Threshold | Status |
|---|---|---|---|
| model-landscape.md | [date] | 3 months | [Fresh/Stale] |
| skill-registry.md | [date] | 3 months | [Fresh/Stale] |
| Last research scan | [date] | 1 month | [Fresh/Stale] |
| inventory.json | [date] | 1 hour | [Fresh/Stale] |
```

### Step 2: Scan Sources

Check the following source categories. Prioritize based on what's stale.

#### 2a: Model Ecosystem

Research current state of:

| Category | What to Check | Key Questions |
|---|---|---|
| **Checkpoints** | Latest FLUX, SDXL, SD3 releases | New versions? Performance improvements? VRAM reductions? |
| **LoRAs** | Popular community LoRAs | New style LoRAs? Improved face LoRAs? |
| **ControlNet** | New control types and architectures | FLUX ControlNet updates? New preprocessors? |
| **Upscale** | New upscale models | Improvements over ESRGAN/SUPIR? |
| **VAE** | Updated VAE releases | Better VAEs for specific architectures? |

**Sources to check**:
- HuggingFace trending models (filter: diffusers, safetensors)
- CivitAI top models by category (if accessible)
- GitHub releases for key model repos (black-forest-labs/flux, stability-ai)

#### 2b: Custom Nodes

Research current state of:

| Area | What to Check |
|---|---|
| **Core nodes** | ComfyUI core updates, new built-in nodes |
| **ComfyUI Manager** | New featured nodes, popularity rankings |
| **Workflow tools** | New utility nodes (image processing, masking, etc.) |
| **AI tools** | New SAM versions, face detection, depth estimation |
| **Architecture support** | New architecture-specific nodes (FLUX, SD3, etc.) |

**Sources to check**:
- ComfyUI GitHub releases / changelog
- ComfyUI Manager node database
- Popular custom node repos (ltdrdata, cubiq, Fannovel16, etc.)

#### 2c: Techniques and Workflows

Research current best practices:

| Area | What to Check |
|---|---|
| **Prompting** | New prompting techniques for latest models |
| **Training** | Updated LoRA training best practices, new tools |
| **Quality** | New quality improvement techniques |
| **Speed** | New optimization methods (quantization, distillation) |
| **Workflows** | Community workflow innovations |

**Sources to check**:
- ComfyUI community forums and Discord highlights
- Tutorial creators (key YouTube channels)
- Research papers with practical impact (distillation, etc.)

### Step 3: Analyze Findings

For each finding, assess:

1. **Relevance**: Does this affect our current skills or workflows?
2. **Impact**: Is this a minor improvement or a significant change?
3. **Maturity**: Is this stable and recommended, or experimental?
4. **Action required**: Do we need to update foundation files, skills, or just note it?

Categorize each finding:

| Category | Action |
|---|---|
| **New recommended model** | Update `model-landscape.md` (with user confirmation) |
| **Deprecated model** | Mark as deprecated in `model-landscape.md` |
| **New essential node** | Note in research log; update relevant skill if applicable |
| **New technique** | Note in research log; update relevant skill if it's stable |
| **Breaking change** | Flag to user immediately; may require skill updates |
| **Minor improvement** | Note in research log for reference |

### Step 4: Update Foundation Files (with confirmation)

Per the authority matrix, **always ask the user before modifying foundation files**.

#### Updating model-landscape.md

Present proposed changes:

```
## Proposed Updates to model-landscape.md

### Additions
- [Model name]: [why it's recommended, category, VRAM requirement]

### Changes
- [Model name]: [what changed — e.g., "new version available", "VRAM requirement reduced"]

### Deprecations
- [Model name]: [why — e.g., "superseded by [new model]", "no longer maintained"]

Shall I apply these updates?
```

If confirmed, update the file and refresh the `<!-- Updated: DATE -->` timestamp.

#### Updating skill-registry.md

If new capabilities warrant a new skill or changes to existing skill dependencies, propose the update similarly.

### Step 5: Log the Scan

Write scan results to `state/research-log.json`:

```json
{
  "scans": [
    {
      "timestamp": "2026-04-04T12:00:00Z",
      "sources_checked": ["huggingface", "comfyui-github", "community"],
      "findings": [
        {
          "category": "model",
          "title": "FLUX.2-dev released",
          "impact": "high",
          "action_taken": "updated model-landscape.md",
          "details": "..."
        }
      ],
      "files_updated": ["foundation/model-landscape.md"],
      "next_scan_recommended": "2026-05-04T12:00:00Z"
    }
  ]
}
```

### Step 6: Present Summary

Give the user a concise research summary:

```
## Research Scan Complete

**Sources checked**: [list]
**Date**: [date]

### Key Findings
1. [Most impactful finding — e.g., "FLUX.2-dev is now available with improved quality"]
2. [Second finding]
3. [Third finding]

### Recommendations
- **Install**: [models/nodes worth installing]
- **Update**: [models/nodes with newer versions]
- **Remove**: [deprecated items]

### Your Setup vs. Current Best Practices
- ✅ [things that are up to date]
- ⚠️ [things that could be improved]
- ❌ [things that are missing or outdated]

### Foundation Files Updated
- [list files that were updated, or "No changes needed"]

Next recommended scan: [date based on staleness thresholds]
```

## Monitored Source Registry

Key sources to track. This list can grow over time as the user discovers valuable resources.

### GitHub Repositories

| Repo | What to Track | Check Frequency |
|---|---|---|
| `comfyanonymous/ComfyUI` | Core releases, new built-in nodes | Monthly |
| `black-forest-labs/flux` | FLUX model releases | Monthly |
| `ltdrdata/ComfyUI-Manager` | Node ecosystem changes | Monthly |
| `shawnrushefsky/comfyui-mcp` | MCP tool updates, new tools | Monthly |
| `cubiq/ComfyUI_IPAdapter_plus` | IP-Adapter updates | Quarterly |
| `Fannovel16/comfyui_controlnet_aux` | ControlNet preprocessor updates | Quarterly |
| `ltdrdata/ComfyUI-Impact-Pack` | Impact Pack (FaceDetailer, etc.) | Quarterly |

### Model Hubs

| Source | What to Track |
|---|---|
| HuggingFace (trending + new) | New checkpoint/LoRA releases |
| CivitAI (top models) | Community model rankings |

### Community

| Source | What to Track |
|---|---|
| ComfyUI Reddit/Discord | Workflow innovations, tips |
| Tutorial channels | New technique demonstrations |

## Staleness Integration

This skill is tightly integrated with the staleness tracking system in `foundation/staleness.yml`:

- **Triggers research**: When `model-landscape.md` crosses its 3-month threshold
- **Updates timestamps**: After modifying foundation files, refreshes `<!-- Updated: -->` markers
- **Recommends next scan**: Based on rate of ecosystem changes
- **Logs scan dates**: In `state/research-log.json` for tracking scan frequency

## Offline Mode

| Capability | Online | Offline |
|---|---|---|
| Check foundation freshness | Yes | Yes (read files locally) |
| Scan web sources | Yes | No (skip; note in report) |
| Compare against inventory | Yes | Use cached inventory |
| Update foundation files | Yes (with confirmation) | Yes (with confirmation) |
| Log scan results | Yes | Yes |

In offline mode, the skill can still assess staleness and propose updates based on cached knowledge. Web source scanning is deferred until online.
