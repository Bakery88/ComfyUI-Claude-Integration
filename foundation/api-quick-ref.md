# MCP Tool Quick Reference

All tools are provided by `shawnrushefsky/comfyui-mcp` via the MCP server configured in `.mcp.json`.

## Setup & Status

| Tool | Description |
|---|---|
| `get_status` | Connection status, GPU info, installed version |
| `get_install_guide` | Platform-specific ComfyUI installation instructions |
| `get_model_guide` | Guidance on downloading and installing models |
| `get_capabilities` | Detected capabilities of connected ComfyUI instance |

## Discovery

| Tool | Description |
|---|---|
| `list_models` | List all available models (checkpoints, LoRAs, VAEs, etc.) |
| `list_nodes` | List all available ComfyUI nodes |
| `get_node_info` | Detailed info for a specific node (inputs, outputs, examples) |
| `find_nodes_by_type` | Find nodes by input or output type |

## Workflow Composition

| Tool | Description |
|---|---|
| `build_node` | Generate valid node JSON with proper defaults |
| `validate_workflow` | Validate workflow JSON before execution |
| `search_templates` | Find workflow templates (built-in + custom) |
| `get_template` | Build workflow from template with parameters |
| `save_template` | Save workflow as reusable custom template |
| `delete_template` | Delete a custom saved template |

## Examples & Guides

| Tool | Description |
|---|---|
| `list_examples` | List 70+ official ComfyUI example workflows |
| `get_example_workflow` | Fetch an example workflow from official docs |
| `recommend_workflow` | Get recommended workflow and settings for a model |
| `get_prompting_guide` | Prompting best practices per model type |
| `get_download_url` | Get download URL for a model by name |

## Generation & Execution

| Tool | Description |
|---|---|
| `run_workflow` | Execute workflow (API format JSON) — returns task ID |
| `get_image` | Retrieve generated image as base64 |
| `extract_workflow` | Extract workflow JSON from a generated PNG |

## Task & Queue Management

| Tool | Description |
|---|---|
| `get_task` | Check status of an async generation task |
| `get_task_result` | Get result of a completed task |
| `list_tasks` | List all tasks with optional filtering |
| `cancel_task` | Cancel an async task |
| `name_generation` | Assign a descriptive name to a generation |
| `get_generation_by_name` | Retrieve a generation by its assigned name |
| `get_queue` | Current ComfyUI queue status |
| `cancel_job` | Cancel a queued or running job |
| `interrupt` | Interrupt the currently running job |
| `get_history` | Get generation history |

## Agent Memory (MCP-side)

| Tool | Description |
|---|---|
| `save_note` | Save a learning about image generation |
| `get_notes` | Retrieve saved notes (optional topic filter) |
| `search_notes` | Full-text search of saved notes |
| `delete_note` | Delete a note by ID |
| `list_topics` | List all note topics |

## User Preferences

| Tool | Description |
|---|---|
| `get_user_preferences` | Preferences inferred from output history |

## Common Workflows

**Check what's available:**
```
get_status → list_models → list_nodes
```

**Generate an image:**
```
list_models → search_templates / get_template → validate_workflow → run_workflow → get_task → get_image
```

**Build custom workflow:**
```
find_nodes_by_type → get_node_info → build_node (repeat) → validate_workflow → run_workflow
```

**Troubleshoot:**
```
get_status → get_queue → get_history
```
