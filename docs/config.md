# `config.py` — Configuration reference

Purpose
- `config.py` centralizes runtime settings (paths, OCR/extraction parameters, logging and output columns) so `main.py` and the extraction modules can be configured without changing code.

Primary variables (what to check before running)
- `BASE_DIR` — project root (auto-calculated).
- `DATA_DIR` — `BASE_DIR / "data"`.
- `INPUT_DIR` — default input folder (data/input).
- `OUTPUT_DIR` — default output folder (data/output).
- `DEBUG_DIR` — debug images and log folder (data/debug).

I/O paths
- `INPUT_FOLDER` — folder scanned for PDF files (default: `INPUT_DIR`).
- `CSV_OUTPUT_PATH` / `EXCEL_OUTPUT_PATH` — default filenames in `OUTPUT_DIR` used when fixed output names are needed.

OCR & converter settings
- `TESSERACT_CMD` — full path to the `tesseract` executable. On Linux set to `/usr/bin/tesseract` (or simply `tesseract` if in PATH). On Windows set the full Program Files path.
- `POPPLER_PATH` — folder path pointing to Poppler binaries (used by `pdf2image.convert_from_path`). If Poppler is on PATH leave blank or set to the bin directory.

Image processing parameters (`IMAGE_PARAMS`)
- `denoising_strength`, `template_window_size`, `search_window_size` — used by denoising filters.
- `contour_area_threshold`, `max_contours` — box detection heuristics.
- `contrast_enhancement`, `number_width` — parameters to tune text/number extraction.
- `save_debug_images` — when `True` the pipeline saves annotated debug images to `DEBUG_DIR`.
- `debug_image_interval` — save one debug image for every N boxes processed.

Data columns
- `INPUT_COLUMNS` — column names expected in the raw extracted data CSV (used by `data_processor`).
- `OUTPUT_COLUMNS` — final column order and names placed into the processed Excel output.

Logging
- `LOG_FILE` — path to the logfile (default: `data/debug/electoral_roll_extractor.log`).
- `LOG_LEVEL` — default log level (e.g., `INFO`, `DEBUG`).
- `LOG_FORMAT` — standard logging format string.

Common edits for different environments
- Linux developer machine

```python
TESSERACT_CMD = '/usr/bin/tesseract'
POPPLER_PATH = '/usr/bin'  # or '' if pdftoppm is on PATH
INPUT_FOLDER = 'data/pdf2split'
```

- Windows machine (example)

```python
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'C:\path\to\poppler\bin'
```

Notes
- `config.py` creates `input`, `output`, and `debug` folders automatically if they do not exist.
- Keep `save_debug_images` enabled only during troubleshooting — debug images can grow disk usage quickly.
- When experimenting with recognition accuracy, change values in `IMAGE_PARAMS` and re-run a small PDF to evaluate effects.

If you'd like, I can add a small script `scripts/verify_config.py` that prints resolved paths and sanity-checks `TESSERACT_CMD` and `POPPLER_PATH` executables. Say the word and I will add it.
