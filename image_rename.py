#!/usr/bin/env python3
#
# Copyright (C) 2025 Stephen Bonar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
ImageRename - Renames files from OriginalFilename_YYYYMMDD_Caption.extension
to YYYYMMDD_Caption_OriginalFilename.extension format.
"""

import os
import re
import sys
import argparse
from pathlib import Path

PROGRAM_NAME = "Image Renamer"
PROGRAM_VERSION = "v1.0.0"
PROGRAM_COPYRIGHT = "Copyright (C) 2025 Stephen Bonar"


def matches_old_filename_format(filename: str) -> re.Match | None:
    """
    Check if filename matches the original filename format from the old versions
    of the AI Photo Rename and AI Video Rename scripts, namely:
    OriginalFilename_YYYYMMDD_Caption.extension.

    Args:
        filename: The filename to check

    Returns:
        Match object if pattern matches, None otherwise
    """

    # Pattern: OriginalFilename_YYYYMMDD_Caption.extension
    # YYYYMMDD = 8 digits (date).
    pattern = r'^(.+)_(\d{8})_(.+)(\.\w+)$'

    return re.match(pattern, filename)


def generate_new_filename(filename: str) -> str | None:
    """
    Generate new filename in YYYYMMDD_Caption_OriginalFilename.extension
    format.

    Args:
        filename: Original filename in 
                  OriginalFilename_YYYYMMDD_Caption.extension format

    Returns:
        New filename or None if pattern doesn't match
    """

    # We want to skip any files that don't match the old filename format as
    # only files in that format should be renamed.
    match = matches_old_filename_format(filename)
    if not match:
        return None

    # Extract the components from the regex match groups (the parts enclosed
    # in parentheses in the regex pattern) so we can build the new filename
    # from them.
    original_filename = match.group(1)
    date = match.group(2) 
    description = match.group(3)
    extension = match.group(4)

    new_filename = f"{date}_{description}_{original_filename}{extension}"
    return new_filename


def rename_file(
    filepath: str | Path,
    dry_run: bool = False
) -> tuple[bool, str, str | None, str]:
    """
    Rename a single file if it matches the old filename format.

    Args:
        filepath: Path to the file to rename
        dry_run: If True, only show what would be renamed without actually
                 renaming

    Returns:
        Tuple of (success, old_name, new_name, message)
    """

    path = Path(filepath)

    if not path.exists():
        return False, str(path), None, "File does not exist"

    if not path.is_file():
        return False, str(path), None, "Not a file"

    filename = path.name
    new_filename = generate_new_filename(filename)

    if new_filename is None:
        return (
            False, filename, None,
            "Does not match OriginalFilename_YYYYMMDD_Caption pattern"
        )

    new_path = path.parent / new_filename

    if new_path.exists():
        return False, filename, new_filename, "Target file already exists"

    if dry_run:
        return True, filename, new_filename, "Would rename (dry run)"

    try:
        path.rename(new_path)
        return True, filename, new_filename, "Successfully renamed"
    except Exception as e:
        return False, filename, new_filename, f"Error: {str(e)}"


def rename_files_in_directory(
    directory: str | Path,
    recursive: bool = False,
    dry_run: bool = False
) -> dict:
    """
    Rename all matching files in a directory.

    Args:
        directory: Directory path to process
        recursive: If True, process subdirectories recursively
        dry_run: If True, only show what would be renamed

    Returns:
        Dictionary with statistics about the operation
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        print(f"Error: Directory '{directory}' does not exist")
        return {"error": True}

    if not dir_path.is_dir():
        print(f"Error: '{directory}' is not a directory")
        return {"error": True}

    stats = {
        "total": 0,
        "renamed": 0,
        "skipped": 0,
        "errors": 0,
        "error": False
    }

    if recursive:
        files = dir_path.rglob("*")
    else:
        files = dir_path.glob("*")

    # Use a list comprehension to rebuild the list with only files.
    files = [f for f in files if f.is_file()]

    for file_path in files:
        stats["total"] += 1
        success, old_name, new_name, message = rename_file(file_path, dry_run)

        if success:
            stats["renamed"] += 1
            print(f"✓ {old_name} -> {new_name}")
        elif new_name is None:
            stats["skipped"] += 1
        else:
            stats["errors"] += 1
            print(f"✗ {old_name}: {message}")

    return stats


def main() -> int:
    """Main entry point for the script."""
    
    parser = argparse.ArgumentParser(
        description=(
            "Rename files from OriginalFilename_YYYYMMDD_Caption.ext to "
            "YYYYMMDD_Caption_OriginalFilename.ext"
        ),
        epilog=(
            "Example: python image_rename.py /path/to/images"
        )
    )

    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="File or directory to process"
    )

    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Process subdirectories recursively (only for directories)"
    )

    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="Show what would be renamed without actually renaming files"
    )

    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show program version and exit"
    )

    args = parser.parse_args()

    if args.version:
        print(f"{PROGRAM_NAME} {PROGRAM_VERSION}")
        print(PROGRAM_COPYRIGHT)
        return 0

    if args.path is None:
        parser.print_usage()
        return 1

    if args.dry_run:
        print("=== DRY RUN MODE - No files will be renamed ===\n")

    path_obj = Path(args.path)
    if not path_obj.exists():
        print(f"Error: Path '{args.path}' does not exist")
        return 1

    if path_obj.is_file():
        success, old_name, new_name, message = rename_file(
            path_obj, args.dry_run
        )
        if success:
            print(f"✓ {old_name} -> {new_name}")
            return 0
        else:
            print(f"✗ {old_name}: {message}")
            return 1
    elif path_obj.is_dir():
        stats = rename_files_in_directory(
            args.path, args.recursive, args.dry_run
        )

        if stats.get("error"):
            return 1

        print("\n" + "="*50)
        print("Summary:")
        print(f"  Total files processed: {stats['total']}")
        print(f"  Successfully renamed: {stats['renamed']}")
        print(f"  Skipped (no match): {stats['skipped']}")
        print(f"  Errors: {stats['errors']}")
        print("="*50)

        return 0 if stats['errors'] == 0 else 1
    else:
        print(f"Error: Path '{args.path}' is neither a file nor a directory")
        return 1

if __name__ == "__main__":
    sys.exit(main())
