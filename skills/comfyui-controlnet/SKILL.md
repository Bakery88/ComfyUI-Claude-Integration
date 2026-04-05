# Skill: ComfyUI ControlNet

> Guide image generation with structural control signals — poses, edges, depth maps, and more. Handles preprocessor selection, multi-ControlNet stacking, and architecture-specific model matching.

## When to Use

- User asks "Use ControlNet" / "Match this pose" / "Follow this outline" / "Keep this composition"
- Called by `comfyui-workflow-builder` when adding control guidance to a workflow
- User provides a reference image and wants structural consistency

## Dependencies

- **comfyui-inventory**: Must verify ControlNet models and preprocessor nodes are available
- **comfyui-workflow-builder**: Uses workflow builder for node construction

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `list_models` | Check available ControlNet models |
| `list_nodes` | Verify preprocessor nodes are installed |
| `get_node_info` | Get inputs/outputs for ControlNet and preprocessor nodes |
| `find_nodes_by_type` | Discover ControlNet-related nodes |
| `build_node` | Construct ControlNet pipeline nodes |
| `validate_workflow` | Validate the complete workflow |

## Procedure

### Step 1: Identify Control Type

Determine what kind of structural guidance the user wants:

| Control Type | Use When | Example Input |
|---|---|---|
| **Canny** | Edge detection — preserve outlines and contours | Photo, sketch, line art |
| **Depth** | Depth map — preserve spatial layout and perspective | Photo with foreground/background |
| **OpenPose** | Pose estimation — match body position | Photo of person in a pose |
| **Lineart** | Clean line extraction — preserve detailed outlines | Illustration, technical drawing |
| **Scribble** | Rough sketch guidance — loose structural control | Hand-drawn sketch |
| **Tile** | Detail preservation at higher resolution | Upscaling with structure preservation |
| **IP-Adapter** | Style/content transfer from reference image | Style reference photo |
| **Inpainting** | Masked region control | Partial image edit |

If unclear, ask the user what aspect of the reference image they want to preserve.

### Step 2: Verify Architecture Compatibility

ControlNet models must match the base model architecture. **This is critical — mismatched versions produce garbage output or errors.**

| Base Model | ControlNet Format | Common Prefix/Pattern |
|---|---|---|
| SD 1.5 | SD 1.5 ControlNet | `control_v11p_sd15_*`, `control_v11f1p_sd15_*` |
| SDXL | SDXL ControlNet | `control-lora-*-sdxl-*`, `diffusers_xl_*`, `sdxl_controlnet_*` |
| FLUX | FLUX ControlNet | `flux_*_controlnet_*`, `FLUX.1-*-controlnet-*` |

Check inventory for matching ControlNet models. If the user has ControlNet models for a different architecture than their chosen checkpoint, warn them and suggest alternatives.

### Step 3: Select Preprocessor

Each control type needs a preprocessor node to extract the control signal from the reference image:

| Control Type | Preprocessor Node | Fallback Preprocessor |
|---|---|---|
| Canny | `CannyEdgePreprocessor` | `Canny` (built-in) |
| Depth | `MiDaS-DepthMapPreprocessor` | `Zoe-DepthMapPreprocessor`, `LeReS-DepthMapPreprocessor` |
| OpenPose | `DWPreprocessor` (DWPose) | `OpenposePreprocessor` |
| Lineart | `LineArtPreprocessor` | `AnimeLineArtPreprocessor` (for anime) |
| Scribble | `ScribblePreprocessor` | `FakeScribblePreprocessor` (from photo) |
| Tile | None (uses image directly) | `TilePreprocessor` for preprocessing |

**Check inventory** for preprocessor nodes. Most require the **ComfyUI ControlNet Auxiliary Preprocessors** package. If missing, suggest installation via ComfyUI Manager.

### Step 4: Build the ControlNet Pipeline

#### Basic ControlNet Pipeline

```
Load Image → Preprocessor → Apply ControlNet → [feeds into KSampler alongside text conditioning]
```

Expanded node flow:

```
[1] LoadImage (reference image)
[2] Preprocessor (e.g., CannyEdgePreprocessor)
[3] ControlNetLoader (load the ControlNet model)
[4] Apply ControlNet (ControlNetApplyAdvanced)
      inputs: positive conditioning, negative conditioning, control_net [3], image [2]
      outputs: positive conditioning, negative conditioning → feed to KSampler
```

The ControlNet output replaces the standard positive/negative conditioning going into the KSampler.

