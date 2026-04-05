# Sample Captions: Cyberpunk Anime Style LoRA

## Captioning Philosophy

These captions follow a style LoRA captioning approach:

1. **Trigger word first**: Every caption starts with `cpanime` so the model associates this token with the style.
2. **Natural language**: SDXL was trained on natural language descriptions, not tag lists. Full sentences work better than comma-separated booru tags.
3. **Content + Style**: Describe both WHAT is shown and HOW it looks (lighting, atmosphere, color, composition).
4. **Consistent vocabulary**: Reuse the same terms for recurring style elements (e.g., always say "neon lighting" not sometimes "neon" and sometimes "fluorescent glow").
5. **30-75 words**: Long enough to be descriptive, short enough to avoid noise.

---

## Example Captions

### Caption 1: City Wide Shot (Ghost in the Shell)

**Image**: Aerial view of a dense cyberpunk city at night, with layered buildings, neon signage, and visible infrastructure.

```
cpanime, a vast cyberpunk cityscape at night seen from above, dense layers of buildings with exposed pipes and cables, neon signs in Japanese and English casting colored light on wet streets below, heavy atmospheric haze between structures, deep blue and magenta color palette, anime style, highly detailed background art, wide shot establishing scale
```

### Caption 2: Character + Environment (Akira)

**Image**: A figure on a red motorcycle speeding down a neon-lit highway with the city skyline behind them.

```
cpanime, a person riding a red motorcycle at high speed down an elevated highway at night, motion-streaked neon light trails in red and white, towering cyberpunk city skyline in the background with construction cranes, dynamic low-angle composition, warm orange and cool blue contrast, anime style, detailed mechanical design on the motorcycle, sense of speed and energy
```

### Caption 3: Technology Close-Up (GitS: SAC)

**Image**: A holographic display interface floating in mid-air in a dark room, with data readouts and wireframe models.

```
cpanime, a holographic computer interface floating in a dark room, translucent blue and green wireframe data displays with Japanese text overlays, multiple layered screens showing surveillance feeds and data analysis, cool blue ambient glow illuminating the scene, anime style, futuristic UI design, cyberpunk technology aesthetic, medium close-up shot
```

### Caption 4: Atmospheric Shot (Ghost in the Shell 1995)

**Image**: Rain falling on a canal in a cyberpunk city, with reflections of neon signs shimmering in the water.

```
cpanime, heavy rain falling on a narrow canal in a cyberpunk city, neon sign reflections rippling in dark water, old concrete walls with exposed utility pipes, a small boat moored at the waterside, warm yellow streetlight mixing with cold blue neon, anime style, painterly background art, moody atmospheric scene, melancholic tone, vertical composition emphasizing depth
```

### Caption 5: Mechanical Design (Akira)

**Image**: A massive military helicopter hovering over a ruined city street, with searchlights cutting through dust.

```
cpanime, a large military helicopter hovering low over a destroyed urban street, bright searchlight beams cutting through clouds of dust and debris, detailed mechanical design with visible panel lines and rotors, crumbling buildings and overturned vehicles below, dramatic lighting from above, anime style, muted earth tones with stark white light, tense atmosphere, wide shot
```

### Caption 6: Interior Environment (GitS: SAC)

**Image**: A dimly lit bar with a cyberpunk aesthetic, screens on the walls, and a lone figure at the counter.

```
cpanime, interior of a dimly lit cyberpunk bar, multiple screens and monitors mounted on walls showing news feeds, a lone figure sitting at a long counter with a drink, warm amber lighting from overhead fixtures contrasting with cool blue screen glow, bottles lined up behind the bar, anime style, detailed interior environment, noir atmosphere, medium wide shot
```

### Caption 7: Action Scene (Ghost in the Shell 1995)

**Image**: A figure in thermoptic camouflage (partially invisible) fighting in a flooded courtyard with water splashing.

```
cpanime, an action scene in a flooded shallow courtyard, water splashing violently as an invisible figure fights, thermoptic camouflage creating a transparent distortion effect against the wet environment, grey overcast sky, concrete pillars and utilitarian architecture, anime style, dynamic composition with strong motion, muted desaturated color palette with emphasis on water reflections
```

### Caption 8: Production Art Style (Art Book Source)

**Image**: A painted background of a cyberpunk street market with vendors and hanging cables.

```
cpanime, a painted background artwork of a cyberpunk street market, crowded narrow alley with vendor stalls and hanging cables overhead, warm incandescent lights mixing with blue neon, multilingual signs in Japanese Chinese and English, steam rising from food stalls, dense urban clutter with visible pipes and ducts, anime style, painterly watercolor-influenced rendering, richly detailed environment art
```

### Caption 9: Mecha/Robot Design (GitS: SAC)

**Image**: A spider-like robot tank in a urban setting, painted blue with a rounded body.

```
cpanime, a small blue spider-like robot tank standing on a city street, rounded compact body with four articulated legs, optical sensors on front, cheerful yet mechanical design contrasting with the gritty urban setting, overcast daylight, detailed mechanical joints and surface panels, anime style, cyberpunk technology, medium shot with slight low angle emphasizing the robot
```

### Caption 10: Psychic/Energy Effect (Akira)

**Image**: A figure surrounded by an expanding sphere of destructive psychic energy, buildings crumbling around them.

```
cpanime, a figure at the center of an expanding sphere of destructive energy, buildings crumbling and fragmenting as the shockwave expands outward, intense white light at the core fading to deep red and orange at the edges, debris floating in mid-air, anime style, dramatic wide shot showing massive scale of destruction, high contrast between bright energy and dark surroundings, apocalyptic atmosphere
```

---

## Caption Formatting Rules

### Do:
- Start every caption with `cpanime`
- Use commas to separate descriptive phrases
- Include at least one mention of "anime style"
- Describe lighting conditions explicitly
- Note the color palette
- Mention composition/shot type (wide shot, close-up, etc.)
- Keep between 30-75 words

### Do Not:
- Use character names (the LoRA is for style, not characters)
- Use booru-style tag formatting (`1girl, blue_hair, ...`)
- Include meta-information ("from the movie Akira", "drawn by Otomo")
- Use quality tags from booru (`masterpiece, best quality`) -- these are for inference, not training
- Write overly short captions (under 20 words) -- they fail to teach style associations
- Include subjective judgments ("beautiful", "amazing") without visual backing

### Trigger Word Usage at Inference Time

When using the trained LoRA, include `cpanime` in the prompt:
```
cpanime, a cyberpunk rooftop garden at night, neon city lights visible in the background, 
anime style, detailed environment, atmospheric lighting
```

Recommended LoRA weight at inference: start at 0.7 and adjust. Higher weight = stronger style effect but more risk of artifacts.
