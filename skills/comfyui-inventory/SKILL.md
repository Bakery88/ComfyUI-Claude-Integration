# Skill: ComfyUI Inventory

> Discover installed models, nodes, and capabilities. This is the foundation skill — run it before any other skill.

## When to Use

- User asks "What models do I have?" / "What can I do?" / "What's installed?"
- Another skill needs model or node validation (they depend on this skill)
- Session startup when `state/inventory.json` is missing or stale (>1 hour)

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `list_models` | Enumerate all installed models (checkpoints, LoRAs, VAEs, ControlNets, etc.) |
| `list_nodes` | Enumerate all installed ComfyUI nodes |
| `get_capabilities` | Detect capabilities of the connected ComfyUI instance |
| `get_status` | Verify ComfyUI is running and get GPU/version info |

## Procedure

### Step 1: Check Cache Freshness

Read `state/inventory.json`. If it exists, check the `timestamp` field (ISO 8601 format):
- **Fresh** (< threshold from `foundation/staleness.yml`, default 1 hour): Use cached data, skip to Step 3
- **Stale** (≥ threshold) or **missing**: Continue to Step 2

### Step 2: Scan via MCP

Run these calls (can be parallel):

1. `get_status` — verify ComfyUI is connected, capture GPU info
2. `list_models` — get all available models by type
3. `list_nodes` — get all available nodes
4. `get_capabilities` — detect supported features

Then write the combined result to `state/inventory.json` with this structure:

```json
{
  "timestamp": "2026-04-04T12:00:00Z",
  "gpu": {
    "model": "...",
    "vram_gb": 0
  },
  "models": {
    "checkpoints": [],
    "loras": [],
    "vaes": [],
    "controlnet": [],
    "upscale_models": [],
    "embeddings": [],
    "clip": [],
    "other": []
  },
  "nodes": [],
  "capabilities": {}
}
```

### Step 3: Summarize for User (if user-facing request)

Present a clear summary organized by capability:

```
## Your ComfyUI Setup

**GPU**: [model] — [VRAM]GB VRAM
**ComfyUI Version**: [version]

### Models Installed
- **Checkpoints**: [count] ([list top ones, note architecture: FLUX/SDXL/SD1.5])
- **LoRAs**: [count] ([list or summarize])
- **VAEs**: [count]
- **ControlNet**: [count] ([list types])
- **Upscale Models**: [count]

### What You Can Do
Based on your installed models and [VRAM]GB VRAM:
- ✅ [list capabilities — e.g., "txt2img with FLUX.1-dev", "SDXL inpainting"]
- ⚠️ [list marginal capabilities — e.g., "FLUX FP16 may be tight on VRAM"]
- ❌ [list missing capabilities — e.g., "No video models installed"]
```

### Step 4: Update Hardware Profile (if first scan)

If `foundation/hardware-profile.md` still has placeholder values (`_detect via get_status_`), update it with the actual GPU info from `get_status`.

## Model Architecture Detection

When listing checkpoints, identify the architecture:
- **FLUX**: filenames often contain "flux", "FLUX" — 12B+ params
- **SDXL**: filenames contain "sdxl", "xl" — typically 6.6B params
- **SD 1.5**: filenames contain "v1-5", "sd15", or are legacy models — ~860M params
- **SD 3.x**: filenames contain "sd3" — newer architecture
- When uncertain, note "unknown architecture" rather than guessing

This matters because other skills (prompt-engineer, workflow-builder) need architecture info to select the right workflow pattern and prompting style.

## Validation Helper

Other skills call into inventory for validation. When validating:

**Model validation**: Check if a model name appears in the appropriate `models.*` array. Use fuzzy matching (case-insensitive, ignore file extension) since users may not type exact filenames.

**Node validation**: Check if a node class name appears in the `nodes` array. Node names are exact (case-sensitive).

If a required model or node is missing:
1. Tell the user what's missing
2. Suggest where to get it (use `get_download_url` for models, link to ComfyUI Manager for nodes)
3. Do NOT proceed with a workflow that references missing components

## Offline Behavior

If `get_status` fails (ComfyUI not running):
- Fall back to last cached `state/inventory.json` (warn that it may be stale)
- If no cache exists, inform the user that ComfyUI must be running for inventory scan
- Other skills can still function with cached inventory data
