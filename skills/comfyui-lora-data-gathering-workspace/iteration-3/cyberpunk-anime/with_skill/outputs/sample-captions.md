# Sample Captions: Cyberpunk Anime Style LoRA

## Caption Format

Mode: **style**
Trigger word: **cyberpunkanime**
Format: `cyberpunkanime style, {description of content}`

Captions describe **what is in the image** (subjects, composition, colors, setting, actions). They do NOT describe **how it was made** (the LoRA learns that from the pixels).

## Caption Hygiene

### Words stripped by built-in blocklist:
- "watercolor", "oil painting", "anime style", "pixel art", "digital art", "cel-shaded", "3d render"
- "painting", "illustration", "photograph", "drawing", "sketch"
- "beautiful", "masterpiece", "high quality", "stunning", "gorgeous"

### Words stripped by project-specific `--extra-strip-words`:
- "ghost in the shell", "akira" (franchise names)
- "anime style", "cyberpunk" (style/genre labels)
- "neon", "futuristic", "sci-fi", "science fiction", "dystopian" (genre descriptors the LoRA should learn visually)

### Why these words are stripped:
The auto-captioner (WD14) will naturally try to describe images as "cyberpunk anime illustration of a city" or "futuristic sci-fi cityscape". If we leave these in, the model learns: trigger word = "cyberpunk" + "anime" + "sci-fi" text tokens, rather than learning the actual visual features (the specific color palette, line weight, atmospheric effects, etc.). By stripping these, the caption teaches the model what *content* to apply the style to, while the pixels teach it what the style *looks like*.

---

## Example Captions

### 001.txt -- Wide cityscape, night scene
```
cyberpunkanime style, sprawling city skyline at night, towering buildings with glowing windows, elevated highway with light trails from traffic, dark sky with clouds, dense urban environment, wide shot from elevated viewpoint, warm orange and cool blue color contrast
```

### 002.txt -- Character on motorcycle
```
cyberpunkanime style, person riding a red motorcycle on a wet highway, leather jacket, speed lines, rain streaking across the frame, city lights reflected on the road surface, low angle shot from behind, warm red tones against dark background
```

### 003.txt -- Close-up of cybernetic arm
```
cyberpunkanime style, close-up of a mechanical arm with exposed wiring and metal plates, human hand transitioning to metal components, soft blue rim lighting on the edges, dark background, shallow depth of field, detailed mechanical joints and cables
```

### 004.txt -- Rainy market street
```
cyberpunkanime style, narrow street with market stalls and hanging signs with text, crowd of people with umbrellas, rain falling through beams of light, puddles reflecting colored lights, dense atmosphere with steam rising, eye-level perspective looking down the street
```

### 005.txt -- Military helicopter over water
```
cyberpunkanime style, large military helicopter hovering low over a harbor, searchlight beam cutting through fog, dark water below with reflections, industrial port structures in the background, overcast sky, cool blue-grey color palette with single bright searchlight
```

### 006.txt -- Interior of a bar/club
```
cyberpunkanime style, dimly lit interior of a crowded bar, people sitting at counter, bottles on shelves behind the bar, overhead lamps casting warm pools of light, smoke in the air, tight interior composition, warm amber and brown tones with spots of bright color from signs
```

### 007.txt -- Explosion / action scene
```
cyberpunkanime style, massive explosion engulfing a building, debris flying outward, figure in foreground shielding themselves, intense orange and white light from the blast center, dark silhouettes against the fireball, dynamic diagonal composition, smoke billowing upward
```

### 008.txt -- Rooftop overlooking city
```
cyberpunkanime style, lone figure standing on a rooftop edge looking out over a vast city, wind blowing their coat, city lights stretching to the horizon, dark sky above, wide establishing shot, small figure against enormous urban backdrop, cool blue and purple tones
```

---

## What Makes These Captions Good

1. **No style-leaking words**: None of the captions say "anime", "cyberpunk", "futuristic", "sci-fi", "illustration", "digital art", "beautiful", or "masterpiece". The trigger word alone signals the style.

2. **Content-focused**: Each caption describes what you would see -- subjects, spatial relationships, actions, colors, lighting, and composition.

3. **Composition language**: Terms like "wide shot", "low angle", "close-up", "eye-level perspective" help the model learn which compositions pair with which content types.

4. **Color descriptions are concrete**: "warm orange and cool blue" rather than "beautiful neon colors" or "cyberpunk lighting". We describe what we see, not the aesthetic category.

5. **No proper nouns**: No character names (Motoko, Kaneda), no franchise names (Ghost in the Shell, Akira), no artist names. The model should not associate the style with specific text tokens.

6. **Consistent format**: All follow `cyberpunkanime style, {description}` exactly. No variation in trigger word placement or punctuation.

7. **Appropriate detail level**: Long enough to describe the scene meaningfully (15-40 words after trigger), but not so long that they become noisy.

---

## Common WD14 Issues to Watch For

When reviewing auto-generated captions from WD14, watch for these patterns:

| WD14 Output | Problem | Fix |
|---|---|---|
| `cyberpunkanime style, cyberpunk, city, night` | "cyberpunk" leaked through | Should be caught by `--extra-strip-words`; verify it was stripped |
| `cyberpunkanime style, 1girl, blue_hair, bodysuit` | Booru-style tags instead of natural language | WD14 produces tags, not sentences. This is normal and works well for SDXL training. |
| `cyberpunkanime style, no_humans, scenery, city, building` | Terse for a complex scene | Acceptable for WD14 tag format; consider supplementing with spatial/color tags |
| `cyberpunkanime style, masterpiece, best quality, city` | Quality words leaked | Should be caught by built-in blocklist; verify |
| `cyberpunkanime style, science_fiction, mecha, robot` | Genre tag leaked | Should be caught by `--extra-strip-words`; verify |

**Note on WD14 tag format**: WD14 produces comma-separated tags rather than natural language sentences. This is actually fine for SDXL LoRA training -- SDXL was trained on both tag-style and sentence-style captions. The natural language examples above (001-008) show the ideal format for illustration purposes, but actual WD14 output will look more like:

```
cyberpunkanime style, 1girl, short_hair, bodysuit, standing, city, night, rain, wet_ground, from_behind
```

This tag format is valid and effective for SDXL training. Do not convert WD14 tags to natural language unless you have a specific reason to prefer sentences.
