#!/usr/bin/env python3
"""
Tests for the ImageRename script.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add parent directory to path to import image_rename
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from image_rename import (
    matches_pattern,
    generate_new_filename,
    rename_file,
    rename_files_in_directory
)


class TestPatternMatching(unittest.TestCase):
    """Test pattern matching functionality."""
    
    def test_valid_pattern(self):
        """Test that valid patterns are matched correctly."""
        filename = "IMG_0001_20231215_Vacation.jpg"
        match = matches_pattern(filename)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "0001")  # XXXX
        self.assertEqual(match.group(2), "20231215")  # YYYYMMDD
        self.assertEqual(match.group(3), "Vacation")  # Description
        self.assertEqual(match.group(4), ".jpg")  # extension
    
    def test_valid_pattern_with_longer_description(self):
        """Test pattern with multi-word description."""
        filename = "IMG_1234_20250101_New_Year_Party.png"
        match = matches_pattern(filename)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(3), "New_Year_Party")
    
    def test_invalid_pattern_wrong_img_number(self):
        """Test that files with wrong IMG number format don't match."""
        # Not 4 digits
        self.assertIsNone(matches_pattern("IMG_001_20231215_Test.jpg"))
        self.assertIsNone(matches_pattern("IMG_12345_20231215_Test.jpg"))
    
    def test_invalid_pattern_wrong_date(self):
        """Test that files with wrong date format don't match."""
        # Not 8 digits
        self.assertIsNone(matches_pattern("IMG_0001_2023_Test.jpg"))
        self.assertIsNone(matches_pattern("IMG_0001_202312_Test.jpg"))
        self.assertIsNone(matches_pattern("IMG_0001_202312151_Test.jpg"))
    
    def test_invalid_pattern_missing_description(self):
        """Test that files without description don't match."""
        self.assertIsNone(matches_pattern("IMG_0001_20231215.jpg"))
    
    def test_invalid_pattern_no_prefix(self):
        """Test that files without IMG prefix don't match."""
        self.assertIsNone(matches_pattern("0001_20231215_Test.jpg"))
        self.assertIsNone(matches_pattern("PHOTO_0001_20231215_Test.jpg"))


class TestFilenameGeneration(unittest.TestCase):
    """Test new filename generation."""
    
    def test_generate_new_filename(self):
        """Test basic filename generation."""
        old = "IMG_0001_20231215_Vacation.jpg"
        new = generate_new_filename(old)
        self.assertEqual(new, "20231215_Vacation_IMG_0001.jpg")
    
    def test_generate_new_filename_complex_description(self):
        """Test filename generation with complex description."""
        old = "IMG_1234_20250101_New_Year_Party.png"
        new = generate_new_filename(old)
        self.assertEqual(new, "20250101_New_Year_Party_IMG_1234.png")
    
    def test_generate_new_filename_different_extension(self):
        """Test filename generation with different file extensions."""
        test_cases = [
            ("IMG_0001_20231215_Test.jpeg", "20231215_Test_IMG_0001.jpeg"),
            ("IMG_0001_20231215_Test.PNG", "20231215_Test_IMG_0001.PNG"),
            ("IMG_0001_20231215_Test.mp4", "20231215_Test_IMG_0001.mp4"),
            ("IMG_0001_20231215_Test.MOV", "20231215_Test_IMG_0001.MOV"),
        ]
        for old, expected in test_cases:
            with self.subTest(filename=old):
                new = generate_new_filename(old)
                self.assertEqual(new, expected)
    
    def test_generate_new_filename_invalid_pattern(self):
        """Test that invalid patterns return None."""
        invalid_files = [
            "IMG_001_20231215_Test.jpg",
            "IMG_0001_2023_Test.jpg",
            "IMG_0001_20231215.jpg",
            "NotMatching.jpg",
        ]
        for filename in invalid_files:
            with self.subTest(filename=filename):
                self.assertIsNone(generate_new_filename(filename))


