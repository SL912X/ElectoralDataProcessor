"""
PDF Splitter Program
Splits PDF files into 2 parts:
- File 1: Pages 1, 2, and last page
- File 2: Pages 3 to second-to-last page

Supports:
1. Single PDF file processing
2. Batch processing of multiple PDFs from a folder
"""

import sys
from pathlib import Path
try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    print("Error: PyPDF2 is not installed. Please install it using: pip install PyPDF2")
    sys.exit(1)


def split_pdf(input_pdf, output_dir="data/output2"):
    """
    Split PDF into two files based on page requirements.
    
    Args:
        input_pdf (str): Path to the input PDF file
        output_dir (str): Directory to save output PDF files
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    # Validate input file
    input_path = Path(input_pdf)
    if not input_path.exists():
        print(f"Error: Input file '{input_pdf}' not found.")
        return False
    
    if input_path.suffix.lower() != '.pdf':
        print("Error: Input file must be a PDF file.")
        return False
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Read the input PDF
        pdf_reader = PdfReader(input_pdf)
        total_pages = len(pdf_reader.pages)
        
        if total_pages < 3:
            print(f"Error: PDF must have at least 3 pages. This PDF has {total_pages} page(s).")
            return False
        
        print(f"Total pages in PDF: {total_pages}")
        
        # Create first PDF writer (pages 1, 2, and last page)
        pdf_writer1 = PdfWriter()
        pdf_writer1.add_page(pdf_reader.pages[0])  # Page 1
        pdf_writer1.add_page(pdf_reader.pages[1])  # Page 2
        pdf_writer1.add_page(pdf_reader.pages[-1])  # Last page
        
        # Create second PDF writer (pages 3 to second-to-last page)
        pdf_writer2 = PdfWriter()
        for page_num in range(2, total_pages - 1):  # Pages 3 to second-to-last
            pdf_writer2.add_page(pdf_reader.pages[page_num])
        
        # Generate output file names
        input_name = input_path.stem
        output_file1 = output_path / f"{input_name}_part1.pdf"
        output_file2 = output_path / f"{input_name}_part2.pdf"
        
        # Write the first output PDF
        with open(output_file1, 'wb') as f:
            pdf_writer1.write(f)
        print(f"✓ Created: {output_file1}")
        print(f"  Contains: Page 1, Page 2, Page {total_pages}")
        
        # Write the second output PDF (only if there are pages 3 to second-to-last)
        if total_pages > 3:
            with open(output_file2, 'wb') as f:
                pdf_writer2.write(f)
            print(f"✓ Created: {output_file2}")
            print(f"  Contains: Pages 3 to {total_pages - 1}")
        else:
            print(f"ℹ No pages for part 2 (PDF has exactly 3 pages)")
        
        print("\n✓ PDF splitting completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: Failed to process PDF - {str(e)}")
        return False


def main():
    """Main function to handle command-line arguments."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single file:  python pdf_splitter.py <input_pdf_file> [output_directory]")
        print("  Batch mode:   python pdf_splitter.py --batch <input_folder> <output_folder>")
        print("\nExamples:")
        print("  python pdf_splitter.py input.pdf")
        print("  python pdf_splitter.py input.pdf data/output")
        print("  python pdf_splitter.py --batch data/input data/output")
        sys.exit(1)
    
    # Check if batch mode
    if sys.argv[1] == "--batch":
        if len(sys.argv) < 4:
            print("Error: Batch mode requires input folder and output folder")
            print("Usage: python pdf_splitter.py --batch <input_folder> <output_folder>")
            sys.exit(1)
        
        input_folder = sys.argv[2]
        output_folder = sys.argv[3]
        process_folder(input_folder, output_folder)
    else:
        # Single file mode
        input_pdf = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "data/output"
        split_pdf(input_pdf, output_dir)


def process_folder(input_folder, output_folder):
    """
    Process all PDF files in a given folder.
    
    Args:
        input_folder (str): Path to the folder containing PDF files
        output_folder (str): Path to the output folder for split PDFs
    
    Returns:
        None
    """
    input_path = Path(input_folder)
    
    # Validate input folder
    if not input_path.exists():
        print(f"Error: Input folder '{input_folder}' not found.")
        return
    
    if not input_path.is_dir():
        print(f"Error: '{input_folder}' is not a directory.")
        return
    
    # Get all PDF files in the folder
    pdf_files = list(input_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in '{input_folder}'")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to process\n")
    
    # Create output folder
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Process each PDF file
    successful = 0
    failed = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
        if split_pdf(str(pdf_file), output_folder):
            successful += 1
        else:
            failed += 1
        print()
    
    # Print summary
    print("=" * 60)
    print(f"Processing Summary:")
    print(f"  Total files:     {len(pdf_files)}")
    print(f"  Successful:      {successful}")
    print(f"  Failed:          {failed}")
    print(f"  Output folder:   {output_folder}")
    print("=" * 60)


if __name__ == "__main__":
    main()
