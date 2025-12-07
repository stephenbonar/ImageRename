# ImageRename

Performs a mass rename of files renamed with the initial version of AiPhotoRename or AiVideoRename.

This Python script renames files from the format `OriginalFilename_YYYYMMDD_Caption.extension` to `YYYYMMDD_Caption_OriginalFilename.extension`, where:
- **XXXX** = Four-digit number (e.g., 0001, 1234)
- **YYYYMMDD** = Date in YYYYMMDD format (e.g., 20231215)
- **Caption** = AI generated caption (e.g., Beach_Sunset, Mountain_View)
- **extension** = File extension (e.g., .jpg, .png, .mp4)

## Requirements

- Python 3.6 or higher

## Usage

### Basic Usage

Rename all matching files in the current directory:
```bash
python image_rename.py
```

Rename all matching files in a specific directory:
```bash
python image_rename.py /path/to/images
```

### Options

- `-r, --recursive` - Process subdirectories recursively
- `-n, --dry-run` - Show what would be renamed without actually renaming files
- `-f FILE, --file FILE` - Rename a specific file instead of a directory
- `-h, --help` - Show help message

### Examples

**Dry run to preview changes:**
```bash
python image_rename.py --dry-run /path/to/images
```

**Process directory and all subdirectories:**
```bash
python image_rename.py --recursive /path/to/images
```

**Rename a single file:**
```bash
python image_rename.py --file IMG_0001_20231215_Vacation.jpg
```

## Example

Before:
- `IMG_0001_20231215_Beach_Sunset.jpg`
- `IMG_0002_20231216_Mountain_View.png`
- `IMG_0003_20240101_New_Year.mp4`

After:
- `20231215_Beach_Sunset_IMG_0001.jpg`
- `20231216_Mountain_View_IMG_0002.png`
- `20240101_New_Year_IMG_0003.mp4`

## Remarks

This script was used for me to change my initial renames of images and videos after I decided
I didn't like the original format. It may not be that useful for any other purpose, but feel
free to use it as an example or modify it for your own purposes.

## License

See LICENSE file for details.