class TestFileRenaming(unittest.TestCase):
    """Test actual file renaming operations."""
    
    def setUp(self):
        """Create a temporary directory for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)
    
    def test_rename_valid_file(self):
        """Test renaming a valid file."""
        old_name = "IMG_0001_20231215_Vacation.jpg"
        old_path = self.test_path / old_name
        old_path.touch()
        
        success, old, new, msg = rename_file(old_path)
        
        self.assertTrue(success)
        self.assertEqual(old, old_name)
        self.assertEqual(new, "20231215_Vacation_IMG_0001.jpg")
        self.assertFalse(old_path.exists())
        self.assertTrue((self.test_path / new).exists())
    
    def test_rename_file_dry_run(self):
        """Test dry run mode doesn't actually rename files."""
        old_name = "IMG_0001_20231215_Test.jpg"
        old_path = self.test_path / old_name
        old_path.touch()
        
        success, old, new, msg = rename_file(old_path, dry_run=True)
        
        self.assertTrue(success)
        self.assertEqual(new, "20231215_Test_IMG_0001.jpg")
        self.assertTrue(old_path.exists())  # File should still exist
        self.assertFalse((self.test_path / new).exists())
    
    def test_rename_invalid_pattern(self):
        """Test that files not matching pattern aren't renamed."""
        old_name = "NotMatchingPattern.jpg"
        old_path = self.test_path / old_name
        old_path.touch()
        
        success, old, new, msg = rename_file(old_path)
        
        self.assertFalse(success)
        self.assertIsNone(new)
        self.assertTrue(old_path.exists())
    
    def test_rename_nonexistent_file(self):
        """Test handling of nonexistent file."""
        old_path = self.test_path / "nonexistent.jpg"
        
        success, old, new, msg = rename_file(old_path)
        
        self.assertFalse(success)
        self.assertIn("does not exist", msg)
    
    def test_rename_target_exists(self):
        """Test handling when target file already exists."""
        old_name = "IMG_0001_20231215_Test.jpg"
        new_name = "20231215_Test_IMG_0001.jpg"
        
        old_path = self.test_path / old_name
        new_path = self.test_path / new_name
        
        old_path.touch()
        new_path.touch()  # Create target file
        
        success, old, new, msg = rename_file(old_path)
        
        self.assertFalse(success)
        self.assertIn("already exists", msg)
        self.assertTrue(old_path.exists())


class TestDirectoryRenaming(unittest.TestCase):
    """Test batch renaming in directories."""
    
    def setUp(self):
        """Create a temporary directory with test files."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)
    
    def test_rename_multiple_files(self):
        """Test renaming multiple files in a directory."""
        files = [
            "IMG_0001_20231215_First.jpg",
            "IMG_0002_20231216_Second.jpg",
            "IMG_0003_20231217_Third.jpg",
        ]
        
        for filename in files:
            (self.test_path / filename).touch()
        
        stats = rename_files_in_directory(self.test_dir)
        
        self.assertFalse(stats.get("error", False))
        self.assertEqual(stats["renamed"], 3)
        self.assertEqual(stats["errors"], 0)
        
        # Check new files exist
        self.assertTrue((self.test_path / "20231215_First_IMG_0001.jpg").exists())
        self.assertTrue((self.test_path / "20231216_Second_IMG_0002.jpg").exists())
        self.assertTrue((self.test_path / "20231217_Third_IMG_0003.jpg").exists())
    
    def test_rename_mixed_files(self):
        """Test directory with both matching and non-matching files."""
        files = [
            "IMG_0001_20231215_Match.jpg",
            "NotMatching.jpg",
            "IMG_0002_20231216_AlsoMatch.png",
            "random_file.txt",
        ]
        
        for filename in files:
            (self.test_path / filename).touch()
        
        stats = rename_files_in_directory(self.test_dir)
        
        self.assertEqual(stats["renamed"], 2)
        self.assertEqual(stats["skipped"], 2)
        self.assertEqual(stats["errors"], 0)
    
    def test_rename_recursive(self):
        """Test recursive directory processing."""
        # Create subdirectory
        subdir = self.test_path / "subdir"
        subdir.mkdir()
        
        (self.test_path / "IMG_0001_20231215_Root.jpg").touch()
        (subdir / "IMG_0002_20231216_Sub.jpg").touch()
        
        stats = rename_files_in_directory(self.test_dir, recursive=True)
        
        self.assertEqual(stats["renamed"], 2)
        self.assertTrue((self.test_path / "20231215_Root_IMG_0001.jpg").exists())
        self.assertTrue((subdir / "20231216_Sub_IMG_0002.jpg").exists())
    
    def test_rename_nonrecursive(self):
        """Test non-recursive directory processing (default)."""
        subdir = self.test_path / "subdir"
        subdir.mkdir()
        
        (self.test_path / "IMG_0001_20231215_Root.jpg").touch()
        (subdir / "IMG_0002_20231216_Sub.jpg").touch()
        
        stats = rename_files_in_directory(self.test_dir, recursive=False)
        
        # Should only rename file in root directory
        self.assertEqual(stats["renamed"], 1)
        self.assertTrue((self.test_path / "20231215_Root_IMG_0001.jpg").exists())
        self.assertFalse((subdir / "20231216_Sub_IMG_0002.jpg").exists())
        self.assertTrue((subdir / "IMG_0002_20231216_Sub.jpg").exists())
    
    def test_dry_run_directory(self):
        """Test dry run on directory."""
        (self.test_path / "IMG_0001_20231215_Test.jpg").touch()
        
        stats = rename_files_in_directory(self.test_dir, dry_run=True)
        
        self.assertEqual(stats["renamed"], 1)
        # Original file should still exist
        self.assertTrue((self.test_path / "IMG_0001_20231215_Test.jpg").exists())
        # New file should not exist
        self.assertFalse((self.test_path / "20231215_Test_IMG_0001.jpg").exists())


if __name__ == "__main__":
    unittest.main()
