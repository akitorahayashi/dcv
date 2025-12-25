"""Unit tests for the file manager service."""

from pathlib import Path

import pytest

from dcv.services.file_manager import FileManager


class TestFileManager:
    """Unit tests for FileManager."""

    def test_output_dir_property(self, tmp_path: Path):
        """Test that output_dir property returns correct value."""
        manager = FileManager(output_dir=tmp_path / "output")
        assert manager.output_dir == tmp_path / "output"

    def test_output_dir_default(self):
        """Test that default output directory is set."""
        manager = FileManager()
        assert manager.output_dir == Path("dcv_output")

    def test_ensure_output_dir_creates_directory(self, tmp_path: Path):
        """Test that ensure_output_dir creates the directory."""
        output_dir = tmp_path / "new_output"
        manager = FileManager(output_dir=output_dir)

        assert not output_dir.exists()
        result = manager.ensure_output_dir()
        assert output_dir.exists()
        assert result == output_dir

    def test_validate_input_path_exists(self, tmp_path: Path):
        """Test that validation passes for existing paths."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        manager = FileManager()
        # Should not raise
        manager.validate_input_path(test_file)

    def test_validate_input_path_not_exists(self, tmp_path: Path):
        """Test that validation fails for non-existing paths."""
        manager = FileManager()
        with pytest.raises(FileNotFoundError, match="Input path does not exist"):
            manager.validate_input_path(tmp_path / "nonexistent.txt")

    def test_find_files_single_file(self, tmp_path: Path):
        """Test finding a single file."""
        test_file = tmp_path / "document.pdf"
        test_file.write_bytes(b"test")

        manager = FileManager()
        files = list(manager.find_files(test_file, {".pdf"}))

        assert len(files) == 1
        assert files[0] == test_file

    def test_find_files_single_file_wrong_extension(self, tmp_path: Path):
        """Test that single file with wrong extension is not returned."""
        test_file = tmp_path / "document.txt"
        test_file.write_text("test")

        manager = FileManager()
        files = list(manager.find_files(test_file, {".pdf"}))

        assert len(files) == 0

    def test_find_files_directory(self, tmp_path: Path):
        """Test finding files in a directory."""
        # Create test files
        (tmp_path / "doc1.pdf").write_bytes(b"test")
        (tmp_path / "doc2.pdf").write_bytes(b"test")
        (tmp_path / "readme.txt").write_text("test")

        manager = FileManager()
        files = list(manager.find_files(tmp_path, {".pdf"}))

        assert len(files) == 2
        filenames = {f.name for f in files}
        assert filenames == {"doc1.pdf", "doc2.pdf"}

    def test_find_files_recursive(self, tmp_path: Path):
        """Test recursive file finding."""
        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "root.pdf").write_bytes(b"test")
        (subdir / "nested.pdf").write_bytes(b"test")

        manager = FileManager()
        files = list(manager.find_files(tmp_path, {".pdf"}, recursive=True))

        assert len(files) == 2
        filenames = {f.name for f in files}
        assert filenames == {"root.pdf", "nested.pdf"}

    def test_find_files_non_recursive(self, tmp_path: Path):
        """Test non-recursive file finding."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "root.pdf").write_bytes(b"test")
        (subdir / "nested.pdf").write_bytes(b"test")

        manager = FileManager()
        files = list(manager.find_files(tmp_path, {".pdf"}, recursive=False))

        assert len(files) == 1
        assert files[0].name == "root.pdf"

    def test_find_files_case_insensitive(self, tmp_path: Path):
        """Test that extension matching is case-insensitive."""
        (tmp_path / "doc1.PDF").write_bytes(b"test")
        (tmp_path / "doc2.pdf").write_bytes(b"test")

        manager = FileManager()
        files = list(manager.find_files(tmp_path, {".pdf"}))

        assert len(files) == 2

    def test_get_output_path_simple(self, tmp_path: Path):
        """Test simple output path generation."""
        manager = FileManager(output_dir=tmp_path / "output")
        input_path = Path("/some/path/document.pdf")

        output_path = manager.get_output_path(input_path, ".md")

        assert output_path == tmp_path / "output" / "document.md"

    def test_get_output_path_with_source_dir(self, tmp_path: Path):
        """Test output path with relative structure preservation."""
        manager = FileManager(output_dir=tmp_path / "output")
        source_dir = tmp_path / "input"
        source_dir.mkdir()
        subdir = source_dir / "subdir"
        subdir.mkdir()
        input_path = subdir / "document.pdf"
        input_path.write_bytes(b"test")

        output_path = manager.get_output_path(input_path, ".md", source_dir)

        assert output_path == tmp_path / "output" / "subdir" / "document.md"

    def test_generate_path_pairs_single_file(self, tmp_path: Path):
        """Test path pair generation for single file."""
        manager = FileManager(output_dir=tmp_path / "output")
        input_file = tmp_path / "document.pdf"
        input_file.write_bytes(b"test")

        pairs = list(manager.generate_path_pairs(input_file, {".pdf"}, ".md"))

        assert len(pairs) == 1
        assert pairs[0][0] == input_file
        assert pairs[0][1] == tmp_path / "output" / "document.md"

    def test_generate_path_pairs_directory(self, tmp_path: Path):
        """Test path pair generation for directory."""
        manager = FileManager(output_dir=tmp_path / "output")

        input_dir = tmp_path / "input"
        input_dir.mkdir()
        (input_dir / "doc1.pdf").write_bytes(b"test")
        (input_dir / "doc2.pdf").write_bytes(b"test")

        pairs = list(manager.generate_path_pairs(input_dir, {".pdf"}, ".md"))

        assert len(pairs) == 2
        output_names = {p[1].name for p in pairs}
        assert output_names == {"doc1.md", "doc2.md"}
