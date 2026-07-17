"""Authorized, model-free admission of immutable historical evidence."""

from .models import GitRecord, SourceSet
from .source import DirectoryGitReader, SubprocessGitReader, build_manifest

__all__ = [
    "DirectoryGitReader",
    "GitRecord",
    "SourceSet",
    "SubprocessGitReader",
    "build_manifest",
]
