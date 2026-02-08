# `main.py` — Extractor entrypoint

Overview
- `main.py` is the primary CLI entrypoint for batch processing PDF electoral rolls. It coordinates converting PDFs to images, detecting voter boxes, running OCR via Tesseract, and saving both raw and processed outputs.

High-level flow
- Parse CLI args (`--input-folder`, `--output-folder`, `--debug`).
- Configure environment (set `pytesseract` path, validate folders).
- Locate `.pdf` files in `--input-folder`.
- For each PDF: convert pages to images, preprocess, detect voter boxes, extract text, save raw CSV and processed Excel.

Key functions (in `main.py`)
- `setup_logging()` — configures file + console logging using `config.LOG_FILE`, `config.LOG_LEVEL`, `config.LOG_FORMAT`.
- `configure_environment()` — sets `pytesseract.pytesseract.tesseract_cmd` to `config.TESSERACT_CMD` and validates input/debug directories and `config.POPPLER_PATH`.
- `parse_arguments()` — returns parsed arguments for input/output and debug mode.
- `get_pdf_files(input_folder)` — collects `.pdf` files from the input folder.
- `extract_data_from_pdf(pdf_path)` — converts PDF pages to images with `pdf2image`, runs image processing to find boxes, then calls `process_voter_box` from `extractor.text_extractor` to extract fields.
- `save_raw_data(data, csv_path)` — writes the intermediate raw extraction DataFrame to CSV.
- `process_and_save_output(df, excel_path)` — runs `process_raw_data` from `extractor.data_processor`, selects `config.OUTPUT_COLUMNS`, and writes an Excel file.

CLI usage examples
- Default run (uses `config.py` paths):

```bash
python main.py
```

- Specify custom folders:

```bash
python main.py --input-folder data/pdf2split --output-folder data/output
```

- Enable debug mode (saves debug images and prints more logs):

```bash
python main.py --debug
```

Expected outputs
- For each input PDF named `X.pdf`, `main.py` writes:
  - raw CSV: `{output_folder}/X_extracted.csv`
  - processed Excel: `{output_folder}/X_processed.xlsx`
- Debug images (if enabled) are written to the directory configured as `config.DEBUG_DIR`.

Logs
- Logs are written to `config.LOG_FILE` and streamed to console. Increase verbosity by changing `config.LOG_LEVEL` or running with `--debug`.

Troubleshooting
- No PDF files found: verify `--input-folder` or `config.INPUT_FOLDER` and that files have `.pdf` extension.
- Tesseract not found: ensure `config.TESSERACT_CMD` points to a valid `tesseract` binary and is executable.
- Poppler conversion errors: install `poppler-utils` and ensure `config.POPPLER_PATH` points to a valid poppler binary folder (or leave blank if `pdftoppm` is on PATH).

Developer notes
- Unit-testable units:
  - image pre-processing and box detection in `extractor/image_processor.py`
  - OCR parsing in `extractor/text_extractor.py`
  - data normalization in `extractor/data_processor.py`
- To add a CLI option, update `parse_arguments()` and document it in this file.

Quick sanity test
1. Place a small test PDF in the input folder.
2. Run `python main.py --input-folder path/to/test --output-folder path/to/out --debug`.
3. Confirm `{pdf}_extracted.csv` and `{pdf}_processed.xlsx` appear in the output folder.
