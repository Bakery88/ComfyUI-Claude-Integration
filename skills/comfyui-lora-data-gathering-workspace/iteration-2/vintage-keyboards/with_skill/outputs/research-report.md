# Research Report: Vintage Mechanical Keyboards

## Overview
Research for collecting images of vintage mechanical keyboards — the beige-case, colorful-keycap retro aesthetic from the 1980s-90s era (IBM Model M, Apple Extended Keyboard, Cherry G80 series, etc.).

## Tiered Source Analysis

### Tier A (Primary — high quality, on-style)
- **Deskthority Wiki** — Encyclopedic keyboard photography with multiple angles per model, high-res, well-lit
- **r/MechanicalKeyboards gallery posts** — Curated community photos, often professional-quality product shots
- **GeekHack photo threads** — Dedicated vintage keyboard photography threads

### Tier B (Supplementary — good with filtering)
- **eBay/Etsy vintage listings** — Product photos from sellers, varied quality but wide variety of models
- **Keyboard enthusiast blogs** — Review sites with detailed photos (Chyrosran22, Thomas Ran)
- **Flickr vintage computing groups** — Mixed quality, good for unusual angles

### Tier C (Opportunistic — gap-fillers)
- **YouTube keyboard review videos** — Frame extraction from vintage keyboard reviews/restorations
- **Museum of Computing photos** — Occasional high-res archival shots
- **Google Image Search** — Filtered for large images, last resort

## Key Visual Characteristics
- Beige/cream plastic cases (sometimes grey or off-white)
- Colorful keycap sets (PBT dye-sub, doubleshot ABS)
- Chunky, industrial design language
- Coiled cables, large bezels
- Cherry MX, Alps, buckling spring switches visible in some shots
- Period-appropriate desk settings (CRT monitors, floppy disks)

## Gap Analysis (Pre-Collection)
- **Potential bias**: Most community photos feature IBM Model M. Need to include variety: Apple, Cherry, Commodore, Atari keyboards.
- **Angle bias**: Enthusiast photos tend to be top-down. Seek side-profile, detail close-ups, and in-context desk shots.
- **Background variety**: Many product shots use plain backgrounds. Include some in-situ photos with period desk setups.

## Training Alignment
- Base model: FLUX (1024px target)
- Captioning mode: **object** (trigger + ", " + context description)
- Recommended trigger word: `vintage_kb` — short, unique, descriptive
- Target: 25-30 images across Tier A and B sources
- Captioner: Florence-2 (best for product/object description)
