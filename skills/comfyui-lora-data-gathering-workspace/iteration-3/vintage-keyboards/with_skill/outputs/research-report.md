# Research Report: Vintage Mechanical Keyboards LoRA Dataset

**Project**: vintage-keyboards
**Date**: 2026-04-05
**Goal**: Collect 25-35 training images capturing the retro aesthetic of vintage mechanical keyboards -- beige/cream cases, colorful keycaps (dye-sub PBT, doubleshot ABS), chunky bezels, coiled cables, and the distinct 1980s-1990s computing look.

---

## Subject Analysis

The "vintage mechanical keyboard" aesthetic has several defining visual qualities the LoRA needs to learn:

1. **Case color**: Beige, cream, off-white, sometimes yellowed with age
2. **Keycap styles**: Colorful dye-sublimated legends, doubleshot ABS, spherical (SA) or cylindrical (Cherry) profiles, modifier keys in contrasting colors (grey, blue, orange)
3. **Form factors**: Full-size with numpad, oversized bezels, thick cases, sometimes integrated wrist rests
4. **Details**: Coiled cables, DIN or PS/2 connectors, toggle switches, visible screws, brand badges (IBM, Cherry, Alps, NEC, Fujitsu)
5. **Context**: Photographed on desks with retro computing setups, or clean deskmat backgrounds in the modern enthusiast community

### Key Keyboard Families to Cover

- **IBM Model M** (1985+): Buckling spring, beige case, blue/grey IBM logo, industrial aesthetic
- **IBM Model F** (1981+): Earlier, heavier, capacitive buckling spring, darker beige
- **Cherry G80 series**: German-made, Cherry MX switches, colorful dyesub keycaps on beige cases
- **Alps SKCM boards** (Apple Extended Keyboard II, Dell AT101, Focus FK-2001): Various beige case designs with Alps switches
- **NEC/Fujitsu Japanese vintage**: Colorful sublegends, unique layouts, vibrant accent keys
- **Commodore/Amiga keyboards**: Integrated keyboards, very retro aesthetic
- **Modern retro builds**: Reproduction keycap sets (SA Retro, GMK 9009, PBT Classic Retro) on modern boards -- capture the aesthetic with professional photography

---

## Source Discovery

### Search Strategy

Research was conducted across five categories:
1. Enthusiast community galleries (Reddit, Geekhack, Deskthority)
2. Keyboard wiki/museum sites with curated product shots
3. YouTube showcase channels for frame extraction
4. Vendor product photography for modern retro keycap sets
5. Photography communities with artistic keyboard shots

### Tiered Source Analysis

#### Tier A (Primary) -- High-quality, on-target, consistent

**1. Deskthority Wiki -- Keyboard gallery pages**
- URL: https://deskthority.net/wiki/
- Type: gallery
- Est. usable images: 15-20
- Rationale: The premier vintage keyboard reference. Individual wiki pages for IBM Model M, Model F, Cherry G80-3000, Alps boards etc. each contain multiple high-resolution photos with neutral backgrounds, consistent lighting, and multiple angles (top-down, profile, detail shots of keycaps and switches). Images are community-contributed under wiki norms.

**2. r/MechanicalKeyboards -- Vintage flair posts (top/all time)**
- URL: https://www.reddit.com/r/MechanicalKeyboards/ (filtered by "Vintage" flair)
- Type: gallery
- Est. usable images: 20-30
- Rationale: Largest keyboard enthusiast community (1M+ members). Vintage-flaired posts contain high-res photos of restored IBM, Cherry, and Alps boards. Top-of-all-time filtering ensures quality. Many photos show keyboards in styled desk setups that provide contextual variety. Mix of amateur and semi-professional photography.

**3. Geekhack.org -- Vintage keyboard appreciation threads**
- URL: https://geekhack.org/
- Type: gallery
- Est. usable images: 10-15
- Rationale: Older enthusiast forum with dedicated vintage keyboard photo threads dating back to 2008+. Members post detailed multi-angle shots of their collections. Particularly strong for rare boards (Cherry G80 with dyesub caps, Omnikey, Northgate). Images tend to be well-lit and focused on the keyboard itself.

#### Tier B (Supplementary) -- Good variety, needs more filtering

