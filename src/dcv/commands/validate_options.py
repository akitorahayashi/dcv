"""Common utilities for CLI commands."""

from pathlib import Path
from typing import Optional

import typer


def validate_input_options(
    file: Optional[Path], directory: Optional[Path]
) -> tuple[Path, bool]:
    """
    Validate and return the input source.

    Args:
        file: Optional file path.
        directory: Optional directory path.

    Returns:
        Tuple of (source_path, is_directory).

    Raises:
        typer.BadParameter: If neither or both options are provided.
    """
    if file is None and directory is None:
        raise typer.BadParameter("Either --file/-f or --dir/-d must be specified.")

    if file is not None and directory is not None:
        raise typer.BadParameter(
            "Cannot specify both --file/-f and --dir/-d. Choose one."
        )

    if file is not None:
        return file, False
    return directory, True  # type: ignore
