"""Basic Windows filesystem utilities for the File Archaeologist project.

This module provides low-level helpers for working with Windows paths,
file attributes and directory listing. It has no dependencies on other
project modules and is intended to be imported by navigation, analysis
and search modules.
"""

from __future__ import annotations

import os
import platform
import stat
from pathlib import Path
from typing import List, Tuple, Union

try:
    import ctypes
    HAS_CTYPES = True
except ImportError:  # pragma: no cover - ctypes is stdlib, but be safe
    HAS_CTYPES = False

PathString = Union[str, Path]

# Windows-specific constants.
FORBIDDEN_CHARS = set('/:*?"<>|')
MAX_PATH_LENGTH = 260

# Windows file attribute flags.
FILE_ATTRIBUTE_READONLY = 0x1
FILE_ATTRIBUTE_HIDDEN = 0x2
FILE_ATTRIBUTE_SYSTEM = 0x4
FILE_ATTRIBUTE_DIRECTORY = 0x10
INVALID_FILE_ATTRIBUTES = 0xFFFFFFFF


def is_windows_os():
    """Return True if running on Windows."""
    return platform.system() == "Windows"


def get_windows_attributes(path):
    """Return raw Windows attribute flags for path."""
    try:
        return os.stat(path).st_file_attributes
    except (OSError, AttributeError):
        pass

    if HAS_CTYPES and is_windows_os():
        try:
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
            if attrs == INVALID_FILE_ATTRIBUTES:
                return INVALID_FILE_ATTRIBUTES
            return attrs
        except (OSError, AttributeError):
            pass

    return INVALID_FILE_ATTRIBUTES


def validate_segment(segment):
    """Return error message for an invalid segment, or None if valid."""
    for ch in segment:
        if ch in FORBIDDEN_CHARS:
            return f"forbidden character {ch!r} in segment {segment!r}"
    if segment.endswith(" ") or segment.endswith("."):
        return f"segment {segment!r} ends with a space or dot"
    return None


def validate_windows_path(path):
    """Validate a Windows path syntactically; return (ok, reason)."""
    if not isinstance(path, (str, Path)):
        return False, f"path must be str or Path, got {type(path).__name__}"

    raw = str(path)
    if not raw.strip():
        return False, "path is empty"

    if len(raw) > MAX_PATH_LENGTH:
        return False, (
            f"path length {len(raw)} exceeds the {MAX_PATH_LENGTH}-character "
            "limit (long paths are not supported at stage I)"
        )

    normalized = raw.replace("/", "\\")
    drive, remainder = os.path.splitdrive(normalized)

    if drive and not (len(drive) == 2 and drive[1] == ":"):
        return False, f"invalid drive prefix {drive!r}"

    if drive and not drive[0].isalpha():
        return False, f"invalid drive letter in {drive!r}"

    body = remainder if drive else normalized
    for segment in body.split("\\"):
        if segment == "":
            continue
        err = validate_segment(segment)
        if err:
            return False, err

    return True, ""


def format_size(size_bytes):
    """Format a byte count as a human-readable Windows-style string."""
    if size_bytes < 0:
        return "0 B"
    if size_bytes < 1024:
        return f"{size_bytes} B"

    value = float(size_bytes)
    for unit in ("KB", "MB", "GB", "TB", "PB"):
        value /= 1024.0
        if value < 1024.0:
            return f"{value:.1f} {unit}"
    return f"{value:.1f} EB"


def get_parent_path(path):
    """Return the parent directory of a Windows path."""
    raw = str(path)
    if not raw:
        return "."

    normalized = os.path.normpath(raw)
    parent = os.path.dirname(normalized)

    if parent == "":
        return "."
    return parent


def safe_windows_listdir(path):
    """Return directory entries, or [] on any error."""
    try:
        return os.listdir(path)
    except (PermissionError, FileNotFoundError, OSError):
        return []


def is_hidden_windows_file(path):
    """Return True if path has the FILE_ATTRIBUTE_HIDDEN flag."""
    attrs = get_windows_attributes(path)
    if attrs == INVALID_FILE_ATTRIBUTES:
        return False
    return bool(attrs & FILE_ATTRIBUTE_HIDDEN)
