"""File management service for handling input/output paths."""

from pathlib import Path
from typing import Iterator


class FileManager:
    """Service for file discovery, path resolution, and validation."""

    def __init__(self, output_dir: Path | None = None) -> None:
        """
        Initialize the file manager.

        Args:
            output_dir: Default output directory for converted files.
        """
        self._output_dir = output_dir or Path("dcv_output")

    @property
    def output_dir(self) -> Path:
        """Get the output directory."""
        return self._output_dir

    def ensure_output_dir(self) -> Path:
        """
        Ensure the output directory exists.

        Returns:
            The output directory path.
        """
        self._output_dir.mkdir(parents=True, exist_ok=True)
        return self._output_dir

    def validate_input_path(self, path: Path) -> None:
        """
        Validate that an input path exists.

        Args:
            path: Path to validate.

        Raises:
            FileNotFoundError: If the path does not exist.
        """
        if not path.exists():
            raise FileNotFoundError(f"Input path does not exist: {path}")

    def find_files(
        self,
        source: Path,
        extensions: set[str],
        recursive: bool = True,
    ) -> Iterator[Path]:
        """
        Find files with specified extensions in a directory or return single file.

        Args:
            source: Source file or directory path.
            extensions: Set of file extensions to match (e.g., {'.pdf', '.PDF'}).
            recursive: Whether to search recursively in directories.

        Yields:
            Paths to matching files.

        Raises:
            FileNotFoundError: If source does not exist.
        """
        self.validate_input_path(source)

        if source.is_file():
            if source.suffix.lower() in {ext.lower() for ext in extensions}:
                yield source
            return

        if source.is_dir():
            pattern = "**/*" if recursive else "*"
            for file_path in source.glob(pattern):
                if file_path.is_file() and file_path.suffix.lower() in {
                    ext.lower() for ext in extensions
                }:
                    yield file_path

    def get_output_path(
        self,
        input_path: Path,
        output_extension: str,
        source_dir: Path | None = None,
    ) -> Path:
        """
        Generate output path for a converted file.

        Args:
            input_path: Original input file path.
            output_extension: Target file extension (e.g., '.md', '.pdf').
            source_dir: Source directory for relative path calculation.
                       If None, only the filename is used.

        Returns:
            Output path preserving relative directory structure.
        """
        if source_dir and input_path.is_relative_to(source_dir):
            relative_path = input_path.relative_to(source_dir)
            output_path = self._output_dir / relative_path.with_suffix(output_extension)
        else:
            output_path = self._output_dir / input_path.with_suffix(
                output_extension
            ).name

        return output_path

    def generate_path_pairs(
        self,
        source: Path,
        input_extensions: set[str],
        output_extension: str,
        recursive: bool = True,
    ) -> Iterator[tuple[Path, Path]]:
        """
        Generate input/output path pairs for batch conversion.

        Args:
            source: Source file or directory.
            input_extensions: Set of input file extensions.
            output_extension: Target output extension.
            recursive: Whether to search recursively.

        Yields:
            Tuples of (input_path, output_path).
        """
        source_dir = source if source.is_dir() else None

        for input_path in self.find_files(source, input_extensions, recursive):
            output_path = self.get_output_path(
                input_path, output_extension, source_dir
            )
            yield input_path, output_path
