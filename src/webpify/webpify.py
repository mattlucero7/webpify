import os
import argparse
from pathlib import Path
from PIL import Image
import multiprocessing # Import the multiprocessing module
import functools # For passing multiple arguments with starmap

# Predefined lists of image mime types
DEFAULT_MIME_TYPES = ["image/jpeg", "image/png", "image/gif"]
DEFAULT_SKIP_TYPES = ["image/webp"]

# --- Worker Function ---
# This function processes a single image file.
# It needs to be defined at the top level so multiprocessing can pickle it.
def _process_single_image(args_tuple):
    """Worker function to convert a single image to WebP."""
    # Unpack arguments passed via starmap
    file_path, input_path_base, output_path_base, quality, mime_types, skip_types, delete_original = args_tuple

    try:
        # Skip files that are already in WebP format (redundant check, but safe)
        if file_path.suffix.lower() == ".webp":
            # This check might be better placed before adding to the task list,
            # but keeping it here ensures worker robustness.
            # print(f"Skipping {file_path} (already in WebP format)")
            return f"Skipped (already WebP): {file_path}"

        # Open the image and check its mime type
        with Image.open(file_path) as img:
            # Ensure img.format is not None before accessing MIME type
            if img.format is None:
                return f"Skipped (unknown format): {file_path}"

            mime_type = Image.MIME.get(img.format)

            if mime_type in skip_types:
                return f"Skipped (mime type {mime_type}): {file_path}"

            if mime_type not in mime_types:
                return f"Skipped (unsupported mime type {mime_type}): {file_path}"

            # Determine output path
            relative_path = file_path.relative_to(input_path_base)
            output_file = output_path_base / relative_path.with_suffix(".webp")
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Convert and save the image as WebP
            img.save(output_file, "WEBP", quality=quality)
            result_msg = f"Converted {file_path} to {output_file}"

            # Delete original file if delete_original is True
            if delete_original:
                try:
                    file_path.unlink()
                    result_msg += f" | Deleted original {file_path}"
                except Exception as del_e:
                    # Handle potential deletion errors separately
                    result_msg += f" | FAILED to delete original {file_path}: {del_e}"

            return result_msg

    except Exception as e:
        return f"Error processing {file_path}: {e}"

# --- Main Conversion Logic ---
def convert_to_webp_parallel(input_path, output_path, quality, mime_types, skip_types, delete_original):
    """Converts images in the given path to WebP format using multiprocessing."""
    input_path = Path(input_path).resolve() # Use resolved paths
    output_path = Path(output_path).resolve()

    if not input_path.exists():
        print(f"Error: The input path {input_path} does not exist.")
        return

    if not output_path.exists():
        print(f"Creating output directory: {output_path}")
        output_path.mkdir(parents=True, exist_ok=True)

    tasks = []
    print("Scanning for image files...")
    for root, _, files in os.walk(input_path):
        current_dir = Path(root)
        for file in files:
            file_path = current_dir / file
            # Basic filtering before adding to task list (optional, but efficient)
            if file_path.suffix.lower() == ".webp":
                continue
            # Add more filtering here if needed (e.g., based on simple suffix before opening)

            # Prepare arguments for the worker function
            # Pass base paths as resolved Paths
            args_tuple = (
                file_path,
                input_path, # Pass the resolved base input path
                output_path, # Pass the resolved base output path
                quality,
                mime_types,
                skip_types,
                delete_original
            )
            tasks.append(args_tuple)

    if not tasks:
        print("No eligible image files found to convert.")
        return

    print(f"Found {len(tasks)} potential images to process.")
    print(f"Starting conversion with {os.cpu_count()} worker processes...")

    # Use multiprocessing Pool with context manager
    # Defaults to os.cpu_count() processes
    with multiprocessing.Pool() as pool:
        # Use starmap to pass multiple arguments to the worker function
        results = pool.starmap(_process_single_image, tasks)

    print("\n--- Conversion Summary ---")
    # Print results/status from each task
    processed_count = 0
    error_count = 0
    skipped_count = 0
    for msg in results:
        print(msg)
        if "Converted" in msg:
            processed_count += 1
        elif "Error" in msg:
            error_count += 1
        elif "Skipped" in msg:
            skipped_count += 1

    print("---")
    print(f"Total tasks: {len(tasks)}")
    print(f"Successfully converted: {processed_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Errors: {error_count}")
    print("Conversion process finished.")


# --- Main Execution Block ---
def main():
    parser = argparse.ArgumentParser(description="Convert images to WebP format using multiple processes.")
    # Keep arguments the same
    parser.add_argument("path", nargs="?", default=".", help="Path to the directory containing images (default: current directory).")
    parser.add_argument("-o", "--output", default=".", help="Output directory for converted images (default: current directory).")
    parser.add_argument("-q", "--quality", type=int, default=80, help="Quality of the WebP images (default: 80).")
    parser.add_argument("-m", "--mime-types", nargs="*", default=DEFAULT_MIME_TYPES, help="List of image mime types to convert.")
    parser.add_argument("-s", "--skip-types", nargs="*", default=DEFAULT_SKIP_TYPES, help="List of image mime types to skip.")
    parser.add_argument("--delete", action="store_true", help="Delete original files after conversion.")

    args = parser.parse_args()

    # Call the parallel conversion function
    convert_to_webp_parallel(
        input_path=args.path,
        output_path=args.output,
        quality=args.quality,
        mime_types=args.mime_types,
        skip_types=args.skip_types,
        delete_original=args.delete
    )

# --- IMPORTANT: Multiprocessing Guard ---
# This ensures the Pool is only created when the script is run directly,
# crucial on platforms like Windows.
if __name__ == "__main__":
    # Ensure Pillow uses the correct MIME types (usually automatic, but good practice)
    Image.init()
    main()