# Eval Framework

## Purpose

Structured test cases for validating that each skill produces correct, safe, and useful outputs. These are **manual evaluation checklists** designed for a human or AI reviewer — not automated test scripts.

## Structure

Each skill has an `eval/test-cases.md` file:

```
skills/
├── comfyui-inventory/eval/test-cases.md       (6 test cases)
├── comfyui-prompt-engineer/eval/test-cases.md  (6 test cases)
├── comfyui-workflow-builder/eval/test-cases.md (8 test cases)
├── comfyui-troubleshooter/eval/test-cases.md   (8 test cases)
└── comfyui-generation/eval/test-cases.md       (8 test cases)
```

**Total: 36 test cases** across 5 skills.

## Test Case Format

Each test case follows this structure:

| Field | Description |
|---|---|
| **ID** | `TC-{SKILL}-{NUMBER}` (e.g., TC-INV-01, TC-GEN-05) |
| **Setup** | Preconditions (inventory state, ComfyUI status, available models) |
| **Input** | What the user says or what triggers the test |
| **Expected** | What the skill should do (behavior, not exact output) |
| **Assertions** | Checkbox list of verifiable outcomes |

## How to Run an Eval

### Single Skill Eval

1. Read the skill's `eval/test-cases.md`
2. For each test case:
   a. Set up the preconditions (setup field)
   b. Provide the input to Claude with this project's CLAUDE.md active
   c. Check each assertion in the checklist
   d. Note any failures with the specific assertion that failed

### Cross-Skill Eval

The generation skill (TC-GEN-*) tests the full pipeline across all skills. Running TC-GEN-01 through TC-GEN-08 exercises:
- Inventory validation (inventory skill)
- Prompt crafting (prompt-engineer skill)
- Workflow construction (workflow-builder skill)
- Error handling (troubleshooter skill)

### Baseline Comparison

To measure skill effectiveness:

1. **With skills**: Run a generation request with CLAUDE.md and all skills active
2. **Without skills**: Run the same request with only `.mcp.json` (no CLAUDE.md, no skills)
3. **Compare**:
   - Did the with-skills version check inventory first?
   - Was the prompt formatted correctly for the model?
   - Was VRAM considered in model selection?
   - Was the workflow validated before execution?
   - Were errors handled with specific guidance?

## Key Invariants to Test

These should hold across ALL test cases:

1. **Inventory First**: No workflow is built without checking inventory
2. **Authority Matrix**: `run_workflow`, `save_template`, `delete_template` always require user confirmation
3. **Model Validation**: Every model referenced in a workflow exists in inventory
4. **Node Validation**: Every node class in a workflow exists in inventory
5. **Architecture Consistency**: ControlNet/LoRA models match the checkpoint architecture
6. **VRAM Awareness**: Model selection respects available VRAM
7. **Offline Graceful Degradation**: Connection failures don't crash — fall back to cached data or inform user

## Tracking Results

Use this format to log eval results:

```
## Eval Run: [DATE]

### TC-INV-01: Fresh Scan Populates Inventory
- [x] state/inventory.json exists after execution
- [x] JSON has timestamp, models, nodes keys
- [ ] FAIL: models.checkpoints was missing (bug: list_models returned flat list)
- [x] Summary mentions GPU info
- [x] Summary lists model counts by category

**Result**: PARTIAL PASS — 4/5 assertions
**Notes**: Need to handle flat model list from list_models
```
