# Skill: ComfyUI Prompt Interview

> Interactive guided discovery for vague or exploratory image generation requests. Walks the user through a conversational flow to produce a complete prompt, parameters, and pipeline recommendation.

## When to Use

- User says "I want to make something but I'm not sure what"
- User gives a very vague request: "make something cool" / "surprise me" / "I want art"
- User is new to image generation and needs guidance
- User has a rough idea but needs help articulating it

**Contrast with `comfyui-prompt-engineer`**: Prompt engineer refines an existing prompt or crafts one from a clear description. Prompt interview discovers what the user wants through conversation.

## Dependencies

- **comfyui-inventory**: Need to know available models to tailor recommendations
- Feeds output into **comfyui-prompt-engineer** for final prompt formatting

## MCP Tools Used

This skill uses no MCP tools directly — it's a conversational skill. Its output feeds into the generation pipeline.

## Procedure

### Step 1: Assess Starting Point

Determine how much the user already knows:

| User says | Starting point | Skip to |
|---|---|---|
| "I have no idea" / "surprise me" | Blank slate | Step 2: Category selection |
| "Something with a cat" | Has a subject | Step 3: Subject refinement |
| "A fantasy landscape" | Has subject + genre | Step 4: Style and mood |
| "Cyberpunk portrait, neon lighting" | Nearly complete | Skip interview → `comfyui-prompt-engineer` |

### Step 2: Category Selection

Ask the user to pick a broad creation type:

```
What kind of image are you thinking about?

1. **Portrait** — a person, character, or face
2. **Scene / Landscape** — an environment, location, or vista
3. **Product / Object** — a specific item, food, vehicle, etc.
4. **Abstract / Artistic** — patterns, textures, surreal, experimental
5. **Concept Art** — characters, environments, or props for a project
6. **Photo Recreation** — something that looks like a real photograph

Or just describe what's on your mind and I'll help shape it.
```

### Step 3: Subject Refinement

Based on the category, ask targeted follow-ups. Ask 2–3 questions max per round — don't overwhelm.

#### Portrait Path
1. "Who is the subject? (real person style, fictional character, fantasy creature, anime character...)"
2. "What's the framing? (close-up headshot, upper body, full body, environmental portrait)"
3. "Any specific features or clothing that matter?"

#### Scene / Landscape Path
1. "What environment? (urban, natural, fantasy, sci-fi, interior, underwater...)"
2. "Time of day and weather? (golden hour sunset, stormy night, misty morning...)"
3. "Should it feel vast/epic or intimate/cozy?"

#### Product / Object Path
1. "What's the item? (food, tech, fashion, vehicle, furniture...)"
2. "What's the context? (studio product shot, in use, flat lay, floating...)"
3. "Any specific material or finish? (matte, glossy, wooden, metallic...)"

#### Abstract / Artistic Path
1. "What feeling should it evoke? (calm, chaotic, dreamy, dark, vibrant...)"
2. "Any visual elements you're drawn to? (fractals, fluid, geometric, organic...)"
3. "Color palette preference? (warm, cool, monochrome, neon, pastel...)"

#### Concept Art Path
1. "For what kind of project? (game, film, book, personal...)"
2. "What's the subject? (character design, environment concept, prop sheet, creature...)"
3. "What's the setting/genre? (fantasy, sci-fi, historical, post-apocalyptic...)"

#### Photo Recreation Path
1. "What kind of photo? (portrait, street photography, nature, macro, aerial...)"
2. "Camera feel? (DSLR shallow depth of field, iPhone casual, film grain vintage, medium format...)"
3. "Lighting? (natural, studio, dramatic, soft, backlit...)"

### Step 4: Style and Mood

Once the subject is clear, refine the aesthetic:

1. "What art style?" — Offer options based on category:
   - Photorealistic, cinematic, anime/manga, oil painting, watercolor, digital art, pixel art, 3D render, comic book, pencil sketch
2. "What mood or atmosphere?" — Examples:
   - Serene, dramatic, mysterious, playful, dark, ethereal, gritty, whimsical, epic, intimate
3. "Any specific color preferences?" — If not covered already

### Step 5: Technical Preferences (optional)

Only ask if relevant or if the user seems technical:

1. "Any aspect ratio preference?" (landscape 16:9, portrait 9:16, square 1:1, cinematic 21:9)
2. "Do you have a preferred model?" (If they know about FLUX, SDXL, etc.)
3. "How important is speed vs. quality?" (Quick draft vs. maximum quality)

If the user doesn't have technical preferences, make autonomous decisions based on the subject and available models.

### Step 6: Synthesize and Present

Compile the interview results into a complete generation plan:

```
## Here's what I've put together:

**Subject**: [assembled subject description]
**Style**: [art style + mood]
**Composition**: [framing, camera angle if relevant]
**Lighting**: [lighting description]
**Color palette**: [color direction]

### Recommended Settings
| Setting | Value | Why |
|---|---|---|
| Model | [name] | [reason based on style + available models] |
| Resolution | [WxH] | [based on aspect ratio choice] |
| CFG | [value] | [based on model] |
| Steps | [value] | [based on quality preference] |

### Prompt (ready for generation)
**Positive**: [full formatted prompt, model-appropriate style]
**Negative**: [negative prompt if applicable to model]

### Pipeline
[txt2img / img2img / etc.] using [architecture]
[Any extras: ControlNet, LoRA, upscaling plan]

Want me to generate this, or would you like to adjust anything first?
```

### Step 7: Hand Off

Based on user response:
- **"Generate it"** → Hand off to `comfyui-generation` with the assembled plan
- **"Change X"** → Adjust the specific element, re-present
- **"Show me variations"** → Generate 2–3 prompt variations with different emphasis
- **"Start over"** → Return to Step 2

## Interview Guidelines

### Do
- Keep questions conversational and friendly
- Offer concrete examples with each question (don't ask open-ended questions without options)
- Limit to 4–7 total questions across the interview
- Summarize what you've gathered between rounds so the user sees progress
- Respect "I don't care" / "you decide" — make autonomous choices and note them

### Don't
- Ask all questions at once (overwhelming)
- Ask more than 3 questions per message
- Use technical jargon without explanation
- Force the user through every step if they're already specific enough
- Second-guess clear user preferences

### Adaptive Depth

Adjust interview depth to the user's engagement:
- **Enthusiastic / detailed responses**: Ask follow-up questions, explore nuance
- **Short / dismissive responses**: Wrap up quickly, fill gaps autonomously
- **"Just make something"**: Pick interesting defaults, generate, iterate from there

## Quick-Start Presets

If the user says "surprise me" or refuses to engage with the interview, use one of these as a starting point:

| Preset | Description | Good For |
|---|---|---|
| **Cinematic Portrait** | Close-up portrait, dramatic lighting, shallow DoF | Showcasing model quality |
| **Fantasy Landscape** | Epic vista, magical atmosphere, golden hour | Visual impact |
| **Cozy Scene** | Warm interior, soft lighting, detailed props | Aesthetic appeal |
| **Sci-Fi Concept** | Futuristic environment, neon lighting, cyberpunk | Technical showcase |
| **Abstract Flow** | Fluid patterns, vibrant colors, ethereal | Artistic exploration |

Pick one matching available models and generate. The user can iterate from there.

## Offline Mode

This skill is fully offline — it's a conversational flow that produces a prompt and settings. The output is handed to other skills (prompt-engineer, generation) which handle online/offline behavior themselves.
