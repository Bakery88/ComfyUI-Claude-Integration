# Dataset Plan: Amano JRPG Style LoRA (Baseline)

## Target
- **Subject**: Yoshitaka Amano watercolor JRPG style
- **Base Model**: FLUX.1-dev
- **Target Images**: 200-330 images
- **Resolution**: 1024x1024 minimum

## Image Selection Criteria
- Must show Amano's signature watercolor/ink style
- Prefer complete illustrations over sketches
- Avoid heavily cropped or low-res scans
- Focus on character art and key visual pieces

## Captioning Strategy
- Trigger word: `amano_style`
- Detailed descriptions of content, medium, color palette, composition

## Preprocessing
- Resize to 1024x1024
- Remove watermarks where possible
- Convert to PNG

## Training Parameters
- Learning rate: ~1e-4
- Steps: 1500-3000
- Rank: 16-32
- Optimizer: AdamW8bit

## Quality Validation
- Generate test images at multiple LoRA strengths
- Compare against reference Amano artworks
