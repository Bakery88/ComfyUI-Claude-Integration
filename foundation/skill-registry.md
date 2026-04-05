# Skill Registry

Dependency graph for all skills. Always check dependencies before invoking a skill.

## Foundation Skills (no dependencies)

| Skill | Path | Purpose |
|---|---|---|
| `comfyui-inventory` | `skills/comfyui-inventory/` | Discover installed models, nodes, and capabilities via MCP tools |

## Core Creation Skills (depend on inventory)

| Skill | Path | Depends On |
|---|---|---|
| `comfyui-prompt-engineer` | `skills/comfyui-prompt-engineer/` | inventory (needs model info for model-specific rules) |
| `comfyui-workflow-builder` | `skills/comfyui-workflow-builder/` | inventory (validates nodes/models exist) |

## Orchestration Skills (depend on creation skills)

| Skill | Path | Depends On |
|---|---|---|
| `comfyui-generation` | `skills/comfyui-generation/` | inventory, prompt-engineer, workflow-builder |

## Specialized Workflow Skills (depend on inventory + workflow-builder)

| Skill | Path | Depends On |
|---|---|---|
| `comfyui-upscale` | `skills/comfyui-upscale/` | inventory, workflow-builder |
| `comfyui-controlnet` | `skills/comfyui-controlnet/` | inventory, workflow-builder |
| `comfyui-face-id` | `skills/comfyui-face-id/` | inventory, workflow-builder, prompt-engineer |
| `comfyui-inpaint` | `skills/comfyui-inpaint/` | inventory, workflow-builder, prompt-engineer |

## Conversational Skills (depend on inventory)

| Skill | Path | Depends On |
|---|---|---|
| `comfyui-prompt-interview` | `skills/comfyui-prompt-interview/` | inventory (feeds output into prompt-engineer) |
| `comfyui-lora-training` | `skills/comfyui-lora-training/` | inventory (guidance skill — training is external) |
| `comfyui-lora-data-gathering` | `skills/comfyui-lora-data-gathering/` | inventory, lora-training (researches and prepares training datasets) |

## Support Skills (independent)

| Skill | Path | Purpose |
|---|---|---|
| `comfyui-troubleshooter` | `skills/comfyui-troubleshooter/` | Diagnose failures, suggest fixes |
| `comfyui-research` | `skills/comfyui-research/` | Monitor ecosystem, update foundation knowledge |

## Dependency Graph

```
comfyui-inventory (foundation — no deps)
    │
    ├── comfyui-prompt-engineer (needs model info)
    ├── comfyui-prompt-interview (feeds into prompt-engineer)
    │
    ├── comfyui-workflow-builder (needs node/model validation)
    │   ├── comfyui-upscale (specialized workflow pattern)
    │   ├── comfyui-controlnet (specialized workflow pattern)
    │   ├── comfyui-face-id (specialized workflow pattern)
    │   └── comfyui-inpaint (specialized workflow pattern)
    │
    ├── comfyui-lora-training (references inventory for model info)
    │   └── comfyui-lora-data-gathering (researches + prepares training datasets)
    │
    └── comfyui-generation (orchestrates all above)

comfyui-troubleshooter (independent — invoked on failure)
comfyui-research (independent — updates foundation files)
```

## Invocation Patterns

- **Before any generation or workflow skill**: Always check `comfyui-inventory` first
- **After any failure**: Route to `comfyui-troubleshooter`
- **Prompt crafting**: `comfyui-prompt-engineer` can be used standalone or called by `comfyui-generation`
- **Workflow building**: `comfyui-workflow-builder` can be used standalone or called by `comfyui-generation`
- **Specialized workflows**: `comfyui-upscale`, `comfyui-controlnet`, `comfyui-face-id`, `comfyui-inpaint` extend workflow-builder with domain-specific patterns
- **Discovery**: `comfyui-prompt-interview` for vague requests; feeds results into prompt-engineer
- **Training**: `comfyui-lora-training` is a guidance skill — training runs outside ComfyUI
- **Data gathering**: `comfyui-lora-data-gathering` researches and collects training datasets; its output feeds into lora-training
- **Knowledge maintenance**: `comfyui-research` runs on-demand to update foundation files
