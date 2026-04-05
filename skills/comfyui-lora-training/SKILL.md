# Skill: ComfyUI LoRA Training

> Guide end-to-end LoRA training for FLUX and SDXL architectures. Covers dataset preparation, training configuration, evaluation, and integration into ComfyUI workflows.

## When to Use

- User asks "Train a LoRA" / "Fine-tune on these images" / "Make a model of [subject]"
- User wants to create a custom style or subject LoRA
- User asks whether to train a LoRA vs. use zero-shot methods (IP-Adapter, InstantID)

## Dependencies

- **comfyui-inventory**: Need to know what base models are available for training and inference

## MCP Tools Used

This skill primarily provides guidance — LoRA training happens **outside ComfyUI** using external tools. MCP tools are used for post-training integration:

| Tool | Purpose |
|---|---|
| `list_models` | Check available base checkpoints and existing LoRAs |
| `build_node` | Build workflow with the trained LoRA |
| `validate_workflow` | Validate LoRA workflow before testing |
| `run_workflow` | Test the trained LoRA with a generation |

## Decision: Train LoRA vs. Zero-Shot

Before starting training, help the user decide if training is actually needed:

```
Does the user need a LoRA?
├── Want to replicate a specific person's face consistently
│   ├── Have 10+ reference images → Train LoRA (best consistency)
│   └── Have 1–3 reference images → Try IP-Adapter FaceID or InstantID first
│
├── Want a specific art style
│   ├── Style is unique/personal → Train LoRA
│   └── Style is well-known → Try prompt engineering first; check if a community LoRA exists
│
├── Want a specific object/product
│   └── Train LoRA (best approach for custom objects)
│
├── Want a concept/theme
│   └── Try prompt engineering first; LoRA only if results are insufficient
│
└── Want general improvement
    └── Don't train — try better prompts, different models, or community LoRAs
```

If zero-shot methods suffice, redirect to `comfyui-face-id` or `comfyui-prompt-engineer` instead.

## Procedure

### Step 1: Choose Architecture and Training Tool

| Architecture | Training Tool | Min VRAM | Notes |
|---|---|---|---|
| FLUX | AI-Toolkit (ostris) | 24GB (FP16) or 9GB (NF4) | Best current quality |
| FLUX | SimpleTuner | 24GB | Alternative, more configurable |
| SDXL | Kohya_ss | 12GB | Mature, well-documented |
| SD 1.5 | Kohya_ss | 8GB | Legacy, still useful for SD 1.5 workflows |

**Recommendation**: Train for the architecture the user will generate with. Check inventory for what checkpoints they have.

### Step 2: Dataset Preparation

#### Image Requirements

| Aspect | Guideline |
|---|---|
| **Count** | 10–30 images (more is better, diminishing returns past 50) |
| **Resolution** | At least 512x512; ideally 1024x1024 for FLUX/SDXL |
| **Variety** | Different angles, lighting, backgrounds, expressions |
| **Quality** | Sharp, well-lit, no watermarks or heavy compression |
| **Subject isolation** | Subject should be clearly the focus; crop if needed |
| **Consistency** | All images should show the same subject/style you're training |

#### Captioning Strategy

Every training image needs a caption. Strategy depends on what you're training:

**For a person/character (trigger word approach)**:
```
[trigger_word], a photo of a person wearing a red jacket, standing outdoors
[trigger_word], close-up portrait, studio lighting, neutral background
```
- Use a unique trigger word (e.g., `ohwx`, `sks`, or a made-up word)
- Describe everything EXCEPT the subject identity (the LoRA learns the identity)

**For a style**:
```
[trigger_word] style, a landscape painting with rolling hills
[trigger_word] style, portrait of a woman, dramatic lighting
```
- Describe the content; the LoRA learns the style

**Captioning tools**:
- **BLIP-2** or **Florence-2**: Automatic captioning (good starting point)
- **WD14 Tagger**: Tag-based captioning (good for anime/illustration)
- **Manual**: Best quality, most time-consuming

### Step 3: Training Configuration

#### FLUX LoRA (AI-Toolkit)

| Parameter | Recommended Value | Notes |
|---|---|---|
| `rank` | 16 | Higher rank = more capacity, more VRAM. 16 is a good default |
| `learning_rate` | 4e-4 | Standard for FLUX LoRA |
| `steps` | 1000–2000 | ~1500 is typical; more for complex subjects |
| `batch_size` | 1 | Increase if VRAM allows (speeds training) |
| `resolution` | 1024 | Match FLUX native resolution |
| `optimizer` | adamw8bit | Memory-efficient; use prodigy for auto-LR |
| `precision` | bf16 or NF4 | NF4 for <12GB VRAM, bf16 for 24GB |
| `gradient_checkpointing` | true | Required for <24GB VRAM |

