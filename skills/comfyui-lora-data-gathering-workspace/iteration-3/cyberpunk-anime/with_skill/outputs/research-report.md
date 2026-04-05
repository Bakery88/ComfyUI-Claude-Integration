# Research Report: Cyberpunk Anime Style LoRA

**Date**: 2026-04-05
**Target Style**: Cyberpunk anime aesthetic (Ghost in the Shell, Akira lineage)
**Base Model**: SDXL
**Target Resolution**: 1024px
**Target Dataset Size**: 25-35 images
**LoRA Type**: Style (learning an aesthetic, not a specific character)

---

## Style Analysis

The "cyberpunk anime" style as defined by Ghost in the Shell (1995, dir. Mamoru Oshii) and Akira (1988, dir. Katsuhiro Otomo) shares these key visual qualities:

### Core Visual Characteristics

1. **Color palette**: Deep blues, neon pinks/magentas, electric teals, warm oranges from explosions/fire, dark shadows with high-contrast neon highlights
2. **Line work**: Detailed, semi-realistic proportions (not chibi/cute), heavy mechanical detail, visible hand-drawn quality in backgrounds
3. **Composition**: Cinematic widescreen framing, dramatic perspective (often low-angle shots of towering cityscapes), dense layered backgrounds
4. **Lighting**: Heavy use of rim lighting, neon glow effects, atmospheric fog/haze with light bleeding through, harsh artificial lighting
5. **Subject matter**: Cybernetic augmentation, dense urban environments, motorcycles/vehicles, military/police hardware, computer interfaces, sprawling megacities
6. **Texture**: Gritty, industrial surfaces, reflective wet streets, metallic sheen on cybernetics, smoke/steam/rain atmospherics
7. **Mood**: Dark, contemplative, technologically oppressive yet visually beautiful

### Key Differences Between the Two References

- **Akira** (Otomo): More explosive action, warmer color tones (reds, oranges), biker gang aesthetic, iconic red motorcycle, 1980s futurism, hand-painted cel backgrounds with extraordinary detail
- **Ghost in the Shell** (Oshii/Shirow): More cerebral/contemplative, cooler color tones (blues, teals), military/espionage aesthetic, cybernetic bodies, water/reflection motifs, 1990s digital-influenced look

The dataset should capture the overlapping aesthetic zone: the cyberpunk anime look both franchises share. We want variety across both warm (Akira-like) and cool (GitS-like) palettes so the LoRA generalizes across the full cyberpunk anime spectrum.

### What the LoRA Should NOT Learn (Exclusion Criteria)

- Specific character faces (Motoko Kusanagi, Kaneda, Tetsuo) -- we want the style, not the characters
- Modern Western "cyberpunk" styles (Cyberpunk 2077 3D rendering -- not anime)
- Clean/sterile sci-fi (Star Trek-like) -- cyberpunk is gritty and lived-in
- Cute/moe anime styles -- this is serious, cinematic anime
- Low-detail or comedic anime art

---

## Research Findings

### Search Strategy

The following search queries were used or would be executed:

1. "Ghost in the Shell official concept art high resolution gallery"
2. "Akira anime official artwork high resolution art book scans"
3. "cyberpunk anime art style reference images collection"
4. "Katsuhiro Otomo artwork gallery high resolution"
5. "Masamune Shirow Ghost in the Shell art"
6. "cyberpunk anime aesthetic artstation"
7. "Ghost in the Shell 1995 background art production Hiromasa Ogura"
8. "Akira production art cel backgrounds Neo-Tokyo"
9. "cyberpunk anime cityscape art neon"
10. "90s anime cyberpunk aesthetic dark sci-fi"
11. "Bubblegum Crisis anime art" (related cyberpunk anime for variety)
12. "Appleseed Masamune Shirow concept art" (same creator as GitS)

### Source Analysis

#### Tier A Sources (Primary -- High Quality, On-Style)

**Source A1: Ghost in the Shell Production Art / Background Paintings**
- Hiromasa Ogura's background paintings for the 1995 film are some of the finest background art in anime history
- Hong Kong-inspired cityscapes, market sequences, waterway/canal scenes, rooftop panoramas, cybernetics lab interiors
- Art-of books ("The Analysis of Ghost in the Shell") contain high-resolution reproductions
- High consistency with target aesthetic; every image is usable
- Estimated usable images: 8-12

**Source A2: Akira Art Book ("Akira Club") / Katsuhiro Otomo Illustrations**
- "Akira Club" art book contains hundreds of illustrations by Otomo
- Production cels and background paintings available in high resolution
- Neo-Tokyo cityscapes (the famous night skyline), motorcycle chase backgrounds, SOL satellite, military facility interiors, Tetsuo mutation sequences (for organic/mechanical hybrid aesthetic)
- Otomo's incredibly detailed linework is core to the style
- Estimated usable images: 8-12

