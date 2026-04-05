# Skill: ComfyUI Workflow Builder

> Build valid ComfyUI workflows using MCP tools for node discovery, construction, and validation.

## When to Use

- User asks "Build a workflow" / "Make a workflow for..."
- Called by `comfyui-generation` skill when a custom workflow is needed
- User wants to modify or extend an existing workflow

## Dependencies

- **comfyui-inventory**: Must verify all models and nodes exist before building
- Read `foundation/api-quick-ref.md` for available MCP tools

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `get_node_info` | Get detailed inputs/outputs for a specific node |
| `find_nodes_by_type` | Discover nodes by input/output type |
| `build_node` | Generate valid node JSON with proper defaults |
| `validate_workflow` | Validate complete workflow before execution |
| `search_templates` | Find existing workflow templates to start from |
| `get_template` | Build workflow from a template with parameters |
| `save_template` | Save workflow as reusable template (requires user confirmation) |
| `list_examples` | Browse 70+ official example workflows |
| `get_example_workflow` | Fetch an example as a starting point |

## Procedure

### Step 1: Understand the Request

Determine what kind of workflow the user needs:
- **txt2img**: Text prompt → image (most common)
- **img2img**: Image + prompt → modified image
- **inpainting**: Image + mask + prompt → filled region
- **ControlNet**: Image + control signal + prompt → guided generation
- **upscaling**: Low-res image → high-res image
- **Custom pipeline**: Combination of the above or specialized nodes

### Step 2: Check for Templates

Before building from scratch, check if a template exists:
1. `search_templates` with keywords matching the request
2. If a good match exists, use `get_template` to get a parameterized workflow
3. If no template matches, also check `list_examples` for official examples

Templates save time and are pre-validated. Prefer them over manual construction.

### Step 3: Select the Pipeline Pattern

Based on the request type and available models (from inventory), select the right node pattern:

#### txt2img Pipeline

```
Model Loader → CLIP Text Encode (positive) → 
                CLIP Text Encode (negative) → KSampler → VAE Decode → Save Image
```

**Nodes by architecture**:

| Architecture | Loader Node | CLIP Node | KSampler | VAE Decode |
|---|---|---|---|---|
| FLUX | UNETLoader + DualCLIPLoader + VAELoader | CLIPTextEncode | KSampler | VAEDecode |
| SDXL | CheckpointLoaderSimple | CLIPTextEncode (x2 for base+refiner) | KSampler | VAEDecode |
| SD 1.5 | CheckpointLoaderSimple | CLIPTextEncode | KSampler | VAEDecode |

#### img2img Pipeline

```
Load Image → VAE Encode → [same as txt2img from KSampler] 
                            (set denoise 0.4-0.7)
```

#### Inpainting Pipeline

```
Load Image → Load Mask → VAE Encode (Inpaint) → KSampler → VAE Decode → Save Image
```
Use inpainting-specific checkpoint if available.

#### ControlNet Pipeline

```
[txt2img pipeline] + Load ControlNet Model → Apply ControlNet → [feeds into KSampler]
```

#### Upscaling Pipeline

```
Load Image → Upscale Model Loader → Image Upscale With Model → Save Image
```

### Step 4: Build Nodes

For each node in the pipeline:

1. **Verify node exists**: Check against inventory nodes list
2. **Get node details**: `get_node_info` for the node class name
3. **Build the node**: `build_node` with appropriate parameters
4. **Connect nodes**: Ensure output types match input types of the next node

When using `build_node`:
- It returns valid JSON for a single node with correct defaults
- You still need to wire node connections (link output slots to input slots)
- Node IDs must be unique strings (use sequential numbers: "1", "2", "3"...)

### Step 5: Assemble and Validate

1. Combine all node JSONs into a single workflow object (API format)
2. Call `validate_workflow` with the complete JSON
3. If validation fails, read the error and fix:
   - Missing connection: wire the missing link
   - Invalid input: check `get_node_info` for correct types/values
   - Unknown node: check inventory, suggest installation if missing

### Step 6: Present to User

Show the user:
- A summary of the workflow (nodes used, model selected, key parameters)
- Any choices made and why (model selection, resolution, sampler)
- The workflow is ready to run (hand off to `comfyui-generation` or offer to save)

## Workflow JSON Format (ComfyUI API)

Workflows must be in ComfyUI API format (not the UI save format). Structure:

```json
{
  "1": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": {
      "ckpt_name": "model.safetensors"
    }
  },
  "2": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "text": "a photo of a cat",
      "clip": ["1", 1]
    }
  },
  "3": {
    "class_type": "KSampler",
    "inputs": {
      "seed": 0,
      "steps": 20,
      "cfg": 7.0,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1.0,
      "model": ["1", 0],
      "positive": ["2", 0],
      "negative": ["4", 0],
      "latent_image": ["5", 0]
    }
  }
}
```

**Connection format**: `["source_node_id", output_slot_index]`
- Slot indices are 0-based, matching the order from `get_node_info` outputs

## VRAM Estimation

Before building, estimate VRAM requirements:

| Component | Approximate VRAM |
|---|---|
| FLUX FP16 checkpoint | 24GB |
| FLUX FP8/GGUF checkpoint | 12-16GB |
| SDXL checkpoint | 6-8GB |
| SD 1.5 checkpoint | 4-6GB |
| ControlNet model | +1-3GB |
| LoRA | +0.1-0.5GB each |
| Upscale model | +0.5-2GB |
| Generation buffer (1024x1024) | ~2GB |

Compare total against available VRAM from inventory. If tight:
- Suggest FP8/GGUF variants
- Recommend `--lowvram` flag
- Suggest a lighter model alternative

## Common Pitfalls

1. **Wrong model format**: Ensure checkpoint filename exactly matches inventory (including extension)
2. **FLUX needs separate loaders**: FLUX uses UNETLoader + DualCLIPLoader + VAELoader, not CheckpointLoaderSimple
3. **Missing VAE**: Some checkpoints have baked-in VAE, others need external VAE loader
4. **Resolution mismatch**: Using 512x512 with SDXL or 1024x1024 with SD 1.5 produces poor results
5. **ControlNet version mismatch**: SD 1.5 ControlNets don't work with SDXL and vice versa
6. **Empty latent dimensions**: Must be multiples of 8 (ideally 64)

## Saving Workflows

When the user wants to save a workflow:
1. Confirm with user (per authority matrix)
2. Use `save_template` with a descriptive name
3. The workflow is saved as a reusable template accessible via `search_templates`

For local storage, save to `workflows/` directory as `{descriptive-name}.json`.

## Offline Mode

When ComfyUI is not running:

| Step | Online | Offline |
|---|---|---|
| Check templates | `search_templates` | Skip (MCP unavailable) |
| Get node info | `get_node_info` | Use known node schemas from pipeline patterns above |
| Build nodes | `build_node` | Construct JSON manually using patterns in this skill |
| Validate | `validate_workflow` | Skip — warn user workflow is unvalidated |
| Save | `save_template` or local file | Local file only (`workflows/` directory) |

In offline mode, build workflows using the pipeline patterns documented in this skill (Step 3 tables). These patterns are reliable for standard nodes. For custom/unusual nodes, warn the user that validation is deferred until ComfyUI is available.