**NF4 quantized training** (9GB VRAM):
- Enable `quantize_model: true` in config
- Uses 4-bit base model with full-precision LoRA weights
- Slight quality loss vs. FP16 but enables training on consumer GPUs

#### SDXL LoRA (Kohya_ss)

| Parameter | Recommended Value | Notes |
|---|---|---|
| `network_rank` | 32 | SDXL benefits from slightly higher rank |
| `learning_rate` | 1e-4 (unet), 5e-5 (text encoder) | Train text encoder for better prompt response |
| `epochs` | 10 | Monitor for overfitting after epoch 5 |
| `batch_size` | 1–2 | |
| `resolution` | 1024 | Match SDXL native |
| `optimizer` | AdamW8bit or Prodigy | Prodigy auto-tunes LR |
| `noise_offset` | 0.1 | Improves contrast range |
| `mixed_precision` | bf16 | |

### Step 4: Monitor Training

Advise the user to watch for:

**Overfitting indicators**:
- Training loss drops to near zero but validation loss increases
- Generated images look exactly like training images (memorization)
- Model ignores the prompt and always produces the same image
- Details become overly crisp or stylized

**Underfitting indicators**:
- Generated images don't resemble the training subject
- Trigger word has no effect
- High training loss that doesn't decrease

**Checkpointing**: Save checkpoints every 200–500 steps. Test intermediate checkpoints to find the sweet spot before overfitting.

### Step 5: Evaluate the Trained LoRA

Once training completes, test the LoRA in ComfyUI:

1. Copy the LoRA file to ComfyUI's `models/loras/` directory
2. Refresh inventory (`list_models`) to pick up the new LoRA
3. Build a test workflow:

```
CheckpointLoader → LoRALoader → CLIPTextEncode → KSampler → VAEDecode → SaveImage
```

LoRA Loader settings:

| Parameter | Test Value |
|---|---|
| `lora_name` | The trained LoRA filename |
| `strength_model` | 0.7–0.9 (start at 0.8) |
| `strength_clip` | 0.7–0.9 (match model strength) |

4. Generate test images with these prompts:
   - Trigger word only: `[trigger_word]` — does it produce the subject?
   - Trigger word + scene: `[trigger_word], in a forest` — does it respect the prompt?
   - No trigger word: a normal prompt — has it contaminated the base model?
   - Different strengths: try 0.5, 0.7, 0.9, 1.0 — find the sweet spot

### Step 6: Integration into Workflows

Once the LoRA is validated, it can be used in any standard workflow by adding a LoRA Loader node between the checkpoint loader and the rest of the pipeline.

**Recommended usage**:

| Scenario | LoRA Strength |
|---|---|
| Subject generation (person, object) | 0.7–0.9 |
| Style transfer | 0.5–0.8 |
| Subtle style influence | 0.3–0.5 |
| Multiple LoRAs stacked | 0.5–0.7 each (reduce to avoid artifacts) |

**Multiple LoRAs**: Chain LoRA Loader nodes. Each takes the model output of the previous one. Keep total combined strength reasonable (sum of strengths < 1.5 as a rough guideline).

## LoRA Strength Troubleshooting

| Issue | Fix |
|---|---|
| LoRA effect too weak | Increase strength; verify trigger word in prompt |
| LoRA effect too strong / distorted | Decrease strength to 0.5–0.7 |
| LoRA conflicts with another LoRA | Reduce both strengths; try different load order |
| LoRA works but colors are off | May need specific VAE; check training base model's VAE |
| LoRA only works with specific prompts | Training was too narrow; retrain with more varied captions |

## Training Time Estimates

| Setup | FLUX LoRA (1500 steps) | SDXL LoRA (10 epochs, 20 images) |
|---|---|---|
| RTX 4090 (24GB) | ~30–60 min | ~20–40 min |
| RTX 3090 (24GB) | ~45–90 min | ~30–60 min |
| RTX 4070 Ti (12GB, NF4) | ~60–120 min | ~40–80 min |
| Cloud GPU (A100) | ~15–30 min | ~10–20 min |

These are rough estimates. Actual time depends on resolution, batch size, and dataset size.

## Offline Mode

This skill is mostly offline-compatible since training happens outside ComfyUI. The only online-dependent steps are:

| Step | Online | Offline |
|---|---|---|
| Check base models | `list_models` | Use cached inventory |
| Test trained LoRA | `run_workflow` | Save test workflow to `workflows/lora-test-{name}.json` |
| Refresh inventory after training | `list_models` | Remind user to refresh when ComfyUI is running |
