# Skill: ComfyUI Prompt Engineer

> Craft effective prompts tailored to the specific model architecture being used.

## When to Use

- User asks "Help me write a prompt" / "Improve this prompt"
- Called by `comfyui-generation` skill during the planning step
- User wants to understand prompting differences between models

## Dependencies

- **comfyui-inventory**: Must know which model will be used (architecture determines prompting rules)
- Read `foundation/model-landscape.md` for model capabilities

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `get_prompting_guide` | Retrieve model-specific prompting best practices (fallback/supplement) |
| `recommend_workflow` | Get recommended settings for a specific model |

## Model-Specific Prompting Rules

### FLUX Family (FLUX.1, FLUX.2)

**Style**: Natural language descriptions
**CFG Scale**: 3.5 (FLUX.1-dev) / 3.5 (FLUX.2-dev)
**Steps**: 20-30 (dev) / 4 (klein/schnell)
**Sampler**: euler
**Scheduler**: normal
**Negative Prompt**: Not used — FLUX ignores negative prompts

**Prompt structure**:
```
[subject description in natural language]. [scene/environment]. [lighting and mood]. [camera/composition]. [style notes].
```

**Example**:
```
A woman with auburn hair sitting at a sunlit café table, reading a leather-bound book.
The café has exposed brick walls and hanging plants. Warm morning light streams through
tall windows, casting soft shadows. Shot from a low angle with shallow depth of field.
Photorealistic, editorial photography style.
```

**FLUX-specific tips**:
- Write prompts like you're describing a photograph to someone
- Be specific about lighting, camera angle, and mood
- Longer, more detailed prompts generally produce better results
- No need for quality tags like "masterpiece" or "best quality"
- Avoid comma-separated tag lists — use full sentences

### SDXL (Stable Diffusion XL)

**Style**: Hybrid — natural language with quality tags
**CFG Scale**: 7-9
**Steps**: 25-35
**Sampler**: dpmpp_2m or euler_ancestral
**Scheduler**: karras
**Negative Prompt**: Important — use it

**Prompt structure**:
```
[quality tags], [subject], [scene details], [lighting], [style], [camera]
```

**Example**:
```
masterpiece, best quality, highly detailed, a woman with auburn hair sitting at a café,
reading a book, exposed brick walls, hanging plants, warm morning sunlight, soft shadows,
low angle shot, shallow depth of field, photorealistic, editorial photography
```

**Negative prompt template**:
```
worst quality, low quality, blurry, deformed, disfigured, bad anatomy, bad hands,
extra fingers, missing fingers, extra limbs, watermark, text, signature
```

**SDXL-specific tips**:
- Quality tags at the start significantly improve output
- Negative prompt is critical for avoiding common artifacts
- Resolution: 1024x1024 (native), or 896x1152 / 1152x896 for portraits/landscapes
- Can mix natural language and tags effectively

### SD 1.5 (Stable Diffusion 1.5)

**Style**: Tag-based (comma-separated keywords)
**CFG Scale**: 7-11
**Steps**: 25-40
**Sampler**: dpmpp_2m or euler_ancestral
**Scheduler**: karras
**Negative Prompt**: Critical

**Prompt structure**:
```
[quality tags], [subject tags], [scene tags], [lighting tags], [style tags]
```

**Example**:
```
masterpiece, best quality, highly detailed, 1girl, auburn hair, sitting, cafe,
reading book, exposed brick, plants, warm lighting, morning sun, soft shadows,
low angle, shallow dof, photorealistic, editorial photo
```

**Negative prompt template**:
```
worst quality, low quality, normal quality, blurry, deformed, ugly, bad anatomy,
bad hands, extra fingers, missing fingers, extra limbs, fused fingers, long neck,
watermark, text, signature, cropped
```

**SD 1.5-specific tips**:
- Heavily tag-based — commas between concepts
- Quality tags matter enormously
- Negative prompt is essential for quality
- Resolution: 512x512 (native), 512x768 / 768x512 for other ratios
- Extensive LoRA ecosystem — prompt may need trigger words for active LoRAs

## Prompt Improvement Procedure

When a user provides a prompt to improve:

### Step 1: Identify Target Model

Check inventory to determine which model will be used. If ambiguous, ask the user.

### Step 2: Analyze Current Prompt

Evaluate the prompt against the model's rules:
- Is it using the right style (natural language vs. tags)?
- Is it missing key elements (lighting, composition, style)?
- Is it too vague or too cluttered?
- Does it have a negative prompt (if the model needs one)?

### Step 3: Enhance

Apply these principles in order:
1. **Specificity**: Replace vague terms with concrete descriptions
   - "a person" → "a middle-aged man with silver-streaked beard"
   - "nice lighting" → "golden hour side-lighting with long shadows"
2. **Composition**: Add camera/framing if missing
   - "portrait" → "close-up portrait, eye-level, 85mm lens, f/1.8"
3. **Atmosphere**: Add mood/environment details
   - Add time of day, weather, ambient elements
4. **Style anchoring**: Reference specific visual styles if appropriate
   - "cinematic", "editorial photography", "oil painting", "concept art"
5. **Model-specific formatting**: Reformat to match model expectations

### Step 4: Present Result

Show the improved prompt with brief notes on what changed and why. Include:
- The enhanced positive prompt
- A negative prompt (if the model uses one)
- Recommended CFG, steps, sampler, scheduler for the model

## Resolution Guidelines

| Aspect Ratio | FLUX | SDXL | SD 1.5 |
|---|---|---|---|
| 1:1 (square) | 1024x1024 | 1024x1024 | 512x512 |
| 3:4 (portrait) | 896x1152 | 896x1152 | 512x680 |
| 4:3 (landscape) | 1152x896 | 1152x896 | 680x512 |
| 16:9 (wide) | 1344x768 | 1344x768 | 680x384 |
| 9:16 (tall) | 768x1344 | 768x1344 | 384x680 |

## LoRA Trigger Words

When LoRAs are active, they often require specific trigger words in the prompt. Check:
1. The LoRA filename often hints at the trigger word
2. Use `get_node_info` on the LoRA loader node if needed
3. Ask the user if uncertain — trigger words are model-specific and not always discoverable

## Fallback

If you're unsure about prompting rules for an unfamiliar model, call `get_prompting_guide` via MCP to get up-to-date guidance. Also check `recommend_workflow` for model-specific parameter recommendations.
