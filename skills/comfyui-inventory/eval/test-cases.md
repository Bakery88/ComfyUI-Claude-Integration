# Eval: comfyui-inventory

## Test Cases

### TC-INV-01: Fresh Scan Populates Inventory

**Setup**: Delete `state/inventory.json` if it exists
**Input**: "What models do I have?"
**Expected**:
- Calls `get_status`, `list_models`, `list_nodes` via MCP
- Creates `state/inventory.json` with valid structure
- `timestamp` field is present and within last minute
- `models` object contains categorized arrays (checkpoints, loras, vaes, etc.)
- `nodes` array is non-empty
- Presents a readable summary to the user

**Assertions**:
- [ ] `state/inventory.json` exists after execution
- [ ] JSON has `timestamp`, `models`, `nodes` keys
- [ ] `models.checkpoints` is an array
- [ ] Summary mentions GPU info
- [ ] Summary lists model counts by category

### TC-INV-02: Cache Hit Skips MCP Calls

**Setup**: Ensure `state/inventory.json` exists with timestamp < 1 hour old
**Input**: "What can I do?"
**Expected**:
- Reads cached inventory without calling `list_models` or `list_nodes`
- Still presents a summary to the user

**Assertions**:
- [ ] No `list_models` or `list_nodes` MCP calls made
- [ ] Response still contains model/capability summary

### TC-INV-03: Stale Cache Triggers Refresh

**Setup**: Set `state/inventory.json` timestamp to 2+ hours ago
**Input**: "What models do I have?"
**Expected**:
- Detects stale cache
- Calls `list_models` and `list_nodes` to refresh
- Updates `state/inventory.json` with new timestamp

**Assertions**:
- [ ] MCP scan tools are called
- [ ] `timestamp` in inventory.json is updated to current time

### TC-INV-04: Model Architecture Detection

**Setup**: Inventory contains checkpoints with various naming patterns
**Input**: Internal validation call from another skill
**Expected**:
- FLUX models identified (filenames containing "flux", "FLUX")
- SDXL models identified (filenames containing "sdxl", "xl")
- SD 1.5 models identified (filenames containing "v1-5", "sd15")
- Unknown models flagged rather than guessed

**Assertions**:
- [ ] Architecture labels assigned to known patterns
- [ ] No false architecture assignments

### TC-INV-05: Offline Fallback

**Setup**: ComfyUI not running (`get_status` fails)
**Input**: "What models do I have?"
**Expected**:
- Falls back to last cached `state/inventory.json`
- Warns user that data may be stale
- If no cache exists, tells user ComfyUI must be running

**Assertions**:
- [ ] No crash on connection failure
- [ ] Stale warning displayed if using cache
- [ ] Clear error message if no cache and no connection

### TC-INV-06: Hardware Profile Update

**Setup**: `foundation/hardware-profile.md` has placeholder values (`_detect via get_status_`)
**Input**: First inventory scan after fresh install
**Expected**:
- GPU info from `get_status` written to hardware-profile.md
- Placeholder values replaced with actual data

**Assertions**:
- [ ] hardware-profile.md no longer contains `_detect via get_status_`
- [ ] GPU model, VRAM, and version fields populated