**Source A3: ArtStation -- Professional Cyberpunk Anime Art**
- URL pattern: https://www.artstation.com/search?q=cyberpunk%20anime
- Professional artists creating portfolio-quality work in this genre
- Search terms: "cyberpunk anime", "neo-tokyo", "sci-fi anime cityscape", "Ghost in the Shell fan art"
- Consistently high resolution (artists upload full-res)
- Need to filter for anime-style specifically (many results are 3D or Western-style)
- Estimated usable images: 10-15

#### Tier B Sources (Supplementary -- Good with Filtering)

**Source B1: Danbooru -- Tagged Anime Art Archive**
- URL: https://danbooru.donmai.us/
- Relevant tags: `cyberpunk`, `cityscape`, `neon_lights`, `rain`, `science_fiction`, `dark`, `detailed_background`
- Can combine tags for precision: `cyberpunk cityscape night neon_lights -chibi -cute`
- Large volume; quality varies widely -- need strict filtering
- Many images are fan art; some are excellent quality
- Estimated usable images: 5-8

**Source B2: DeviantArt -- Cyberpunk Anime Category**
- Search: "cyberpunk anime" filtered to Digital Art > Drawings & Paintings
- Fan art and original work in the cyberpunk anime style
- Quality is inconsistent -- filter for professional-level work only
- Estimated usable images: 3-5

**Source B3: Pinterest -- Cyberpunk Anime Mood Boards**
- Curated collections exist for this aesthetic
- Mixed resolution -- many are thumbnails; need to trace back to originals
- Better as a discovery tool to find new Tier A/B sources than as a direct image source
- Estimated usable images: 2-4 (after tracing to full-res)

#### Tier C Sources (Opportunistic -- Fill Gaps Only)

**Source C1: YouTube -- Art Compilations and Art Book Flip-Throughs**
- "Ghost in the Shell production art compilation" -- video slideshows of background art
- "Akira art book flip through" -- shows art book pages at readable resolution
- "Cyberpunk anime aesthetic compilation" -- curated video compilations
- Frame extraction can yield good stills; resolution depends on video quality (720p minimum)
- Estimated usable frames: 5-10

**Source C2: Reddit -- r/Cyberpunk, r/anime, r/ImaginarySliceOfLife, r/ImaginaryCityscapes**
- Community posts sharing cyberpunk anime art
- Hit-or-miss quality, many reposts at reduced resolution
- Useful for finding sources other searches missed
- Estimated usable images: 2-4

**Source C3: Wallpaper Sites (Wallhaven, Alphacoders)**
- URL: https://wallhaven.cc/search?q=cyberpunk+anime
- High-resolution anime wallpapers tagged "cyberpunk"
- Often cropped or AI-upscaled versions, not originals
- Good for filling specific gaps (e.g., need more wide-shot cityscapes)
- Estimated usable images: 3-5

---

## Recommended Acquisition Strategy

For a target of 25-35 images:

1. **Phase 1 -- Tier A** (target: 20-25 images): Ghost in the Shell production art + Akira art book + ArtStation professional work. This should form the backbone of the dataset.
2. **Phase 2 -- Tier B** (if below 25): Danbooru filtered searches + DeviantArt to add variety. Focus on subjects/compositions underrepresented in Tier A.
3. **Phase 3 -- Tier C** (only for gap-filling): YouTube frame extraction for specific missing composition types. Reddit/wallpaper sites for last-resort fills.
4. **Video sources**: Recommended only if static images don't provide enough variety in composition types (e.g., if we lack close-up mechanical detail shots).

## Diversity Goals for This Style

To ensure the LoRA learns "cyberpunk anime style" broadly rather than overfitting:

| Category | Target | Why |
|---|---|---|
| Cityscapes / wide shots | 6-8 images | Core to the aesthetic; dense urban environments |
| Character scenes (medium shot) | 5-7 images | People in cyberpunk settings, cybernetic details |
| Close-up details | 4-5 images | Mechanical parts, neon signs, rain on metal, UI screens |
| Action / dynamic scenes | 3-4 images | Explosions, chases, combat -- the kinetic side of the style |
| Interior environments | 3-4 images | Labs, apartments, bars, control rooms |
| Vehicles / machinery | 2-3 images | Motorcycles, tanks, aircraft, robots |

## Ethical Notes

- Ghost in the Shell artwork is copyrighted by Production I.G / Kodansha / Bandai Visual
- Akira artwork is copyrighted by TMS Entertainment / Kodansha
- ArtStation/DeviantArt artwork belongs to individual artists
- This dataset and resulting LoRA should be for personal/educational use unless the user verifies licensing for each source
- All source URLs will be logged in download-log.json for attribution
- No real people are depicted -- no likeness consent issues
