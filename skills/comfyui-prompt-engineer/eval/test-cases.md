# Eval: comfyui-prompt-engineer

## Test Cases

### TC-PE-01: FLUX Prompt Formatting

**Setup**: Inventory shows FLUX.1-dev as the active model
**Input**: "Help me write a prompt for a cat sitting on a windowsill"
**Expected**:
- Prompt uses natural language (full sentences, not tags)
- CFG recommended at 3.5
- No negative prompt included
- No quality tags like "masterpiece" or "best quality"

**Assertions**:
- [ ] Prompt contains complete sentences
- [ ] No comma-separated tag lists
- [ ] CFG = 3.5
- [ ] No negative prompt section
- [ ] Steps in range 20-30

### TC-PE-02: SDXL Prompt Formatting

**Setup**: Inventory shows RealVisXL as the active model
**Input**: "Help me write a prompt for a cat sitting on a windowsill"
**Expected**:
- Prompt starts with quality tags
- Includes a negative prompt
- CFG recommended at 7-9

**Assertions**:
- [ ] Prompt begins with quality modifiers (masterpiece, best quality, etc.)
- [ ] Negative prompt provided with anatomy/quality terms
- [ ] CFG in range 7-9
- [ ] Resolution suggested at 1024x1024

### TC-PE-03: SD 1.5 Prompt Formatting

**Setup**: Inventory shows SD 1.5 variant as the active model
**Input**: "Help me write a prompt for a cat sitting on a windowsill"
**Expected**:
- Tag-based format with commas
- Includes negative prompt (critical for SD 1.5)
- CFG recommended at 7-11

**Assertions**:
- [ ] Prompt is comma-separated tags
- [ ] Negative prompt provided and substantial
- [ ] CFG in range 7-11
- [ ] Resolution suggested at 512x512

### TC-PE-04: Prompt Improvement

**Input**: "Improve this prompt: a nice photo of a dog"
**Expected**:
- Identifies vague terms ("nice photo", "a dog")
- Adds specificity (breed, lighting, composition, style)
- Reformats for the target model's style
- Shows before/after with explanation of changes

**Assertions**:
- [ ] Output prompt is more specific than input
- [ ] Explanation mentions what was changed and why
- [ ] Format matches target model architecture

### TC-PE-05: Resolution Recommendation

**Input**: "I want a portrait-oriented image"
**Expected**:
- Recommends correct resolution for the target model:
  - FLUX/SDXL: 896x1152
  - SD 1.5: 512x680

**Assertions**:
- [ ] Resolution matches model architecture
- [ ] Aspect ratio is portrait (height > width)
- [ ] Dimensions are multiples of 8

### TC-PE-06: LoRA Trigger Words

**Setup**: Inventory shows active LoRA with known trigger word
**Input**: "Write a prompt using my [LoRA name]"
**Expected**:
- Mentions that the LoRA may need a trigger word
- Asks user for trigger word if not discoverable
- Includes trigger word in prompt if known

**Assertions**:
- [ ] LoRA trigger word topic addressed
- [ ] Prompt includes trigger word or asks user for it
