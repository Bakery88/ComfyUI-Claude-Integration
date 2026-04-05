# Research Report: Cyberpunk Anime Style LoRA

## Subject Analysis

**What the LoRA should learn**: The visual style of classic cyberpunk anime — specifically the detailed, gritty, neon-drenched aesthetic of Ghost in the Shell (1995) and Akira (1988). Key visual qualities:
- Highly detailed mechanical/cybernetic designs
- Dense urban environments with towering architecture
- Neon lighting against dark, rain-soaked environments
- Hand-painted cel animation look with rich gouache backgrounds
- Contrast between organic human forms and hard-edged technology
- Muted palette punctuated by vivid neon (pink, cyan, orange)
- Atmospheric depth with haze, fog, reflections

**LoRA type**: Style LoRA
**Base model**: SDXL (1024px target — user specified)

## Search Queries Used

1. "cyberpunk anime art style Ghost in the Shell Akira illustration gallery"
2. "Akira anime background art production cel concept art high resolution"
3. "cyberpunk anime aesthetic neon city illustration"

## Sources Found

### Tier 1: Production Art & Archives (highest quality)

| Source | Type | Est. Images | Quality | Notes |
|---|---|---|---|---|
| [akira.ie — Akira Cels & Production Artwork](https://akira.ie/) | Archive | 50+ | Very High | Personal collection of Akira production cels, documented |
| [Riekeles Gallery — Akira Backgrounds](https://www.riekeles.com/) | Gallery | 30+ | Very High | Premium solegraph reproductions of Akira production backgrounds |
| [Halcyon Realms — Akira Animation Archives](https://halcyonrealms.com/animation/revisiting-the-art-of-akira-part-i-akira-animation-archives/) | Article + gallery | 40+ | High | Detailed articles with production art scans |
| [Halcyon Realms — GITS Background Art](https://halcyonrealms.com/anime/ghost-in-the-shell-background-art-cut-no-683/) | Article + gallery | 20+ | High | Individual background art documentation |

### Tier 2: Community Collections

| Source | Type | Est. Images | Quality | Notes |
|---|---|---|---|---|
| [Pinterest — Ghost in the Shell (900+ pins)](https://www.pinterest.com/atsf100/ghost-in-the-shell/) | Curated board | 100+ | Variable | Large collection, needs filtering for production art vs. fan art |
| [Pinterest — Ghost in the Shell ideas](https://www.pinterest.com/ideas/ghost-in-the-shell/959654803881/) | Community | 50+ | Variable | Broader collection including fan interpretations |
| [DeviantArt — Cyberpunk Anime Style](https://www.deviantart.com/tag/cyberpunkanime) | Community | 100+ | Variable | Mix of original and fan art in cyberpunk anime style |

### Tier 3: Exhibition Documentation

| Source | Type | Est. Images | Quality | Notes |
|---|---|---|---|---|
| [Anime Architecture Exhibition](https://www.archipanic.com/anime-architecture/) | Article | 15+ | High | Curated exhibition of 100 technical drawings + watercolours from GITS, Akira, Metropolis |
| [Akira: The Architecture of Neo Tokyo Exhibition](https://www.itsnicethat.com/news/akira-the-architecture-of-neo-tokyo-exhibition-illustration-080622) | Article | 10+ | High | Rare artworks by Akira's art directors |

### Tier 4: Video Sources

| Source | Type | Est. Frames | Notes |
|---|---|---|---|
| YouTube: "Akira art analysis" / "making of Akira" | Video | 30-40 frames | Behind-the-scenes with production art |
| YouTube: "Ghost in the Shell animation analysis" | Video | 20-30 frames | Breakdowns showing background art and key frames |
| YouTube: "cyberpunk anime aesthetic" compilations | Video | 40-50 frames | Curated compilations across multiple shows |

## Additional Cyberpunk Anime References

Beyond GITS and Akira, these sources broaden the style without diluting it:
- **Blade Runner: Black Lotus** — Direct cyberpunk anime, similar aesthetic
- **Psycho-Pass** — Modern take on cyberpunk anime environments
- **Bubblegum Crisis** — Classic 80s cyberpunk anime OVA
- **Ergo Proxy** — Dark, atmospheric cyberpunk

## Ethical Notes

- Production cels and backgrounds are copyrighted by their respective studios (Tokyo Movie Shinsha for Akira, Production I.G for GITS)
- Heritage Auctions and Riekeles Gallery sell originals — high-res scans from these are ideal quality
- Fan art on DeviantArt/Pinterest may be useful for expanding the dataset but introduces style variation

## Recommendation

Start with Halcyon Realms articles (well-documented production art) and the akira.ie collection (dedicated Akira production cels). For GITS, use the Anime Architecture exhibition documentation. Supplement with Pinterest boards after filtering strictly for production art and official illustrations. Target 30-35 images focusing on background art and key animation frames rather than character close-ups, since the urban environments are the strongest style signal. Use WD14 Tagger for captioning since this is anime content.
