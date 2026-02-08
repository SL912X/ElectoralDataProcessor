"""
Electoral Roll Data Extractor

This script extracts voter information from electoral roll PDFs, processes
the extracted data, and outputs structured information to CSV and Excel files.

Usage:
    python main.py 
"""
import os
import sys
import logging
import argparse
from pathlib import Path
import cv2
import numpy as np
import pandas as pd
import pdf2image
import pytesseract
from tqdm import tqdm

# Import configuration
import config

# Import project modules
from extractor.image_processor import (
    preprocess_image, 
    find_boxes, 
    find_inner_boxes,
    create_debug_image
)
from extractor.text_extractor import process_voter_box
from extractor.data_processor import process_raw_data

def setup_logging():
    """Configure logging for the application."""
    # Create handlers
    file_handler = logging.FileHandler(config.LOG_FILE)
    console_handler = logging.StreamHandler()
    
    # Set log levels
    file_handler.setLevel(logging.DEBUG)
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Create formatter
    formatter = logging.Formatter(config.LOG_FORMAT)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger


def configure_environment():
    """Configure the environment for OCR and image processing."""
    logger = logging.getLogger(__name__)
    
    # Set Tesseract path
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD
    logger.info(f"Tesseract path set to: {config.TESSERACT_CMD}")
    
    # Verify input folder exists
    if not Path(config.INPUT_FOLDER).exists():
        logger.error(f"Input folder not found: {config.INPUT_FOLDER}")
        raise FileNotFoundError(f"Input folder not found: {config.INPUT_FOLDER}")
    
    # Verify Poppler path exists (if provided)
    if config.POPPLER_PATH and not Path(config.POPPLER_PATH).exists():
        logger.warning(f"Poppler path not found: {config.POPPLER_PATH}")
    
    logger.info("Environment configured successfully")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Electoral Roll Data Extractor")
    
    parser.add_argument(
        "--input-folder", 
        type=str,
        default=str(config.INPUT_FOLDER),
        help="Path to folder containing PDF files to process"
    )
    
    parser.add_argument(
        "--output-folder", 
        type=str,
        default=str(config.OUTPUT_DIR),
        help="Path to folder where output CSV/Excel files will be saved"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug mode with additional output and visualizations"
    )
    
    return parser.parse_args()


