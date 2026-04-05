# Eval: comfyui-generation

## Test Cases

### TC-GEN-01: Basic txt2img Generation

**Setup**: ComfyUI running, SDXL checkpoint available, 8GB+ VRAM
**Input**: "Generate a photo of a sunset over mountains"
**Expected**:
- Checks inventory first
- Selects appropriate model for VRAM
- Crafts prompt using prompt-engineer rules
- Builds valid workflow
- Presents plan to user before executing (authority matrix)
- On confirmation, runs workflow and retrieves image

**Assertions**:
- [ ] Inventory checked before workflow build
- [ ] Model exists in inventory
- [ ] Prompt follows model-specific rules
- [ ] `validate_workflow` called before `run_workflow`
- [ ] User asked for confirmation before execution
- [ ] Image retrieved and presented on success

### TC-GEN-02: Model Selection with VRAM Constraint

**Setup**: 12GB VRAM, FLUX FP16 and SDXL checkpoints available
**Input**: "Generate a photorealistic portrait"
**Expected**:
- Recognizes FLUX FP16 needs 24GB (over budget)
- Selects SDXL or FLUX FP8/GGUF if available
- If tradeoff exists, asks user (per authority matrix)

**Assertions**:
- [ ] Does NOT select FLUX FP16 on 12GB VRAM
- [ ] Selects a model that fits VRAM budget
- [ ] If ambiguous, asks user for preference

### TC-GEN-03: User Confirmation Before Execution

**Input**: "Create an image of a space station"
**Expected**:
- Presents full plan before running:
  - Model name
  - Prompt (or summary)
  - Resolution
  - Key parameters (CFG, steps, sampler)
- Waits for user confirmation
- Does NOT call `run_workflow` without confirmation

**Assertions**:
- [ ] Plan presented with all key details
- [ ] Explicit confirmation requested
- [ ] `run_workflow` only called after confirmation

### TC-GEN-04: Retry on Bad Seed

**Setup**: First generation produces poor quality, user says "try again"
**Input**: "That doesn't look right, try again"
**Expected**:
- First retry: new seed only (autonomous per authority matrix)
- Does NOT change model or significantly alter prompt on first retry

**Assertions**:
- [ ] Seed changed
- [ ] Same model, prompt, and parameters
- [ ] No user confirmation needed for seed retry

### TC-GEN-05: Retry Escalation

**Setup**: Multiple retries with new seeds haven't improved quality
**Input**: "Still not good, the style is wrong"
**Expected**:
- Moves beyond seed retry to prompt refinement
- May suggest parameter adjustment
- If model swap needed, asks user (per authority matrix)

**Assertions**:
- [ ] Retry strategy follows order: seed → prompt → params → model
- [ ] Model swap requires user confirmation
- [ ] Explanation of what changed and why

### TC-GEN-06: Offline Mode Generation

**Setup**: ComfyUI not running (`get_status` fails)
**Input**: "Generate an image of a castle"
**Expected**:
- Detects offline state
- Falls back to cached inventory
- Builds workflow JSON and saves to `workflows/`
- Tells user to import manually when ComfyUI is running

**Assertions**:
- [ ] No crash on connection failure
- [ ] Workflow JSON saved to `workflows/` directory
- [ ] User informed of offline mode and manual import steps

### TC-GEN-07: End-to-End with ControlNet

**Setup**: ControlNet model + matching checkpoint in inventory
**Input**: "Generate an image using ControlNet canny from this reference image"
**Expected**:
- Full 5-step process including ControlNet nodes
- Image loading and preprocessing nodes included
- Architecture match between ControlNet and checkpoint

**Assertions**:
- [ ] ControlNet nodes present in workflow
- [ ] Reference image loading included
- [ ] Architecture consistency validated
- [ ] `validate_workflow` passes

### TC-GEN-08: Ambiguous Request Handling

**Input**: "Make something cool"
**Expected**:
- Asks clarifying questions before proceeding
- Does NOT pick a random subject and generate

**Assertions**:
- [ ] Clarifying questions asked (style? subject? etc.)
- [ ] No workflow built until intent is clear
