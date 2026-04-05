# Sample Captions: Vintage Mechanical Keyboards

## Caption Configuration

- **Trigger word**: `retrokb`
- **Mode**: `object` -- format is `{trigger_word}, {description of context and setting}`
- **Captioner**: Florence-2
- **Extra strip words**: `mechanical keyboard, keyboard, retro, vintage, computer keyboard, typing, keys`

## Caption Hygiene Rules Applied

The following words are automatically stripped from all captions:

**Built-in blocklist** (from auto_caption.py):
- Style terms: "watercolor", "oil painting", "anime style", "pixel art", "digital art", "cel-shaded", "3d render"
- Medium descriptors: "painting", "illustration", "photograph", "drawing", "sketch"
- Quality words: "beautiful", "masterpiece", "high quality", "stunning", "gorgeous"

**Project-specific strip words** (via `--extra-strip-words`):
- "mechanical keyboard", "keyboard", "retro", "vintage", "computer keyboard", "typing", "keys"

These are stripped because the LoRA should learn the visual concept of "vintage keyboard" from the pixels, not from text tokens in the captions. If "vintage keyboard" appeared in every caption, the model would associate the trigger word with those text tokens rather than learning the actual visual features (beige cases, colorful keycaps, chunky bezels).

## Example Captions

### 001.txt -- IBM Model M on neutral background (Deskthority wiki)

```
retrokb, beige device with grey and white keycaps on a plain white surface, overhead view showing full layout with number pad, blue oval logo badge on upper right
```

### 002.txt -- Cherry G80-3000 with colorful dyesub caps (Deskthority wiki)

```
retrokb, cream colored device with multicolored legends on white and grey keycaps, green and orange accent markings on modifier keys, sitting on a grey desk surface, front-facing three quarter angle view
```

### 003.txt -- IBM Model F XT on wooden desk (Reddit post)

```
retrokb, heavy beige device with dark grey keycaps on a warm wooden desk, angled side profile view showing thick case and stepped key rows, soft natural window lighting from the left
```

### 004.txt -- Apple Extended Keyboard II (Deskthority wiki)

```
retrokb, off-white device with matching keycaps and a clean minimalist design, small rainbow logo on upper left, photographed from above at slight angle on a light grey background
```

### 005.txt -- Modern retro build with SA keycaps (Reddit post)

```
retrokb, cream colored device with tall sculpted keycaps in beige and blue tones, coiled cable extending to the right, on a dark green deskmat with a potted plant in the soft background
```

### 006.txt -- Video frame close-up of Model M keycaps (Chyrosran22)

```
retrokb, extreme close-up of white and grey keycaps with black printed legends, shallow depth of field with blurred beige case in background, warm indoor lighting
```

### 007.txt -- Cherry G80 with blue modifiers on desk setup (Geekhack)

```
retrokb, beige device with white keycaps and blue modifier keys, next to a beige CRT monitor and matching mouse on a grey office desk, overhead three quarter view under fluorescent lighting
```

### 008.txt -- NEC PC-8801 keyboard (eBay listing)

```
retrokb, light grey device with multicolored function key row in red yellow and green, Japanese and English keycap legends, white background, top-down view showing compact layout with distinctive spacebar design
```

## What Makes These Captions Effective

1. **No style-leaking words**: None of the captions say "vintage", "retro", "classic", "old", "nostalgic", or "mechanical keyboard" -- those concepts are what the LoRA learns from pixels
2. **Object mode format**: Each starts with `retrokb,` followed by a description of the context, setting, and visual attributes -- NOT what the object "is"
3. **Descriptive of visual features**: Colors (beige, cream, grey, blue), materials implied by appearance, spatial relationships
4. **Composition details included**: Camera angle (overhead, three-quarter, profile, close-up), lighting quality (natural, warm, fluorescent), depth of field
5. **Context when present**: Desk surface, nearby objects (CRT monitor, mouse, deskmat, plant), background
6. **Neutral language**: Avoids subjective quality judgments ("beautiful", "stunning", "perfect") that would pollute the training signal
7. **Consistent format**: All follow the same `retrokb, {description}` pattern for training stability
