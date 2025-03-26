import os
import argparse
from pathlib import Path
from PIL import Image

# Predefined lists of image mime types
DEFAULT_MIME_TYPES = ["image/jpeg", "image/png", "image/gif"]
DEFAULT_SKIP_TYPES = ["image/webp"]

def convert_to_webp(input_path, output_path, quality, mime_types, skip_types):
    """Converts images in the given path to WebP format."""
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        print(f"Error: The path {input_path} does not exist.")
        return

    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)

    for root, _, files in os.walk(input_path):
        for file in files:
            file_path = Path(root) / file
            try:
                # Skip files that are already in WebP format
                if file_path.suffix.lower() == ".webp":
                    print(f"Skipping {file_path} (already in WebP format)")
                    continue

                # Open the image and check its mime type
                with Image.open(file_path) as img:
                    # Ensure img.format is not None before accessing MIME type
                    if img.format is None:
                        print(f"Skipping {file_path} (unknown image format)")
                        continue

                    mime_type = Image.MIME.get(img.format)

                    if mime_type in skip_types:
                        print(f"Skipping {file_path} (mime type: {mime_type})")
                        continue

                    if mime_type not in mime_types:
                        print(f"Skipping {file_path} (unsupported mime type: {mime_type})")
                        continue

                    # Convert and save the image as WebP
                    relative_path = file_path.relative_to(input_path)
                    output_file = output_path / relative_path.with_suffix(".webp")
                    output_file.parent.mkdir(parents=True, exist_ok=True)

                    img.save(output_file, "WEBP", quality=quality)
                    print(f"Converted {file_path} to {output_file}")

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Convert images to WebP format.")
    parser.add_argument("path", nargs="?", default=".", help="Path to the directory containing images (default: current directory).")
    parser.add_argument("-o", "--output", default=".", help="Output directory for converted images (default: current directory).")
    parser.add_argument("-q", "--quality", type=int, default=80, help="Quality of the WebP images (default: 80).")
    parser.add_argument("-m", "--mime-types", nargs="*", default=DEFAULT_MIME_TYPES, help="List of image mime types to convert (default: common types).")
    parser.add_argument("-s", "--skip-types", nargs="*", default=DEFAULT_SKIP_TYPES, help="List of image mime types to skip (default: WebP).")

    args = parser.parse_args()

    convert_to_webp(
        input_path=args.path,
        output_path=args.output,
        quality=args.quality,
        mime_types=args.mime_types,
        skip_types=args.skip_types
    )

if __name__ == "__main__":
    main()