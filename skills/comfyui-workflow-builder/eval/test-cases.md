# Eval: comfyui-workflow-builder

## Test Cases

### TC-WF-01: txt2img Workflow — SDXL

**Setup**: Inventory has SDXL checkpoint available
**Input**: "Build a txt2img workflow using SDXL"
**Expected**:
- Workflow contains: CheckpointLoaderSimple, CLIPTextEncode (x2), EmptyLatentImage, KSampler, VAEDecode, SaveImage
- Model filename exactly matches inventory
- Connections are properly wired (output types match input types)
- `validate_workflow` passes

**Assertions**:
- [ ] All required nodes present
- [ ] `ckpt_name` matches a real inventory entry
- [ ] All connections use valid `["node_id", slot_index]` format
- [ ] `validate_workflow` returns success
- [ ] Resolution is 1024x1024 (SDXL native)

### TC-WF-02: txt2img Workflow — FLUX

**Setup**: Inventory has FLUX checkpoint, CLIP models, and VAE
**Input**: "Build a txt2img workflow using FLUX"
**Expected**:
- Uses UNETLoader + DualCLIPLoader + VAELoader (NOT CheckpointLoaderSimple)
- Only positive prompt (no negative for FLUX)
- CFG set to 3.5

**Assertions**:
- [ ] Uses FLUX-specific loader nodes
- [ ] No negative prompt CLIPTextEncode connected to KSampler (or empty)
- [ ] CFG = 3.5
- [ ] `validate_workflow` returns success

### TC-WF-03: Inpainting Workflow

**Setup**: Inventory has inpainting checkpoint
**Input**: "Build an inpainting workflow"
**Expected**:
- Includes LoadImage + LoadImageMask or combined node
- Uses VAE Encode (Inpaint) or equivalent
- Denoise < 1.0

**Assertions**:
- [ ] Image and mask loading nodes present
- [ ] Inpainting-specific encode node used
- [ ] Denoise parameter between 0.3-0.8
- [ ] `validate_workflow` passes

### TC-WF-04: ControlNet Workflow

**Setup**: Inventory has ControlNet model + matching architecture checkpoint
**Input**: "Build a ControlNet canny workflow"
**Expected**:
- txt2img base pipeline plus ControlNet nodes
- ControlNet model matches checkpoint architecture (no SDXL ControlNet with SD 1.5)

**Assertions**:
- [ ] ControlNet loader and apply nodes present
- [ ] Architecture match between ControlNet and checkpoint
- [ ] `validate_workflow` passes

### TC-WF-05: Template Usage

**Input**: "Build a basic txt2img workflow"
**Expected**:
- Checks `search_templates` before building from scratch
- If template found, uses `get_template` with appropriate parameters
- If no template, falls back to manual construction

**Assertions**:
- [ ] `search_templates` called before manual build
- [ ] Template result used if available

### TC-WF-06: Missing Model Rejection

**Setup**: Workflow references a model not in inventory
**Input**: "Build a workflow with NonExistentModel.safetensors"
**Expected**:
- Detects model not in inventory
- Does NOT produce a workflow with the missing model
- Tells user what's missing and how to get it

**Assertions**:
- [ ] No workflow output containing the missing model
- [ ] Clear error message about missing model
- [ ] Suggestion for download or alternative

### TC-WF-07: VRAM Estimation

**Setup**: Inventory shows 8GB VRAM GPU
**Input**: "Build a FLUX FP16 workflow"
**Expected**:
- Estimates VRAM requirement (~24GB)
- Warns that it exceeds available VRAM (8GB)
- Suggests alternatives (FP8, GGUF, or different model)

**Assertions**:
- [ ] VRAM warning displayed
- [ ] Alternative suggestion provided
- [ ] Does not silently build a workflow that will OOM

### TC-WF-08: Valid API Format

**Input**: Any workflow build request
**Expected**:
- Output is valid ComfyUI API format JSON (not UI save format)
- Node IDs are string keys
- Connections use `["source_id", slot_index]` format

**Assertions**:
- [ ] Top-level keys are string node IDs
- [ ] Each node has `class_type` and `inputs`
- [ ] Connection values are `[string, number]` arrays
