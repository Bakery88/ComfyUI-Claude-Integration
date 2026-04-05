# Skill: ComfyUI Troubleshooter

> Diagnose failures, identify quality issues, and suggest fixes for ComfyUI workflows.

## When to Use

- User reports an error or failed generation
- A workflow fails during `run_workflow`
- Generated image has quality problems
- ComfyUI is not responding or behaving unexpectedly

## Dependencies

- **comfyui-inventory**: Need current model/node info for diagnostics
- Call `get_status` and `get_queue` for live system state

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `get_status` | Check ComfyUI connectivity, GPU info, version |
| `get_queue` | See current queue state (pending/running jobs) |
| `get_history` | Check recent generation history for patterns |
| `get_task` | Check status of a specific task |
| `cancel_job` | Cancel a stuck job |
| `interrupt` | Interrupt currently running generation |

## Diagnostic Procedure

### Step 1: Gather Context

Run these in parallel:
1. `get_status` — is ComfyUI running? What GPU state?
2. `get_queue` — is anything stuck in the queue?
3. Ask user for the error message if they haven't provided it

### Step 2: Match Error Pattern

Use the decision tree below to identify the issue and apply the fix.

---

## Error Pattern Decision Tree

### Connection Errors

**Symptom**: `get_status` fails, "connection refused", "ECONNREFUSED"

```
Is ComfyUI running?
├── No → Tell user to start ComfyUI
├── Yes, wrong port → Check ComfyUI startup logs for actual port, update .mcp.json
└── Yes, correct port → Check if Docker can reach host.docker.internal
    ├── Docker networking issue → Suggest using host IP instead
    └── Firewall blocking → Suggest checking firewall rules for port 8188
```

### CUDA Out of Memory (OOM)

**Symptom**: "CUDA out of memory", "RuntimeError: CUDA error"

```
CUDA OOM
├── During model loading
│   ├── Model too large for VRAM → Suggest smaller model or quantized variant
│   │   ├── FLUX FP16 on <24GB → Use FP8 or GGUF version
│   │   ├── SDXL on <8GB → Use --lowvram flag or SD 1.5
│   │   └── Multiple models loaded → Restart ComfyUI to clear VRAM
│   └── Other models still in VRAM → Restart ComfyUI (clears GPU memory)
├── During generation
│   ├── Resolution too high → Reduce resolution, generate smaller then upscale
│   ├── Batch size > 1 → Reduce to batch_size 1
│   └── Too many ControlNets → Reduce to 1 ControlNet
└── During upscaling
    └── Image too large → Use tiled upscaling node instead
```

**Quick fixes for OOM**:
1. Restart ComfyUI to clear VRAM
2. Reduce resolution (halve each dimension = 4x less VRAM for latents)
3. Use `--lowvram` or `--cpu-offload` launch flags
4. Switch to quantized model (FP8, GGUF, NF4)

### Missing Node Errors

**Symptom**: "Cannot find node class", "Unknown node type: X"

```
Missing node
├── Custom node not installed → Suggest installing via ComfyUI Manager
├── Node name typo → Check get_node_info for correct class_type name
└── Node deprecated/renamed → Search for replacement with find_nodes_by_type
```

### Missing Model Errors

**Symptom**: "Model file not found", "Cannot load checkpoint"

```
Missing model
├── Wrong filename → Check list_models for exact filename (case-sensitive)
├── Wrong subfolder → Model in wrong directory (e.g., LoRA in checkpoints/)
├── Not downloaded → Suggest download source (get_download_url)
└── Corrupted file → Suggest re-downloading
```

### Workflow Validation Errors

**Symptom**: `validate_workflow` returns errors

```
Validation error
├── Missing required input → Check get_node_info for required fields
├── Type mismatch → Output type doesn't match input type on connection
├── Invalid value → Parameter out of allowed range
├── Circular dependency → Node graph has a loop (restructure connections)
└── Unconnected required input → Wire the missing connection
```

### Generation Hangs

**Symptom**: Task stays in "running" state indefinitely

```
Generation hanging
├── Check get_queue — is it actually running?
│   ├── Queue empty but task shows running → Task tracking desync, check get_history
│   ├── Job running for >5 minutes (simple generation) → May be stuck
│   │   ├── Try interrupt to stop current job
│   │   └── If interrupt fails → Restart ComfyUI
│   └── Many jobs queued → Wait or cancel_job to clear queue
└── get_status shows high GPU usage but no progress
    └── Possible infinite loop in custom node → interrupt + check node configuration
```

---

## Quality Issue Decision Tree

### Blurry or Low-Detail Output

```
Blurry output
├── Too few steps → Increase steps (20-30 for dev models, 25-40 for SD 1.5)
├── CFG too low → Increase CFG (but not above model's sweet spot)
├── Resolution wrong for model
│   ├── SD 1.5 at 1024x1024 → Reduce to 512x512
│   └── SDXL at 512x512 → Increase to 1024x1024
├── VAE issue → Try explicit VAE loader instead of built-in
└── Wrong sampler/scheduler → Try dpmpp_2m + karras (reliable default)
```

### Anatomical Deformities (Bad Hands, Extra Limbs)

```
Anatomy issues
├── Missing negative prompt (SDXL/SD1.5) → Add anatomy-focused negative prompt
├── CFG too high → Reduce CFG (overshoot causes distortion)
├── Model limitation → Suggest better model for human subjects
├── Resolution too low → Increase resolution for more detail budget
└── Inpainting fix → Isolate and regenerate affected area
```

### Color Issues (Washed Out, Oversaturated)

```
Color problems
├── Washed out → CFG may be too low, or VAE issue
├── Oversaturated → CFG too high, reduce by 1-2
├── Wrong VAE → Some models need specific VAE (especially SDXL)
├── Color cast → Check ControlNet preprocessor settings
└── Banding/posterization → Increase bit depth or use different sampler
```

### Artifacts and Noise

```
Artifacts
├── Checkerboard pattern → VAE issue (try different VAE)
├── Grid/seam lines → Tiling issue in upscaler, use seamless mode
├── Random noise patches → Not enough steps or wrong scheduler
├── Watermark-like text → Add "watermark, text" to negative prompt
└── Repeated patterns → Reduce CFG, try different seed
```

### Prompt Not Followed

```
Prompt not followed
├── FLUX with negative prompt → Remove negative prompt (FLUX ignores it, wastes capacity)
├── Prompt too long → Prioritize key elements, reduce complexity
├── Competing concepts → Simplify prompt, generate in stages
├── CFG too low → Model isn't paying attention to prompt, increase CFG
├── Wrong CLIP → Check CLIP model matches architecture
└── LoRA overriding → Reduce LoRA strength (try 0.5-0.7)
```

## Recovery Actions

After identifying the issue, apply fixes in this order:

1. **Parameter adjustment** (fastest): Change CFG, steps, sampler, resolution
2. **Prompt refinement**: Adjust prompt text or negative prompt
3. **Workflow modification**: Add/remove nodes, change connections
4. **Model swap**: Try different checkpoint (requires user confirmation per authority matrix)
5. **System restart**: Restart ComfyUI to clear state (last resort)

## Reporting to User

When reporting a diagnosis:
1. State what went wrong (the error/issue)
2. State the likely cause (from the decision tree)
3. Provide the fix (specific parameter change, command, or workflow edit)
4. If multiple possible causes, list them ranked by likelihood
