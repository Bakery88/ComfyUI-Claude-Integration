# Sample Captions: Yoshitaka Amano JRPG Watercolor Style

## Caption Configuration

- **Trigger word**: `amanoart`
- **Mode**: `style` (format: `{trigger_word} style, {description of content}`)
- **Captioner**: Florence-2
- **Extra strip words**: `final fantasy, square enix, yoshitaka amano, amano, watercolor, painting, illustration, jrpg, rpg, video game, concept art`

## Caption Hygiene Rules

Captions describe **what is in the image** (subject, composition, colors, setting), NOT **how it was made**. The LoRA learns the "how" from the pixels; the caption teaches it what content to apply the style to.

**Stripped automatically by built-in blocklist**:
- Style terms: "watercolor", "oil painting", "anime style", "digital art", etc.
- Medium descriptors: "painting", "illustration", "drawing", "sketch"
- Quality words: "beautiful", "masterpiece", "high quality", "stunning"

**Stripped by project-specific `--extra-strip-words`**:
- Franchise: "final fantasy", "square enix"
- Artist: "yoshitaka amano", "amano"
- Genre: "jrpg", "rpg", "video game", "concept art"

**Why this matters**: If captions contain "watercolor painting of a knight," the model learns to associate `amanoart` with the text token "watercolor" rather than the actual visual watercolor qualities in the pixels. Stripping these words forces the LoRA to learn the style purely from visual features.

## Example Captions

### Caption 1 — Full-body character portrait (FF VI Terra)

**Image**: A figure with flowing green hair in ornate red and gold armor, standing against a gradient purple-to-blue background. Ethereal wisps of light surround the figure.

**Caption file** (`001.txt`):
```
amanoart style, a woman with long flowing green hair wearing ornate red and gold armor, standing pose, ethereal wisps of light surrounding the figure, gradient purple and blue background
```

**Notes**: No mention of "watercolor", "Final Fantasy", "Terra", or "anime". The character name is omitted because the LoRA should learn the style, not specific characters.

---

### Caption 2 — Group composition (FF IV party)

**Image**: Four figures in elaborate costumes arranged in a triangular composition. A dark-armored knight in the center, flanked by a figure in white robes and a woman with flowing pink hair. Rich blue and gold tones dominate.

**Caption file** (`002.txt`):
```
amanoart style, four figures in elaborate costumes arranged in triangular composition, dark armored knight in center, figure in white robes to the left, woman with flowing pink hair to the right, rich blue and gold color palette, dark atmospheric background
```

**Notes**: Describes composition and visual elements. No character names (Cecil, Rosa, etc.), no franchise references.

---

### Caption 3 — Vampire Hunter D (non-FF subject variety)

**Image**: A tall, slender figure in a wide-brimmed hat and dark flowing cape, mounted on a dark horse. Deep indigo and violet tones with splashes of crimson. A crescent moon in the upper background.

**Caption file** (`003.txt`):
```
amanoart style, a tall slender figure wearing a wide-brimmed hat and flowing dark cape riding a dark horse, deep indigo and violet tones with splashes of crimson, crescent moon in the background, dramatic silhouette composition
```

**Notes**: No mention of "Vampire Hunter D" or the character name. The gothic subject matter adds variety that helps the LoRA generalize beyond a single franchise.

---

### Caption 4 — Close-up detail (face and ornamental detail)

**Image**: A close-up of a face with elongated features, pale skin, and elaborate gold headdress. Fine linework details visible in the jewelry. Soft lavender and cream background wash.

**Caption file** (`004.txt`):
```
amanoart style, close-up of a face with elongated features and pale skin, elaborate gold headdress with intricate details, fine linework in jewelry, soft lavender and cream background
```

**Notes**: Composition variety (close-up vs. the full-body shots above). Describes the visual details without saying "detailed" or "intricate artwork."

---

### Caption 5 — Landscape/environment piece

**Image**: A floating castle among clouds, with spires reaching upward. Warm golden light from the left, cool blue shadows on the right. Organic, flowing architectural forms. Small figures barely visible at the base.

**Caption file** (`005.txt`):
```
amanoart style, a floating castle among clouds with tall spires, warm golden light from the left and cool blue shadows on the right, organic flowing architectural forms, tiny figures at the base of the castle, expansive sky
```

**Notes**: A non-character piece that helps the LoRA learn to apply the style to environments and architecture, not just characters.

---

### Caption 6 — Dynamic action pose (FF I Warrior of Light)

**Image**: A figure in flowing blue and silver armor mid-leap, wielding a long curved sword. Hair and cape streaming behind. Explosive burst of gold and white light at the center. Dark contrasting background.

**Caption file** (`006.txt`):
```
amanoart style, a figure in flowing blue and silver armor leaping through the air wielding a curved sword, hair and cape streaming behind, burst of gold and white light at center, dark contrasting background, dynamic action pose
```

**Notes**: Action composition adds variety. No "Warrior of Light" or "Final Fantasy" references. Describes the motion and energy of the piece.

---

### Caption 7 — Muted/darker color palette piece

**Image**: A solitary cloaked figure standing in a desolate landscape. Muted earth tones -- browns, grays, faded greens. Bare twisted tree branches frame the scene. Overcast sky with subtle warm undertones.

**Caption file** (`007.txt`):
```
amanoart style, a solitary cloaked figure standing in a desolate landscape, muted earth tones with browns grays and faded greens, bare twisted tree branches framing the scene, overcast sky with warm undertones
```

**Notes**: Expands the color palette range of the dataset beyond the typical luminous pastels. Important for preventing the LoRA from only producing bright, jewel-toned outputs.

---

## Caption Quality Checklist

For each caption, verify:

- [x] Starts with `amanoart style, `
- [x] No style-leaking words (watercolor, painting, illustration, anime, etc.)
- [x] No franchise names (Final Fantasy, Square Enix)
- [x] No artist name (Amano, Yoshitaka)
- [x] No character names (Terra, Cecil, Warrior of Light)
- [x] No quality words (beautiful, masterpiece, stunning)
- [x] Describes composition (close-up, full-body, group, landscape)
- [x] Describes colors (specific palette, not generic "colorful")
- [x] Describes key visual elements (armor, hair, background features)
- [x] Consistent format across all captions
