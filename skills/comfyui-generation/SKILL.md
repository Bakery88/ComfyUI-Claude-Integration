# Skill: ComfyUI Generation

> End-to-end image generation orchestrator. Coordinates inventory, prompt engineering, workflow building, and execution.

## When to Use

- User asks "Generate an image" / "Create a picture of..." / "Make me a..."
- Any request that results in running a ComfyUI workflow to produce an image

## Dependencies

This skill orchestrates all others:
- **comfyui-inventory** — verify models/nodes before building (always first)
- **comfyui-prompt-engineer** — craft the prompt for the selected model
- **comfyui-workflow-builder** — build or select the workflow
- **comfyui-troubleshooter** — handle failures during execution

Read these sub-skills as needed during the procedure below. Do not read all upfront.

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `run_workflow` | Execute the workflow (returns task ID) |
| `get_task` | Poll task status |
| `get_task_result` | Get completed task result |
| `get_image` | Retrieve generated image as base64 |
| `name_generation` | Assign a descriptive name to the generation |

Plus all tools from sub-skills (inventory, workflow builder, etc.)

## The 5-Step Generation Process

### Step 1: Gather Context

1. **Check inventory** (read `comfyui-inventory` skill):
   - Load `state/inventory.json` (refresh if stale)
   - Know what models, nodes, and VRAM are available

2. **Understand user intent**:
   - What do they want to create? (subject, style, mood)
   - Any specific requirements? (resolution, model preference, ControlNet)
   - Is there a reference image? (img2img, inpainting, ControlNet)

If the request is vague, ask clarifying questions before proceeding:
- "What style are you going for?" (photorealistic, artistic, anime, etc.)
- "Any specific resolution or aspect ratio?"
- "Do you have a model preference?"

### Step 2: Plan

Make these decisions (see decision trees below):

1. **Select model** — based on user intent + available models + VRAM
2. **Select workflow type** — txt2img, img2img, inpainting, ControlNet, etc.
3. **Craft prompt** — read `comfyui-prompt-engineer` skill, apply model-specific rules
4. **Set parameters** — CFG, steps, sampler, scheduler, resolution (from prompt-engineer tables)

**Model Selection Decision Tree**:
```
What does the user want?
├── Photorealistic image
│   ├── VRAM ≥ 24GB → FLUX.2-dev or FLUX.1-dev
│   ├── VRAM 16-24GB → FLUX.1-dev FP8
│   ├── VRAM 12-16GB → FLUX.2-klein or SDXL
│   └── VRAM < 12GB → SDXL or SD 1.5
├── Fast iteration / drafts
│   ├── FLUX.2-klein (4 steps, fast)
│   └── SD 1.5 (low VRAM, fast)
├── Specific LoRA or style
│   └── Use the architecture the LoRA was trained for
├── Inpainting
│   └── Use inpainting-specific checkpoint (match architecture)
├── ControlNet guided
│   └── Use architecture matching available ControlNet models
└── User specified a model → Use that model
```

If model selection involves tradeoffs (e.g., quality vs. speed, VRAM is tight), **ask the user** per the authority matrix.

### Step 3: Build and Validate

1. **Build workflow** — read `comfyui-workflow-builder` skill:
   - Check for matching templates first (`search_templates`)
   - If no template, build from pipeline pattern
   - Wire all nodes correctly
2. **Validate** — call `validate_workflow`
   - If validation fails, fix issues per workflow-builder guidance
   - Re-validate after fixes
3. **VRAM check** — estimate total VRAM from workflow-builder tables
   - If over budget, suggest optimizations before running

### Step 4: Execute

**This step requires user confirmation** (per authority matrix).

Present the plan to the user before executing:
```
Ready to generate:
- Model: [name]
- Prompt: [summary or full prompt]
- Resolution: [WxH]
- Parameters: [CFG, steps, sampler]
- Estimated VRAM: [amount]

Shall I run this?
```

Once confirmed:

1. Call `run_workflow` with the validated workflow JSON
2. Receive a task ID
3. Poll `get_task` for status (brief intervals)
4. On completion, call `get_task_result` to check for success
5. If failed, route to troubleshooter (Step 5 failure path)

### Step 5: Review

**On success**:
1. Call `get_image` to retrieve the generated image
2. Present the image to the user
3. Optionally call `name_generation` with a descriptive name
4. Ask if they want refinements:
   - Different seed (autonomous — just re-run)
   - Prompt adjustments (re-enter at Step 2)
   - Different model (ask user, re-enter at Step 2)
   - Upscaling (build upscale workflow)

**On failure**:
1. Read `comfyui-troubleshooter` skill
2. Match the error pattern
3. Apply the fix
4. Re-enter at the appropriate step:
   - Parameter issue → Step 2
   - Workflow issue → Step 3
   - System issue → Step 1 (re-check status)

## Retry Strategy

When a generation produces poor quality (user says "that's not what I wanted"):

```
Retry sequence:
1. New seed (autonomous) — maybe it's just a bad seed
2. Prompt refinement — re-read prompt-engineer, improve specificity
3. Parameter adjustment — try different CFG, steps, or sampler
4. Model swap (ask user) — different model may handle the subject better
```

Apply retries in order. Don't jump to model swap before trying simpler fixes.

## Batch Workflow

When the user wants multiple variations:
1. Generate with different seeds (vary seed in the workflow)
2. Use batch_size parameter if VRAM allows
3. Present all results for comparison
4. Let user pick favorites for refinement

## Saving Results

After a successful generation the user likes:
- Offer to save the workflow to `workflows/` for reuse (requires confirmation)
- Offer to save as a template via `save_template` (requires confirmation)
- The generated image is already stored by ComfyUI in its output directory

## Offline Mode

When ComfyUI is not running (`get_status` fails), this skill switches to **workflow-export mode**:

1. **Steps 1-3 still work**: Inventory uses cache, prompt engineering is fully local, workflow building generates JSON
2. **Step 3 partial**: `validate_workflow` is skipped (requires ComfyUI) — warn user the workflow is unvalidated
3. **Step 4 skipped**: Cannot call `run_workflow` — instead, save the workflow JSON to `workflows/{descriptive-name}.json`
4. **Step 5 skipped**: No image to review

**Tell the user**:
```
ComfyUI is not running. I've built the workflow and saved it to workflows/{name}.json.
To generate:
1. Start ComfyUI
2. Import the workflow JSON via the ComfyUI web UI (drag and drop or Load)
3. Click "Queue Prompt" to run
```

When the user later says ComfyUI is running, re-check with `get_status` and offer to validate + execute any previously saved workflows.
