#!/usr/bin/env python3
"""
ImageRename - Renames files from IMG_XXXX_YYYYMMDD_Description.extension 
to YYYYMMDD_Description_IMG_XXXX.extension format.
"""

import os
import re
import sys
import argparse
from pathlib import Path


def matches_pattern(filename):
    """
    Check if filename matches the IMG_XXXX_YYYYMMDD pattern.
    
    Args:
        filename: The filename to check
        
    Returns:
        Match object if pattern matches, None otherwise
    """
    # Pattern: IMG_XXXX_YYYYMMDD_Description.extension
    # XXXX = 4 digits, YYYYMMDD = 8 digits (date)
    pattern = r'^IMG_(\d{4})_(\d{8})_(.+)(\.\w+)$'
    return re.match(pattern, filename)


def generate_new_filename(filename):
    """
    Generate new filename in YYYYMMDD_Description_IMG_XXXX.extension format.
    
    Args:
        filename: Original filename in IMG_XXXX_YYYYMMDD_Description.extension format
        
    Returns:
        New filename or None if pattern doesn't match
    """
    match = matches_pattern(filename)
    if not match:
        return None
    
    img_number = match.group(1)  # XXXX
    date = match.group(2)         # YYYYMMDD
    description = match.group(3)  # Description
    extension = match.group(4)    # .extension
    
    # New format: YYYYMMDD_Description_IMG_XXXX.extension
    new_filename = f"{date}_{description}_IMG_{img_number}{extension}"
    return new_filename


def rename_file(filepath, dry_run=False):
    """
    Rename a single file if it matches the pattern.
    
    Args:
        filepath: Path to the file to rename
        dry_run: If True, only show what would be renamed without actually renaming
        
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
        return False, filename, None, "Does not match IMG_XXXX_YYYYMMDD pattern"
    
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


def rename_files_in_directory(directory, recursive=False, dry_run=False):
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
    
    # Get files to process
    if recursive:
        files = dir_path.rglob("*")
    else:
        files = dir_path.glob("*")
    
    files = [f for f in files if f.is_file()]
    
    for file_path in files:
        stats["total"] += 1
        success, old_name, new_name, message = rename_file(file_path, dry_run)
        
        if success:
            stats["renamed"] += 1
            print(f"✓ {old_name} -> {new_name}")
        elif new_name is None:
            stats["skipped"] += 1
            # Don't print skipped files (files that don't match pattern)
        else:
            stats["errors"] += 1
            print(f"✗ {old_name}: {message}")
    
    return stats


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Rename files from IMG_XXXX_YYYYMMDD_Description.ext to YYYYMMDD_Description_IMG_XXXX.ext",
        epilog="Example: python image_rename.py /path/to/images"
    )
    
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Directory containing files to rename (default: current directory)"
    )
    
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Process subdirectories recursively"
    )
    
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Show what would be renamed without actually renaming files"
    )
    
    parser.add_argument(
        "-f", "--file",
        help="Rename a specific file instead of a directory"
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("=== DRY RUN MODE - No files will be renamed ===\n")
    
    if args.file:
        # Rename a single file
        success, old_name, new_name, message = rename_file(args.file, args.dry_run)
        if success:
            print(f"✓ {old_name} -> {new_name}")
            return 0
        else:
            print(f"✗ {old_name}: {message}")
            return 1
    else:
        # Rename files in directory
        stats = rename_files_in_directory(args.path, args.recursive, args.dry_run)
        
        if stats.get("error"):
            return 1
        
        # Print summary
        print("\n" + "="*50)
        print("Summary:")
        print(f"  Total files processed: {stats['total']}")
        print(f"  Successfully renamed: {stats['renamed']}")
        print(f"  Skipped (no match): {stats['skipped']}")
        print(f"  Errors: {stats['errors']}")
        print("="*50)
        
        return 0 if stats['errors'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
