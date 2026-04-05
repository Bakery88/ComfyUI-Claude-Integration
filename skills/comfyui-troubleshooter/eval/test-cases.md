# Eval: comfyui-troubleshooter

## Test Cases

### TC-TS-01: CUDA OOM Diagnosis

**Input**: "I got this error: CUDA out of memory. Tried to allocate 2.00 GiB"
**Expected**:
- Identifies as CUDA OOM error
- Calls `get_status` for GPU/VRAM info
- Suggests concrete fixes: reduce resolution, use quantized model, restart ComfyUI, --lowvram flag
- Ordered from easiest to most disruptive

**Assertions**:
- [ ] Correctly identifies OOM pattern
- [ ] Diagnostic tools called (get_status)
- [ ] At least 3 specific fixes suggested
- [ ] Fixes ordered by effort/disruption

### TC-TS-02: Missing Node Diagnosis

**Input**: "Error: Cannot find node class 'CustomNodeXYZ'"
**Expected**:
- Identifies as missing node error
- Extracts node name "CustomNodeXYZ"
- Suggests installing via ComfyUI Manager
- May search for similar nodes with `find_nodes_by_type`

**Assertions**:
- [ ] Node name extracted from error
- [ ] Installation guidance provided
- [ ] ComfyUI Manager mentioned

### TC-TS-03: Missing Model Diagnosis

**Input**: "Error: Model file not found: flux1-dev.safetensors"
**Expected**:
- Identifies as missing model error
- Checks inventory for close matches (fuzzy match)
- If typo, suggests correct filename
- If truly missing, suggests where to download

**Assertions**:
- [ ] Model name extracted from error
- [ ] Inventory checked for near-matches
- [ ] Download suggestion if model not found

### TC-TS-04: Connection Failure

**Setup**: ComfyUI not running
**Input**: "I can't connect to ComfyUI"
**Expected**:
- Verifies with `get_status`
- Checks common causes: not running, wrong port, Docker networking
- Provides step-by-step troubleshooting

**Assertions**:
- [ ] `get_status` called
- [ ] Multiple possible causes listed
- [ ] Actionable steps for each cause

### TC-TS-05: Quality Issue — Blurry Output

**Input**: "My generated image is blurry and lacks detail"
**Expected**:
- Asks about or checks: model used, resolution, steps, CFG, sampler
- Suggests: increase steps, check resolution matches model, try different sampler
- Does NOT immediately suggest model swap (per retry strategy order)

**Assertions**:
- [ ] Parameter-level fixes suggested first
- [ ] Resolution/model mismatch checked
- [ ] Model swap NOT the first suggestion

### TC-TS-06: Quality Issue — Bad Anatomy

**Input**: "The hands look deformed"
**Expected**:
- If SDXL/SD1.5: check negative prompt (anatomy terms)
- Check if CFG is too high (overshoot)
- Suggest inpainting fix for isolated area
- Suggest higher resolution for more detail budget

**Assertions**:
- [ ] Negative prompt check (if applicable model)
- [ ] CFG adjustment suggested
- [ ] Inpainting mentioned as a targeted fix

### TC-TS-07: Generation Hang

**Input**: "My generation has been running for 10 minutes with no progress"
**Expected**:
- Calls `get_queue` to check queue state
- Calls `get_task` if task ID available
- Suggests `interrupt` if stuck
- Suggests restart as last resort

**Assertions**:
- [ ] `get_queue` called for diagnostics
- [ ] `interrupt` suggested before restart
- [ ] Escalation order: interrupt → cancel → restart

### TC-TS-08: Prompt Not Followed

**Input**: "The image doesn't match my prompt at all"
**Expected**:
- Checks model-specific issues (FLUX with negative prompt, CFG too low)
- Checks prompt length and complexity
- Suggests prompt refinement before model swap

**Assertions**:
- [ ] Model-specific prompt issues checked
- [ ] CFG adjustment suggested
- [ ] Prompt refinement suggested before model change
