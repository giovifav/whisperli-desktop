"""
Sound Manager Module

Handles loading and managing sound files from the 'sounds/' directory.
Provides functionality to scan for audio files (.mp3, .wav, .ogg) organized by categories.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from PySide6.QtCore import QObject, Signal


class SoundManager(QObject):
    """Manages sound file discovery and organization."""

    sounds_updated = Signal()

    def __init__(self, sounds_dir: str = None):
        super().__init__()
        if sounds_dir is None:
            if getattr(sys, '_MEIPASS', False):
                # Running as bundled onefile executable, sounds in temp dir
                sounds_dir = os.path.join(sys._MEIPASS, 'sounds')
            else:
                # Development or bundled onedir: check if 'sounds' exists relative, else try absolute exe dir
                sounds_dir = 'sounds'
        self.sounds_dir = Path(sounds_dir)

        # Additional check: if sounds_dir doesn't exist (e.g., running exe from wrong CWD), fallback to exe dir
        if not self.sounds_dir.exists():
            exe_dir = os.path.dirname(sys.executable)
            alt_sounds = os.path.join(exe_dir, 'sounds')
            if os.path.exists(alt_sounds):
                self.sounds_dir = Path(alt_sounds)

        # Set up user sounds directory (always alongside the program/exe)
        self.user_sounds_dir = self._get_user_sounds_dir()

        self.categories: Dict[str, List[str]] = {}
        self._scan_sounds()

    def _get_user_sounds_dir(self) -> Path:
        """Get the directory for user imported sounds (alongside the program/exe)."""
        # Get directory of the executable or script
        if getattr(sys, '_MEIPASS', False):
            # Running as bundled onefile executable
            exe_dir = os.path.dirname(sys.executable)
        else:
            # Development mode - use current working directory
            exe_dir = os.getcwd()

        return Path(exe_dir) / 'user_sounds'

    def _scan_sounds(self) -> None:
        """Scan the sounds directory for audio files (.mp3, .wav, .ogg) organized by category."""
        self.categories.clear()

        if not self.sounds_dir.exists():
            print(f"Warning: Sounds directory '{self.sounds_dir}' does not exist")
            return

        # Supported audio file extensions
        audio_extensions = ['*.mp3', '*.wav', '*.ogg']

        # Scan each subdirectory as a category
        for category_dir in self.sounds_dir.iterdir():
            if category_dir.is_dir():
                category_name = category_dir.name
                sound_files = []

                # Find all audio files in this category
                for ext in audio_extensions:
                    for sound_file in category_dir.glob(ext):
                        if sound_file.is_file():
                            sound_files.append(str(sound_file))

                if sound_files:
                    self.categories[category_name] = sorted(sound_files)

        # Scan user sounds directory for imported files
        if self.user_sounds_dir.exists():
            user_sound_files = []
            for ext in audio_extensions:
                for sound_file in self.user_sounds_dir.glob(ext):
                    if sound_file.is_file():
                        user_sound_files.append(str(sound_file))

            if user_sound_files:
                self.categories["User Sounds"] = sorted(user_sound_files)
        else:
            # Create the directory if it doesn't exist
            self.user_sounds_dir.mkdir(parents=True, exist_ok=True)

        self.sounds_updated.emit()
    
    def get_categories(self) -> List[str]:
        """Get list of available sound categories."""
        return sorted(self.categories.keys())
    
    def get_sounds_in_category(self, category: str) -> List[str]:
        """Get list of sound file paths in a specific category."""
        return self.categories.get(category, [])

    def get_sounds(self, category: str) -> List[str]:
        """Alias for get_sounds_in_category."""
        return self.get_sounds_in_category(category)
    
    def get_sound_name(self, file_path: str) -> str:
        """Extract the sound name from file path."""
        return Path(file_path).stem
    
    def refresh(self) -> None:
        """Refresh the sound library by re-scanning the directory."""
        self._scan_sounds()
    
    def get_all_sounds(self) -> Dict[str, List[str]]:
        """Get all sounds organized by category."""
        return self.categories.copy()
    
    def is_valid_sound_file(self, file_path: str) -> bool:
        """Check if the given path is a valid audio file (.mp3, .wav, .ogg)."""
        path = Path(file_path)
        supported_extensions = ['.mp3', '.wav', '.ogg']
        return path.exists() and path.suffix.lower() in supported_extensions and path.is_file()

    def import_sounds(self, file_paths: List[str]) -> tuple[int, List[str]]:
        """
        Import sound files to the user sounds directory.

        Args:
            file_paths: List of file paths to import

        Returns:
            Tuple of (successful_imports, list_of_imported_files)
        """
        # Ensure user sounds directory exists
        self.user_sounds_dir.mkdir(parents=True, exist_ok=True)

        imported_files = []
        successful_imports = 0

        for file_path in file_paths:
            if not self.is_valid_sound_file(file_path):
                continue

            src_path = Path(file_path)
            filename = src_path.name
            dst_path = self.user_sounds_dir / filename

            # Handle filename conflicts by appending numbers
            counter = 1
            while dst_path.exists():
                stem = src_path.stem
                suffix = src_path.suffix
                new_name = "02d"
                dst_path = self.user_sounds_dir / new_name

            try:
                shutil.copy2(src_path, dst_path)
                imported_files.append(str(dst_path))
                successful_imports += 1
            except Exception as e:
                print(f"Error copying file {file_path}: {e}")

        return successful_imports, imported_files
