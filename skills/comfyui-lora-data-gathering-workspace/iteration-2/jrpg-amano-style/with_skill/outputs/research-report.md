# Research Report: Yoshitaka Amano JRPG Art Style

## Overview
Research for collecting Yoshitaka Amano's distinctive watercolor-meets-art-nouveau JRPG illustration style, primarily from Final Fantasy concept art and his independent fine art work.

## Tiered Source Analysis

### Tier A (Primary — high quality, on-style)
- **Amano's official website / gallery** — Original high-res artwork, authoritative source for his style
- **Final Fantasy Wikia / FF art galleries** — Curated concept art from FF I–VI, high relevance
- **Art book scans (The Sky, Dawn, Yoshitaka Amano: The Illustrated Biography)** — Production-quality illustrations

### Tier B (Supplementary — good with filtering)
- **ArtStation** — Fan reproductions and studies of Amano's style, useful for variety
- **Safebooru/Danbooru** — Tagged anime art, search `yoshitaka_amano_(style)`, needs quality filtering
- **Pinterest boards** — Curated collections, mixed resolution

### Tier C (Opportunistic — gap-fillers)
- **YouTube art compilation videos** — "Art of Final Fantasy" videos, frame extraction needed
- **Tumblr art blogs** — Scattered but occasionally high-quality posts
- **Google Image Search** — Last resort for specific gaps

## Key Visual Characteristics
- Flowing, ethereal line work with wispy edges
- Transparent watercolor washes with visible brushwork
- Elongated figure proportions
- Limited, muted palette with occasional vivid accents (gold, crimson)
- Art nouveau influence in decorative framing elements
- Dreamlike, atmospheric backgrounds

## Gap Analysis (Pre-Collection)
- **Potential bias**: Amano's most famous work is character portraits — dataset may skew toward single-figure compositions. Actively seek landscape/environment pieces and group compositions.
- **Color range risk**: Many reproductions are desaturated. Prioritize sources with accurate color reproduction.
- **Medium variety**: Mix standalone illustrations with concept sketches to teach the range of the style.

## Training Alignment
- Base model: FLUX (1024px target)
- Captioning mode: **style** (trigger + "style, " + content description)
- Recommended trigger word: `amanoart` — short, unique, won't collide with existing tokens
- Target: 25-30 images across Tier A and B sources
- Captioner: Florence-2 (best for art/illustration content description)
