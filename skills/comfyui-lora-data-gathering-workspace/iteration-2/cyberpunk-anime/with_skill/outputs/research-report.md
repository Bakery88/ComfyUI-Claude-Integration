# Research Report: Cyberpunk Anime Style

## Overview
Research for collecting cyberpunk anime art in the style of Ghost in the Shell (1995) and Akira (1988) — the hand-painted, atmospheric, neon-drenched aesthetic of late-80s/90s anime sci-fi. Training target is SDXL.

## Tiered Source Analysis

### Tier A (Primary — high quality, on-style)
- **Halcyon Realms (halcyonrealms.com)** — Art book reviews with high-res production art from GITS and Akira
- **Settei Dreams / anime settei archives** — Background art and key animation frames from the original productions
- **Official art books (The Art of Akira, GITS Visual Book)** — Definitive source for the target style

### Tier B (Supplementary — good with filtering)
- **Safebooru/Danbooru** — Tagged anime art archives, search `cyberpunk + cityscape + neon`. Needs filtering for style consistency (many modern digital interpretations don't match the hand-painted target)
- **ArtStation** — Fan art and studies. Filter for hand-painted look, reject 3D renders and modern digital styles
- **DeviantArt** — Cyberpunk anime fan art, varied quality

### Tier C (Opportunistic — gap-fillers)
- **YouTube** — Akira/GITS scene compilations, speed-paint tributes. Frame extraction at key moments.
- **Pinterest boards** — Curated collections, resolution varies
- **Tumblr anime art blogs** — Scattered but occasionally unique finds

## Key Visual Characteristics
- Neon-lit megacity environments with dense vertical architecture
- Hand-painted cel animation look (visible brushwork, not clean digital)
- Dark atmospheric palette with vivid neon accents (cyan, magenta, orange)
- Rain, reflections, fog, atmospheric depth
- Detailed mechanical designs (mecha, motorcycles, cybernetics)
- Cinematic composition with dramatic lighting

## Gap Analysis (Pre-Collection)
- **Potential bias**: Character art vastly outnumbers background/environment art online. Actively seek background art and production paintings.
- **Style drift risk**: Modern "cyberpunk anime" fan art often uses clean digital rendering, not the hand-painted cel look we want. Filter strictly for the 80s-90s aesthetic.
- **Subject diversity**: Need both cityscapes and character scenes, day and night settings, interiors and exteriors.

## Training Alignment
- Base model: SDXL (user specified)
- Captioning mode: **style** (trigger + "style, " + content description)
- Recommended trigger word: `cpanime90s` — unique, references era, won't collide with common tokens
- Target: 25-30 images
- Resolution: 1024px (SDXL native)
- Captioner: WD14 Tagger (anime content) or Florence-2 (for environment/background art)