def get_pdf_files(input_folder):
    """
    Get all PDF files from the input folder.
    
    Args:
        input_folder: Path to the folder containing PDF files.
        
    Returns:
        A sorted list of PDF file paths.
    """
    logger = logging.getLogger(__name__)
    pdf_files = list(Path(input_folder).glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in: {input_folder}")
        return []
    
    pdf_files.sort()
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    for pdf_file in pdf_files:
        logger.info(f"  - {pdf_file.name}")
    
    return pdf_files


def extract_data_from_pdf(pdf_path):
    """
    Extract voter information from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file.
        
    Returns:
        A list of dictionaries containing extracted voter information.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting data extraction from: {pdf_path}")
    
    # Convert PDF to images
    logger.info("Converting PDF to images...")
    images = pdf2image.convert_from_path(
        pdf_path, 
        poppler_path=config.POPPLER_PATH
    )
    logger.info(f"PDF converted to {len(images)} images")
    
    # Container for extracted data
    all_data = []
    
    # Process each page
    for page_idx, image in enumerate(tqdm(images, desc="Processing pages")):
        # Convert PIL image to OpenCV format
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Preprocess the image
        preprocessed = preprocess_image(img)
        
        # Find voter boxes in the page
        boxes = find_boxes(preprocessed)
        logger.info(f"Found {len(boxes)} voter boxes on page {page_idx+1}")
        
        # Save debug image of all boxes
        if config.IMAGE_PARAMS["save_debug_images"]:
            debug_img = create_debug_image(img, boxes)
            debug_path = os.path.join(config.DEBUG_DIR, f"page_{page_idx+1}_boxes.png")
            cv2.imwrite(debug_path, debug_img)
        
        # Process each box
        for box_idx, box in enumerate(tqdm(boxes, desc=f"Page {page_idx+1} boxes", leave=False)):
            x, y, w, h = box
            
            # Extract region of interest
            roi = preprocessed[y:y+h, x:x+w]
            
            # Find inner box (voter number box)
            inner_boxes = find_inner_boxes(roi)
            
            if inner_boxes:
                inner_box = inner_boxes[0]
                
                # Extract data from the box
                box_data = process_voter_box(img, box, inner_box)
                
                # Add metadata
                box_data["page"] = page_idx + 1
                box_data["box"] = box_idx + 1
                
                # Add to collection
                all_data.append(box_data)
                
                # Save debug image at intervals
                if (config.IMAGE_PARAMS["save_debug_images"] and 
                    box_idx % config.IMAGE_PARAMS["debug_image_interval"] == 0):
                    
                    debug_img = create_debug_image(img, [box], 0, inner_box)
                    debug_path = os.path.join(
                        config.DEBUG_DIR, 
                        f"page_{page_idx+1}_box_{box_idx+1}.png"
                    )
                    cv2.imwrite(debug_path, debug_img)
            else:
                logger.warning(f"No inner box found in box {box_idx+1} on page {page_idx+1}")
    
    logger.info(f"Extraction complete. Extracted data from {len(all_data)} voter entries")
    return all_data


def save_raw_data(data, csv_path):
    """
    Save raw extracted data to a CSV file.
    
    Args:
        data: List of dictionaries containing extracted data.
        csv_path: Path to save the CSV file.
        
    Returns:
        The DataFrame containing the raw data.
    """
    logger = logging.getLogger(__name__)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv(csv_path, index=False)
    logger.info(f"Raw data saved to: {csv_path}")
    
    return df


def process_and_save_output(df, excel_path):
    """
    Process raw data and save structured output to Excel.
    
    Args:
        df: DataFrame containing raw extracted data.
        excel_path: Path to save the Excel file.
        
    Returns:
        The processed DataFrame.
    """
    logger = logging.getLogger(__name__)
    
    # Process the raw data
    processed_df = process_raw_data(df, config.INPUT_COLUMNS)
    
    # Select output columns
    output_df = processed_df[config.OUTPUT_COLUMNS]
    
    # Save to Excel
    output_df.to_excel(excel_path, index=False)
    logger.info(f"Processed data saved to: {excel_path}")
    
    return output_df


def main():
    """Main execution function."""
    # Set up logging
    logger = setup_logging()
    
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Configure environment
        configure_environment()
        
        # Get all PDF files from the input folder
        pdf_files = get_pdf_files(args.input_folder)
        
        if not pdf_files:
            logger.error("No PDF files found in the input folder")
            return 1
        
        # Create output folder if it doesn't exist
        Path(args.output_folder).mkdir(parents=True, exist_ok=True)
        
        # Track overall statistics
        total_voters = 0
        processed_files = 0
        failed_files = 0
        
        logger.info("=" * 50)
        logger.info(f"Starting batch processing of {len(pdf_files)} PDF files")
        logger.info("=" * 50)
        
        # Process each PDF file
        for pdf_file in pdf_files:
            logger.info(f"\n{'='*50}")
            logger.info(f"Processing: {pdf_file.name}")
            logger.info(f"{'='*50}")
            
            try:
                # Generate output file names based on input PDF name
                pdf_stem = pdf_file.stem  # Filename without extension
                csv_path = Path(args.output_folder) / f"{pdf_stem}_extracted.csv"
                excel_path = Path(args.output_folder) / f"{pdf_stem}_processed.xlsx"
                
                # Extract data from PDF
                data = extract_data_from_pdf(str(pdf_file))
                
                if not data:
                    logger.warning(f"No data extracted from: {pdf_file.name}")
                    failed_files += 1
                    continue
                
                # Save raw data to CSV
                raw_df = save_raw_data(data, csv_path)
                
                # Process and save output
                output_df = process_and_save_output(raw_df, excel_path)
                
                # Print summary for this file
                logger.info(f"✓ File completed successfully")
                logger.info(f"  Voter entries processed: {len(output_df)}")
                logger.info(f"  CSV saved to: {csv_path}")
                logger.info(f"  Excel saved to: {excel_path}")
                
                total_voters += len(output_df)
                processed_files += 1
                
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {e}", exc_info=True)
                failed_files += 1
                continue
        
        # Print final summary
        logger.info("\n" + "=" * 50)
        logger.info("Electoral Roll Batch Processing Complete")
        logger.info("=" * 50)
        logger.info(f"Total PDF files processed: {processed_files}/{len(pdf_files)}")
        logger.info(f"Failed files: {failed_files}")
        logger.info(f"Total voter entries processed: {total_voters}")
        logger.info(f"Output folder: {args.output_folder}")
        logger.info("=" * 50)
        
        return 0 if failed_files == 0 else 1
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
