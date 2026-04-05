# Research Report: Cyberpunk Anime Style LoRA Training Data

## Objective

Gather and prepare a training dataset for an SDXL LoRA that captures the visual style of classic cyberpunk anime, specifically inspired by **Ghost in the Shell** (1995 film, Stand Alone Complex series) and **Akira** (1988 film). The goal is a **style LoRA** -- we want the model to learn the overall aesthetic (color grading, line work, atmosphere, compositional language) rather than specific characters.

---

## Style Analysis

### Core Visual Characteristics of the Cyberpunk Anime Aesthetic

These are the defining visual traits shared by Ghost in the Shell and Akira that the LoRA must learn:

1. **Color Palette**: Deep blues, neon pinks/magentas, toxic greens, warm oranges from firelight and explosions. Heavy contrast between dark environments and bright neon signage. Night scenes dominate both works.

2. **Lighting**: Dramatic rim lighting, volumetric light through fog and smoke, neon reflections on wet surfaces, lens flares from artificial light sources. Strong chiaroscuro contrast throughout.

3. **Line Work**: Clean, detailed line art with consistent stroke weight. Mechanical and architectural elements drawn with technical precision. Characters use slightly thicker outlines than background elements, creating depth separation.

4. **Background Detail**: Extremely dense urban environments -- layered cityscapes with visible infrastructure (pipes, cables, ventilation ducts), multilingual signage (Japanese, English, Chinese), towering buildings showing wear and grime. These backgrounds are practically characters themselves.

5. **Mechanical Design**: Highly detailed mecha, cybernetic prosthetics, vehicles, and weapons. Designs feel functional rather than fantastical -- visible joints, hydraulics, panel lines, access hatches.

6. **Atmosphere**: Perpetual urban haze, rain, reflective wet streets, steam from vents. A pervasive sense of technological density mixed with decay and beauty.

7. **Character Rendering**: Relatively realistic proportions (not chibi or exaggerated), detailed facial features, muted skin tones with strong reflected environmental color. Eyes are large but not extremely stylized.

8. **Composition**: Frequent use of extreme wide shots to establish scale of the megacity, intercut with tight close-ups. Dutch angles and unusual perspectives convey disorientation.

### Ghost in the Shell Specifics

- **1995 Film (Mamoru Oshii)**: Painterly, almost watercolor-style backgrounds by Hiromasa Ogura. Subdued, desaturated palette with green/teal tones. Heavy use of water, reflection, and rain imagery. Contemplative pacing reflected in lingering wide shots.
- **Stand Alone Complex (Production I.G.)**: Cleaner digital cel look, more saturated and vivid colors, detailed UI/HUD overlays, holographic displays. Action-oriented compositions.
- **Key design elements**: Tachikoma (rounded, friendly mecha contrasting angular architecture), Section 9 tactical gear, the Major's thermoptic camouflage visual effect.

### Akira Specifics

