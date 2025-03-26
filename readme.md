# Webpify

Webpify is a simple Python application that converts images to the WebP format. It supports various image formats and allows you to customize the quality of the output images.

## Features
- Convert images from common formats (JPEG, PNG, GIF) to WebP.
- Skip already converted WebP images.
- Specify custom quality for the WebP images.
- Flexible input and output directory options.

## Installation
```bash
pip install webpify
```
### Requirements
1. Ensure you have Python 3.9 or higher installed. 
   - Get Python from their [official website](https://www.python.org/downloads/).



## Usage

Run the application from the command line:

```bash
python -m webpify [path] [-o OUTPUT] [-q QUALITY] [-m MIME_TYPES] [-s SKIP_TYPES] [--delete]
```

### Arguments:
- `path`: Path to the directory containing images (default: current directory).
- `-o, --output`: Output directory for converted images (default: current directory).
- `-q, --quality`: Quality of the WebP images (default: 80).
- `-m, --mime-types`: List of image MIME types to convert (default: JPEG, PNG, GIF).
- `-s, --skip-types`: List of image MIME types to skip (default: WebP).
- `--delete`: Delete original files after conversion.

### Example:
Convert all images in the `images` folder to WebP format with 90% quality, save them in the `output` folder, and delete the original files:

```bash
python -m webpify images -o output -q 90 --delete
```

## Dependencies
- Python >= 3.9
- Pillow >= 11.1.0, < 12.0.0

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.