# Research Report: Vintage Mechanical Keyboard LoRA Training Data

## Subject Definition

**Target aesthetic**: Vintage mechanical keyboards from the 1980s-1990s era, characterized by:
- Beige/cream ABS plastic cases (sometimes described as "battleship beige")
- Full-size or tenkeyless layouts with thick bezels
- Thick PBT or doubleshot ABS keycaps in colorful profiles (dye-sublimated legends)
- Cherry MX, Alps, or buckling spring switches visible in some shots
- Coiled cables, DIN-5 or PS/2 connectors
- Notable brands: IBM Model M, Apple Extended Keyboard II, Cherry G80 series, Commodore, Amiga, NEC, Tandy, Zenith, Wyse, DEC VT-series terminal keyboards

**Secondary aesthetic elements**: SA/DSA-profile retro keycap sets on modern boards mimicking the vintage look (e.g., GMK Retro, SA Ice Cap, SA Vilebloom), retro desk setups with CRT monitors, beige mice, and period-accurate peripherals.

---

## Source Analysis

### Tier 1: High-Quality Curated Sources (Best for Training)

| Source | Type | Volume Estimate | Quality | Notes |
|--------|------|-----------------|---------|-------|
| r/MechanicalKeyboards (Reddit) | Community photos | Thousands of relevant posts | High (enthusiast photography) | Search by flair "Vintage", "Photos" |
| r/VintageComputing (Reddit) | Community photos | Hundreds of keyboard posts | Medium-High | Broader scope; filter for keyboards |
| Deskthority Wiki (deskthority.net) | Reference photography | 500+ keyboard models documented | Very High (standardized, clean shots) | CC-BY-SA licensed wiki content |
| GeekHack Forums (geekhack.org) | Community photography | Thousands of posts | High | Interest Check and Group Buy threads have renders + photos |
| Flickr "vintage keyboard" groups | Photography | Hundreds of images | High | Check per-image Creative Commons license |

### Tier 2: Product and Reference Sources

| Source | Type | Volume Estimate | Quality | Notes |
|--------|------|-----------------|---------|-------|
| ClickyKeyboards.com | Product/restoration photos | 100+ | Very High, consistent lighting | IBM Model M specialist |
| ThereminGoat / Keyboard University | Review photography | 200+ boards | High, macro detail | Mostly modern but some vintage |
| GMK / keycap designer galleries | 3D renders + photos | Varies | Very High | Retro-themed keycap sets capture the aesthetic |
| eBay "vintage keyboard" listings | Product photos | Thousands | Medium (inconsistent) | Good for variety; noisy backgrounds |
| Etsy vintage keyboard shops | Product photos | Hundreds | Medium-High | Often restored/cleaned units |

### Tier 3: Video Sources (Frame Extraction)

| Source | Type | Est. Relevant Videos | Notes |
|--------|------|----------------------|-------|
| Chyrosran22 (YouTube) | Vintage keyboard reviews | 500+ | Best single video source; detailed close-ups of vintage boards |
| 8-Bit Guy (YouTube) | Retro computing restoration | Dozens | Full restoration walkthroughs, excellent before/after |
| LGR / Lazy Game Reviews (YouTube) | Retro tech reviews | Many | Period-accurate desk setups, great environmental context |
| Rhinofeed (YouTube) | Keyboard reviews | Some vintage content | Clean studio lighting |
| TaeKeyboards (YouTube) | Keyboard reviews | Some vintage | Good visual quality |

---

## Key Observations

### Strengths of This Subject for LoRA Training
1. **Distinctive visual signature**: Beige cases + colorful keycaps create a strong, learnable style
2. **Consistent form factor**: Keyboards are rectangular, predictable in shape -- easier for the model to learn
3. **Rich texture detail**: Keycap legends, surface texture, switch stems, cable coils provide strong signal
4. **Community enthusiasm**: The mechanical keyboard community produces massive amounts of high-quality photography
5. **Clear "trigger word" potential**: "vintage mechanical keyboard" or "retro beige keyboard" are natural, unambiguous trigger phrases

### Challenges
1. **Angle diversity**: Most enthusiast photos are top-down; need side profiles, 3/4 views, close-ups, and environmental shots to avoid the model only learning one perspective
2. **Background variety**: Many photos use plain desk backgrounds; if not varied, the model may overfit to desk surfaces
3. **Modern vs. actual vintage**: Modern boards with retro keycap sets look similar but differ subtly. Include both with careful captioning.
4. **Watermarks/overlays**: Some review sites add watermarks that must be filtered out to avoid training artifacts
5. **Text in images**: Keycap legends contain text; the model needs to learn this is an intrinsic part of the subject, not noise

### Iconic Reference Models (boards to prioritize in the dataset)
- **IBM Model M** (1984-1999): The quintessential beige keyboard. Buckling spring, heavy, industrial.
- **Apple Extended Keyboard II**: Beige/platinum, clean Apple aesthetic, Alps switches.
- **Cherry G80-3000**: Beige case, Cherry MX switches, colorful escape/function key accents.
- **Commodore 64 keyboard**: Integrated into the computer; brown/beige with colorful function keys.
- **DEC VT-220 terminal keyboard**: Beige with unique sculpted profile, split-legend keycaps.
- **Wyse WY-60/85 terminal keyboards**: Heavy beige keyboards with distinctive color-coded modifier keys.
- **NEC APC-III keyboard**: Japanese vintage with interesting layout and colors.

---

## Recommended Dataset Composition

| Category | Percentage | Description |
|----------|-----------|-------------|
| Actual vintage keyboards | 60% | Real 1980s-90s boards: IBM, Cherry, Alps, terminal keyboards |
| Modern retro keycap sets | 20% | GMK Retro, SA Ice Cap, etc. on modern boards |
| Environmental/desk shots | 10% | Keyboards in context with CRTs, beige peripherals, period desks |
| Close-up/detail shots | 10% | Keycap profiles, switch details, cable connectors, texture macro |

### Target Dataset Size
- **Minimum viable**: 30-50 images (works with regularization images)
- **Recommended**: 80-150 images (good balance of variety and training efficiency)
- **Ideal**: 150-300 images (maximum variety without redundancy)

---

## Research Methodology Note

This report was compiled from domain knowledge of the mechanical keyboard community, vintage computing preservation efforts, and established LoRA training practices. Web search was unavailable during this session. Before executing the download pipeline, verify current availability of each listed source.