**4. ClickyKeyboards.com (vintage IBM specialist)**
- URL: https://www.clickykeyboards.com/
- Type: gallery
- Est. usable images: 8-12
- Rationale: Specialty vendor that restores and sells vintage IBM keyboards. Product photos show Model M and Model F boards in clean, restored condition with consistent backgrounds. Multiple angles per listing. Some images may be lower resolution.

**5. Modern retro keycap vendor galleries (Drop, NovelKeys, KBDfans)**
- URLs: https://drop.com/, https://novelkeys.com/, https://kbdfans.com/
- Type: gallery
- Est. usable images: 10-15
- Rationale: Professional product photography of retro-themed keycap sets (GMK Retro, SA 9009, NicePBT Retro). Studio lighting, clean compositions. Boards are modern underneath but capture the visual aesthetic perfectly. Excellent for training because of consistent, high-quality photography.

**6. Flickr -- "mechanical keyboard vintage" groups**
- URL: https://www.flickr.com/
- Type: gallery
- Est. usable images: 5-10
- Rationale: Artistic photography with varied creative lighting. Some off-topic results that need filtering. Good for getting unusual angles and moody/atmospheric shots that add diversity.

#### Tier C (Opportunistic) -- Fill gaps, lower hit rate

**7. YouTube: Chyrosran22 and TaeKeyboards vintage reviews**
- URLs: https://www.youtube.com/@Chyrosran22, https://www.youtube.com/@TaeKeyboards
- Type: video
- Est. usable frames: 8-15
- Rationale: Chyrosran22 has reviewed hundreds of vintage keyboards with detailed close-ups of keycaps, switches, and case details. TaeKeyboards does similar showcases. Frame extraction can yield good detail shots and angles not commonly found in static photos. Video quality is 1080p+.

**8. eBay / Yahoo Auctions Japan -- vintage keyboard listings**
- URL: https://www.ebay.com/, https://auctions.yahoo.co.jp/
- Type: gallery
- Est. usable images: 5-8
- Rationale: Sometimes the only source for rarer Japanese vintage boards (NEC PC-8801, Fujitsu FKB4700). Varied quality. Some seller watermarks possible -- flag during curation.

**9. Pinterest -- "vintage mechanical keyboard" boards**
- URL: https://www.pinterest.com/
- Type: gallery
- Est. usable images: 5-10
- Rationale: Curated aesthetic boards. Mixed resolution. Many are reposts from Reddit/Geekhack (dedup will catch). Useful for discovering sources not found through direct search.

---

## Ethical Considerations

- All sources are publicly accessible galleries, community forums, or commercial product pages
- Reddit and Geekhack images are user-submitted to public forums -- attribution logged in download-log.json
- Vendor product photos are marketing material intended for public viewing
- No personal/private photos of individuals identified
- eBay listings may carry seller watermarks -- flagged for curation review
- This is a non-commercial personal LoRA project; if the user plans distribution, source licenses should be reviewed

---

## Estimated Dataset Composition

| Source Tier | Est. Images | Role |
|---|---|---|
| Tier A (Deskthority, Reddit, Geekhack) | 15-20 | Backbone -- consistent quality, authentic vintage boards |
| Tier B (ClickyKB, vendors, Flickr) | 8-12 | Variety -- professional photography, different lighting |
| Tier C images (eBay, Pinterest) | 3-5 | Gap fill -- rare boards, unusual angles |
| Tier C video frames (YouTube) | 5-10 | Supplementary -- close-up details, switch/keycap shots |
| **Total before curation** | **31-47** | |
| **Target after curation** | **25-30** | |

---

## Recommendations

1. **Base model**: SDXL or FLUX recommended -- keycap legends and switch housing detail benefits from 1024px resolution
2. **Trigger word suggestion**: `retrokb` (short, unique, memorable)
3. **Captioning mode**: `object` -- the LoRA learns to generate vintage keyboards as objects; captions describe context and setting
4. **Priority diversity needs**: Multiple angles (top-down, profile, 3/4, close-up), varied lighting (natural, studio, warm desk lamp), varied contexts (bare desk, retro setup with CRT, modern deskmat)
5. **Watch for**: Over-representation of IBM Model M (most commonly photographed vintage board) -- ensure Cherry, Alps, and Japanese boards are represented too