#### Key Parameters

| Parameter | Description | Recommended Range |
|---|---|---|
| `strength` | How strongly the control signal guides generation | 0.3–1.0 (default 1.0) |
| `start_percent` | When to start applying control (0.0 = start) | 0.0–0.3 |
| `end_percent` | When to stop applying control (1.0 = end) | 0.7–1.0 |

**Tuning guidance**:
- **High strength (0.8–1.0)**: Strict adherence to control signal. Good for poses, architecture.
- **Medium strength (0.5–0.7)**: Guided but with creative freedom. Good for general composition.
- **Low strength (0.3–0.5)**: Subtle guidance. Good for mood/atmosphere matching.
- **start_percent > 0**: Lets the model establish composition first, then applies control.
- **end_percent < 1**: Lets the model refine details without control constraint.

#### Preprocessor-Specific Settings

| Preprocessor | Key Parameters |
|---|---|
| Canny | `low_threshold`: 100, `high_threshold`: 200 (adjust for more/fewer edges) |
| MiDaS Depth | `a`: 6.283, `bg_threshold`: 0.1 |
| DWPose | `detect_hand`: true/false, `detect_body`: true, `detect_face`: true/false |
| Lineart | `coarse`: false (true for rougher lines) |

### Step 5: Multi-ControlNet Stacking

To combine multiple control signals (e.g., pose + depth):

```
[1] LoadImage (reference)
[2] Preprocessor A (e.g., DWPose) → control image A
[3] Preprocessor B (e.g., MiDaS Depth) → control image B
[4] ControlNetLoader A (pose model)
[5] ControlNetLoader B (depth model)
[6] Apply ControlNet A: positive, negative, control_net[4], image[2]
[7] Apply ControlNet B: positive_from[6], negative_from[6], control_net[5], image[3]
[8] KSampler: uses conditioning from [7]
```

**Chaining rule**: Each `ControlNetApplyAdvanced` takes the conditioning output of the previous one. The final conditioning goes to the KSampler.

**Recommended combinations**:

| Combination | Use Case | Notes |
|---|---|---|
| Pose + Depth | Character in specific pose and environment | Most common multi-ControlNet setup |
| Canny + Depth | Preserve both edges and spatial layout | Good for architectural scenes |
| Lineart + Color | Colorize a line drawing with color reference | Use Tile ControlNet for color |
| Pose + Face | Character pose with facial detail preservation | Combine with face-id skill for best results |

**VRAM impact**: Each ControlNet adds ~1–3GB VRAM. With 2+ ControlNets, check total against budget.

### Step 6: Validate and Execute

1. Build all nodes using `build_node`
2. Wire connections: preprocessor → ControlNet apply → KSampler conditioning
3. `validate_workflow` to check for errors
4. Present plan to user (per authority matrix)
5. Execute and retrieve result

### Step 7: Assess Results

Common ControlNet issues and fixes:

| Issue | Likely Cause | Fix |
|---|---|---|
| Control signal ignored | Strength too low or wrong ControlNet version | Increase strength; verify architecture match |
| Output looks distorted | Strength too high | Reduce strength to 0.5–0.7 |
| Pose partially followed | DWPose missed joints | Try different preprocessor; adjust detect_hand/face |
| Artifacts at edges | Control signal too harsh | Increase start_percent to 0.1–0.2 |
| Blurry result | ControlNet fighting the prompt | Reduce end_percent to 0.8; lower strength |

## Architecture-Specific Notes

### SD 1.5 ControlNet
- Most mature, widest variety of control types available
- Models are ~1.4GB each
- Preprocessor resolution: 512px recommended

### SDXL ControlNet
- Fewer models available, but growing
- ControlNet-LoRA variants available (smaller file size)
- Preprocessor resolution: 1024px recommended

### FLUX ControlNet
- Newest, still evolving
- Typically uses `XLabs` or `InstantX` FLUX ControlNet models
- May require specific loader nodes (`LoadFluxControlNet` or similar)
- Check inventory for FLUX-specific ControlNet nodes

## Offline Mode

| Step | Online | Offline |
|---|---|---|
| Check ControlNet models | `list_models` | Use cached inventory |
| Verify preprocessor nodes | `list_nodes` | Use cached inventory |
| Build workflow | `build_node` + `validate_workflow` | Build JSON manually, skip validation |
| Execute | `run_workflow` | Save to `workflows/controlnet-{name}.json` |
