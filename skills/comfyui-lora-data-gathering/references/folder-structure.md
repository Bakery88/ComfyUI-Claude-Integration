# Dataset Folder Structure

Read this file when setting up a new project or when you need to locate a specific pipeline output.

```
datasets/{project-name}/
  raw/                         # Original downloaded images (unmodified)
  video/                       # Downloaded videos (temporary, can delete after extraction)
  processed/                   # Training-ready images + caption .txt files
    001.png
    001.txt
    002.png
    002.txt
    ...
    processing-report.json     # Resolution buckets, before/after sizes (from Step 5)
    caption-report.json        # Captioner used, trigger word, all captions (from Step 6)
  sources.json                 # Approved source list from Step 1
  image-urls.json              # Direct image URLs extracted from sources (Step 2 Phase 1)
  download-log.json            # Source attribution for downloaded images (Step 2)
  extraction-log.json          # Source attribution for video frames (Step 3, if applicable)
  keep.txt                     # Optional: filenames to process (Step 5, if used)
  dataset-report.json          # Final aggregated manifest (Step 7)
```

## Key Files by Step

| Step | Produces | Location |
|---|---|---|
| Step 1: Research | `sources.json` | Project root |
| Step 2: Download | `image-urls.json`, `download-log.json`, image files | Project root, `raw/` |
| Step 3: Video Frames | `extraction-log.json`, frame files | Project root, `raw/` |
| Step 4: Curation | `keep.txt` (optional) | Project root |
| Step 5: Processing | `processing-report.json`, processed images | `processed/` |
| Step 6: Captioning | `caption-report.json`, `.txt` caption files | `processed/` |
| Step 7: Report | `dataset-report.json` | Project root |