- **Katsuhiro Otomo's style**: Incredibly detailed hand-drawn backgrounds, 1980s retrofuturism aesthetic. Neo-Tokyo is a sprawling, decaying megacity with construction cranes, elevated highways, Olympic stadium.
- **Iconic visuals**: Motorcycle light-trail sequences (Kaneda's red bike), neon-drenched streets, psychic energy visualizations (organic, disturbing biological forms), military hardware, massive explosions.
- **Technical note**: Akira used an unprecedented 327 colors (vs. typical 150-200) and 160,000+ animation cels. Nearly every frame is exhibition-quality.

### Related Works to Expand the Dataset

Including related titles prevents the LoRA from overfitting to just two sources while staying within the same aesthetic family:

| Title | Studio/Year | Relevance |
|---|---|---|
| **Psycho-Pass** | Production I.G., 2012 | Spiritual successor to GitS; similar city design, UI overlays, surveillance themes |
| **Blame!** (film) | Polygon Pictures, 2017 | Extreme megastructure environments, oppressive dark palette |
| **Ergo Proxy** | Manglobe, 2006 | Dark cyberpunk atmosphere, heavily muted palette, philosophical tone |
| **Bubblegum Crisis** | AIC, 1987-91 | Classic 80s cyberpunk OVA, same era as Akira, similar mechanical design language |
| **Cyber City Oedo 808** | Madhouse, 1990-91 | Peak early-90s cyberpunk anime aesthetic |
| **Armitage III** | AIC, 1995 | Cyberpunk noir on Mars, similar tonal quality to GitS |
| **Texhnolyze** | Madhouse, 2003 | Extremely dark cyberpunk, sparse color palette, industrial decay |
| **Serial Experiments Lain** | Triangle Staff, 1998 | Digital/network cyberpunk aesthetic, unique visual style |
| **Appleseed** (2004, Ex Machina) | Digital Frontier | Masamune Shirow designs (same creator as GitS), mecha-heavy |
| **Blade Runner: Black Lotus** | Crunchyroll/Adult Swim, 2021 | Anime adaptation of Blade Runner aesthetic, directly overlapping visual DNA |

---

## Image Source Analysis

### Source Tier 1: Film/Series Frame Extraction (Primary -- Target 60-70% of Dataset)

**Blu-ray / 4K UHD Sources**
- Ghost in the Shell (1995): Available on 4K UHD Blu-ray with excellent restoration. Native 1920x1080 or 3840x2160.
- Akira (1988): Remastered 4K UHD Blu-ray with frame-by-frame restoration. Exceptional quality.
- Ghost in the Shell: Stand Alone Complex: Blu-ray box sets available at 1080p.
- Method: ffmpeg frame extraction from personal physical media copies.
- Quality: The highest fidelity source -- direct from the master, no recompression.

**Extraction Strategy**
- Extract at 1 frame per 2-5 seconds to avoid near-duplicates
- Target specific scene types: establishing city shots, character medium shots, action sequences, atmospheric shots, UI/technology close-ups
- Discard: motion-blurred frames, pure black/white transition frames, extreme close-ups with no environmental context, frames with heavy subtitle burn-in
- Expected yield: 150-400 usable frames per film, 500-1000 per series season

### Source Tier 2: Official Production Art (Target 15-20% of Dataset)

**Art Books**
- "The Art of Ghost in the Shell" -- background art, character design sheets, color scripts
- "Akira Club" -- Otomo's production artwork, incredibly detailed
- "Akira Animation Archives" -- frame-by-frame breakdowns
- "Ghost in the Shell: SAC Visual Book" -- digital production art

**Key Visuals and Promotional Materials**
- Official movie posters, Blu-ray cover art, theatrical promotional images
- These represent the distilled, most iconic version of each work's style
- Usually available at high resolution from official sources

**Quality Notes**
- Art book scans should be 300+ DPI
- Watch for page curvature distortion near spine -- crop or correct
- Color accuracy may vary between scans; reference the films for true color

### Source Tier 3: Curated Image Board Content (Target 10-15% of Dataset)

**Danbooru / Safebooru**
- Search tags: `ghost_in_the_shell`, `koukaku_kidoutai`, `akira_(manga)`, `cyberpunk`, `neo-tokyo`, `cityscape`, `neon_lights`, `dystopia`
- Critical filters: Add `official_art` or `screencap` tags to stay canonical
- Exclude: `fan_art` unless quality is indistinguishable from source
- Tools: `gallery-dl` for bulk download with tag filtering, `Grabber` (GUI alternative)

**Pixiv**
- Search: "Ghost in the Shell", "AKIRA", "cyberpunk anime" in both English and Japanese
- Filter by bookmark count (>100) as a quality proxy
- Careful curation needed -- many results will be wrong style

### Source Tier 4: Fan Art (Use Very Sparingly -- Max 5-10%)

Only include fan art that is:
- Indistinguishable in quality and style from the source material
- Not introducing incompatible style elements (e.g., chibi, modern moe aesthetic)
- From professional-level artists on ArtStation or Pixiv

---

## Dataset Size Recommendations for SDXL

| Tier | Image Count | Expected Result |
|---|---|---|
| Minimum viable | 30-50 | Basic style transfer, inconsistent application |
| Recommended | 150-250 | Good style capture with flexibility across prompts |
| Optimal | 300-500 | Strong style adherence, handles diverse content well |
| Diminishing returns | 500+ | Marginal improvement, increased overfitting risk |

**Target for this project: 150-250 high-quality, well-captioned images.**

Rationale: Style LoRAs need enough diversity to generalize but not so many images that training becomes unwieldy or the model memorizes specific frames. 150-250 is the sweet spot for SDXL with proper captioning and regularization.

---

## Quality Requirements for SDXL Training

| Attribute | Requirement |
|---|---|
| Minimum resolution | 1024x1024, or 768px on shortest side (will be bucketed) |
| Preferred resolution | 1024x1024+ native, or high-res source downscaled |
| Aspect ratios | Mixed -- 16:9 (screencaps), 1:1, 2:3 (portraits). Training bucketing handles this. |
| File format | PNG preferred (lossless). JPEG at quality 95+ acceptable. |
| Watermarks | None. Exclude or inpaint. |
| Text/subtitles | Must be removed. Crop or use subtitle-free sources. |
| Compression artifacts | No visible blocking or banding. Discard low-quality sources. |
| Duplicate/near-duplicate | Remove. Use perceptual hashing to detect. |

---

## Captioning Strategy Overview

For a **style LoRA**, every caption must include:
1. A consistent **trigger word** (e.g., `cpanime` or `cyberpunk_anime_style`)
2. Description of scene content (what is depicted)
3. Style attributes (lighting, atmosphere, color notes)
4. Composition description (shot type, perspective)

Use natural language captions, not just tag lists. SDXL responds better to descriptive captions.

### Captioning Tool Pipeline
1. **Auto-caption with Florence-2 or CogVLM** -- generates initial natural language descriptions
2. **WD Tagger (SmilingWolf/wd-v1-4-vit-tagger-v2)** -- generates anime-specific booru tags as supplementary metadata
3. **Manual review and enrichment** -- add style-specific details that auto-captioners miss (atmosphere, color grading, reference to the cyberpunk aesthetic)
4. **Prepend trigger word** -- batch-add `cpanime` to every caption

---

## Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| Style dilution from mixed sources | Medium | Strict curation; limit non-canonical sources to <15% |
| Overfitting to specific scenes | Medium | Diverse scene selection; include regularization images |
| Subtitle burn-in from screencaps | Medium | Use subtitle-free video tracks; crop bottom 10-15% of frames |
| Low resolution from older sources | Medium | Prefer remastered/Blu-ray sources; upscale with Real-ESRGAN as last resort |
| Color inconsistency across sources | Low | Visual review pass; normalize obvious outliers |
| Copyright/legal concerns | Variable | Personal copies for personal training use only |
| Near-duplicate frames from video extraction | Low | Perceptual dedup with `fiftyone` or `imagededup` |

---

## Conclusion

The optimal dataset composition:

- **60-70%**: High-quality screencaps from Blu-ray/4K sources of Ghost in the Shell (1995 + SAC) and Akira, supplemented by 2-3 related titles (Psycho-Pass, Bubblegum Crisis, Ergo Proxy)
- **15-20%**: Official production art from art books and promotional materials
- **10-15%**: Carefully filtered image board content using strict canonical tags
- **0-5%**: Professional-grade fan art that matches the source style exactly

This mix provides the canonical style signal while offering enough visual diversity to produce a flexible, non-overfitting LoRA.
