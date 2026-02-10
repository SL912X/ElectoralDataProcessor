#!/usr/bin/env python3
"""
Merge Excel files by concatenating their rows into a single workbook.

This script reads multiple Excel files from a directory or file list,
concatenates them, optionally deduplicates based on a column, and writes
the result to an output Excel file.

Usage examples:
  python merge_excels.py --input-dir data/xlsx --pattern "*.xlsx" --output merged.xlsx
  python merge_excels.py --files file1.xlsx file2.xlsx --output merged.xlsx --dedup --dedup-col "EPIC No"
"""
import pandas as pd
from pathlib import Path
import argparse
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def find_files(input_dir: str, pattern: str):
    """Find all files matching pattern in input directory."""
    p = Path(input_dir)
    if not p.exists():
        raise FileNotFoundError(f"Input directory {input_dir} not found")
    files = sorted(p.rglob(pattern))
    return files


def read_excel_file(path: Path, sheet_name=0):
    """Read an Excel file and return DataFrame."""
    try:
        df = pd.read_excel(path, sheet_name=sheet_name, engine='openpyxl')
        logger.info(f"Read {len(df)} rows from {path.name}")
        return df
    except Exception as e:
        logger.warning(f"Error reading {path}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Merge multiple Excel files into a single workbook."
    )
    parser.add_argument(
        "--input-dir", "-d",
        type=str,
        default="data/xlsx",
        help="Directory containing Excel files (default: data/xlsx)"
    )
    parser.add_argument(
        "--files", "-f",
        nargs="+",
        help="Specific files to merge (overrides --input-dir)"
    )
    parser.add_argument(
        "--pattern", "-p",
        type=str,
        default="*.xlsx",
        help="Glob pattern for files (default: *.xlsx)"
    )
    parser.add_argument(
        "--sheet", "-s",
        default=0,
        help="Sheet name or index to read from each file (default: 0)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="merged.xlsx",
        help="Output Excel file (default: merged.xlsx)"
    )
    parser.add_argument(
        "--dedup",
        action="store_true",
        help="Remove duplicate rows after merging"
    )
    parser.add_argument(
        "--dedup-col",
        type=str,
        help="Column name to use for deduplication (if not set, all columns used)"
    )
    
    args = parser.parse_args()

    # Determine files to process
    if args.files:
        files = [Path(f) for f in args.files]
        logger.info(f"Processing {len(files)} specified files")
    else:
        files = list(find_files(args.input_dir, args.pattern))
        logger.info(f"Found {len(files)} files in {args.input_dir} matching '{args.pattern}'")

    if not files:
        logger.error("No files found to merge")
        sys.exit(1)

    # Read and concatenate all files
    dfs = []
    for f in files:
        df = read_excel_file(f, sheet_name=args.sheet)
        if df is not None:
            dfs.append(df)

    if not dfs:
        logger.error("No data could be read from files")
        sys.exit(1)

    # Concatenate all dataframes
    merged_df = pd.concat(dfs, ignore_index=True, sort=False)
    logger.info(f"Concatenated {len(dfs)} files: {len(merged_df)} total rows")

    # Deduplicate if requested
    if args.dedup:
        original_count = len(merged_df)
        if args.dedup_col:
            if args.dedup_col not in merged_df.columns:
                logger.warning(
                    f"Column '{args.dedup_col}' not found. Available columns: {list(merged_df.columns)}"
                )
                merged_df = merged_df.drop_duplicates()
            else:
                merged_df = merged_df.drop_duplicates(subset=[args.dedup_col])
                logger.info(f"Deduplicated on column '{args.dedup_col}'")
        else:
            merged_df = merged_df.drop_duplicates()
            logger.info("Deduplicated on all columns")
        
        removed = original_count - len(merged_df)
        logger.info(f"Removed {removed} duplicate rows, {len(merged_df)} unique rows remain")

    # Write output
    try:
        merged_df.to_excel(args.output, index=False, engine='openpyxl')
        logger.info(f"✓ Successfully wrote {len(merged_df)} rows to {args.output}")
    except Exception as e:
        logger.error(f"Error writing output file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
