"""
Main Window

The main application window containing the sound library panel (left)
and mixer panel (right) with session management features.
"""

import os
from typing import Dict, List, Any
from pathlib import Path

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                             QPushButton, QLabel, QFileDialog, QMessageBox, QMenuBar, QMenu,
                             QTreeView, QSizePolicy, QStatusBar, QScrollArea)
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QAction, QIcon
import qtawesome as qta
from core.sound_manager import SoundManager
from core.session import SessionManager
from core.themes import ThemeManager
from ui.mixer_track_widget import MixerTrackWidget
from ui.sound_library_widget import SoundLibraryWidget


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.sound_manager = SoundManager()
        self.session_manager = SessionManager()
        self.theme_manager = ThemeManager()
        self.tracks: Dict[str, MixerTrackWidget] = {}

        self._setup_ui()
        self._setup_menus()
        self._setup_connections()
        self._setup_theme()
        self._load_initial_sounds()
    
    def _setup_ui(self):
        """Set up the main user interface."""
        self.setWindowTitle(self.tr("Ambient Sound Mixer"))
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Sound Library
        left_panel = self._create_sound_library_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Mixer
        right_panel = self._create_mixer_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 1)  # Left panel
        splitter.setStretchFactor(1, 2)  # Right panel
        splitter.setSizes([400, 800])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Add sounds from the library to start mixing")
    
    def _create_sound_library_panel(self) -> QWidget:
        """Create the sound library panel with category tree view."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel(self.tr("Sound Library"))
        layout.addWidget(header)
        
        # Sound library tree view
        self.sound_library = SoundLibraryWidget()
        self.sound_library.set_sound_manager(self.sound_manager)
        self.sound_library.sound_selected.connect(self._on_sound_selected)
        
        
        
        layout.addWidget(self.sound_library)
        
        # Refresh button with qtawesome icon
        refresh_icon = qta.icon('fa5s.sync-alt', color='#555555')
        refresh_btn = QPushButton(refresh_icon, self.tr(" Refresh Library"))
        refresh_btn.clicked.connect(self._refresh_sound_library)
        refresh_btn.setMinimumHeight(35)
        layout.addWidget(refresh_btn)
        
        return panel
    
    def _create_mixer_panel(self) -> QWidget:
        """Create the mixer panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        header = QLabel(self.tr("Mixer Panel"))
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        # Play All button
        play_all_icon = qta.icon('fa5s.play-circle', color='#ff9800')
        play_all_btn = QPushButton(play_all_icon, self.tr(" Play All"))
        play_all_btn.clicked.connect(self._play_all_tracks)
        play_all_btn.setMinimumHeight(35)
        header_layout.addWidget(play_all_btn)

        # Clear Mixer button
        clear_icon = qta.icon('fa5s.trash-alt', color='#f44336')
        clear_btn = QPushButton(clear_icon, self.tr(" Clear Mixer"))
        clear_btn.clicked.connect(self._clear_mixer)
        clear_btn.setMinimumHeight(35)
        header_layout.addWidget(clear_btn)

        # Session controls
        save_icon = qta.icon('fa5s.save', color='#2e7d32')
        save_btn = QPushButton(save_icon, self.tr(" Save Session"))
        save_btn.clicked.connect(self._save_session)
        save_btn.setMinimumHeight(35)
        header_layout.addWidget(save_btn)

        load_icon = qta.icon('fa5s.folder-open', color='#1976d2')
        load_btn = QPushButton(load_icon, self.tr(" Load Session"))
        load_btn.clicked.connect(self._load_session)
        load_btn.setMinimumHeight(35)
        header_layout.addWidget(load_btn)
        
        layout.addLayout(header_layout)
        
        # Create a scroll area for the mixer tracks
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Container widget for the scroll area
        scroll_content = QWidget()
        self.mixer_layout = QVBoxLayout(scroll_content)
        self.mixer_layout.setSpacing(10)
        self.mixer_layout.setContentsMargins(5, 5, 5, 5)  # Add some padding
        
        # Add stretch to push tracks to top
        self.mixer_layout.addStretch()
        
        # Set the scroll area widget
        scroll_area.setWidget(scroll_content)
        
        # Add scroll area to the layout
        layout.addWidget(scroll_area, 1)  # The '1' makes it stretch to fill available space
        
        # Track count label
        self.track_count_label = QLabel(self.tr("No tracks loaded"))
        layout.addWidget(self.track_count_label)
        
        return panel
    
    def _setup_menus(self):
        """Set up the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu(self.tr("&File"))
        
        # Icons for menu actions
        save_icon = qta.icon('fa5s.save', color='#2e7d32')
        load_icon = qta.icon('fa5s.folder-open', color='#1976d2')
        import_icon = qta.icon('fa5s.file-import', color='#2196f3')

        # Import sounds action
        import_action = QAction(import_icon, self.tr("&Import Sounds"), self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self._import_sounds)
        file_menu.addAction(import_action)

        # Save session action
        save_action = QAction(save_icon, self.tr("&Save Session"), self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_session)
        file_menu.addAction(save_action)

        # Load session action
        load_action = QAction(load_icon, self.tr("&Load Session"), self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self._load_session)
        file_menu.addAction(load_action)

        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction(self.tr("E&xit"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu(self.tr("&View"))

        # Theme submenu
        theme_menu = view_menu.addMenu(self.tr("&Theme"))

        # Light theme action
        light_theme_action = QAction(self.tr("&Light Theme"), self)
        light_theme_action.triggered.connect(lambda: self._set_theme(ThemeManager.LIGHT_THEME))
        theme_menu.addAction(light_theme_action)

        # Dark theme action
        dark_theme_action = QAction(self.tr("&Dark Theme"), self)
        dark_theme_action.triggered.connect(lambda: self._set_theme(ThemeManager.DARK_THEME))
        theme_menu.addAction(dark_theme_action)

        view_menu.addSeparator()

        # Refresh library action
        refresh_action = QAction(self.tr("&Refresh Library"), self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_sound_library)
        view_menu.addAction(refresh_action)
    
    def _setup_theme(self):
        """Set up the initial theme."""
        self.theme_manager.apply_theme()

    def _set_theme(self, theme: str):
        """Set the application theme."""
        self.theme_manager.set_theme(theme)

    def _setup_connections(self):
        """Set up signal connections."""
        self.sound_manager.sounds_updated.connect(self._populate_sound_library)
        self.session_manager.session_loaded.connect(self._restore_session)
    
    def _load_initial_sounds(self):
        """Load initial sound library."""
        self._populate_sound_library()
    
    def _populate_sound_library(self):
        """Trigger refresh of the sound library tree view."""
        self.sound_library._update_tree()
    
    def _on_sound_selected(self, sound_path: str):
        """Handle sound selection from the library."""
        self._add_track(sound_path)
    
    def _refresh_sound_library(self):
        """Refresh the sound library."""
        self.sound_manager.refresh()
        self.status_bar.showMessage(self.tr("Sound library refreshed"), 2000)

    def _import_sounds(self):
        """Import user sound files."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter(self.tr("Audio Files (*.mp3 *.wav *.ogg)"))
        file_dialog.setWindowTitle(self.tr("Select Sound Files to Import"))
        file_dialog.setDirectory(str(Path.home()))  # Start in user's home directory

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                # Import the sounds
                successful_imports, imported_files = self.sound_manager.import_sounds(selected_files)

                if successful_imports > 0:
                    # Refresh the library to show newly imported sounds
                    self.sound_manager.refresh()
                    self.status_bar.showMessage(self.tr(f"Imported {successful_imports} sound{'s' if successful_imports != 1 else ''} successfully"), 3000)
                else:
                    QMessageBox.warning(self, self.tr("Import Failed"),
                                      self.tr("No valid audio files were imported."))
            else:
                self.status_bar.showMessage(self.tr("Import cancelled"), 2000)
    
    def _add_track(self, sound_file: str):
        """Add a sound track to the mixer."""
        if sound_file in self.tracks:
            QMessageBox.information(self, self.tr("Already Added"),
                                  self.tr(f"{Path(sound_file).stem} is already in the mixer."))
            return
        
        # Check if sound file exists
        if not os.path.exists(sound_file):
            QMessageBox.warning(self, self.tr("File Not Found"),
                              self.tr(f"Sound file not found: {sound_file}"))
            return
        
        # Create track widget
        track_widget = MixerTrackWidget(sound_file)
        track_widget.track_removed.connect(self._remove_track)
        
        # Insert before the stretch
        self.mixer_layout.insertWidget(self.mixer_layout.count() - 1, track_widget)
        
        self.tracks[sound_file] = track_widget
        self._update_track_count()
        
        sound_name = Path(sound_file).stem
        self.status_bar.showMessage(self.tr(f"Added {sound_name} to mixer"), 2000)
    
    def _remove_track(self, sound_file: str):
        """Remove a track from the mixer."""
        if sound_file in self.tracks:
            track_widget = self.tracks[sound_file]
            track_widget.stop()
            self.mixer_layout.removeWidget(track_widget)
            track_widget.deleteLater()
            del self.tracks[sound_file]
            self._update_track_count()
            
            sound_name = Path(sound_file).stem
            self.status_bar.showMessage(self.tr(f"Removed {sound_name} from mixer"), 2000)
    
    def _update_track_count(self):
        """Update the track count label."""
        count = len(self.tracks)
        if count == 0:
            self.track_count_label.setText(self.tr("No tracks loaded"))
        elif count == 1:
            self.track_count_label.setText(self.tr("1 track loaded"))
        else:
            self.track_count_label.setText(self.tr(f"{count} tracks loaded"))
    
    def _save_session(self):
        """Save the current mixer session."""
        if not self.tracks:
            QMessageBox.information(self, self.tr("No Tracks"),
                                  self.tr("No tracks to save. Add some sounds to the mixer first."))
            return
        
        filename, ok = QFileDialog.getSaveFileName(
            self, self.tr("Save Session"), "sessions", self.tr("JSON Files (*.json)"))
        
        if ok and filename:
            # Collect track states
            tracks_data = []
            for track_widget in self.tracks.values():
                tracks_data.append(track_widget.get_state())
            
            session_data = {
                "tracks": tracks_data,
                "metadata": {
                    "name": Path(filename).stem,
                    "description": f"Ambient mixer session with {len(tracks_data)} tracks"
                }
            }
            
            if self.session_manager.save_session(session_data, Path(filename).stem):
                QMessageBox.information(self, self.tr("Success"),
                                      self.tr(f"Session saved as {Path(filename).stem}"))
            else:
                QMessageBox.warning(self, self.tr("Error"), self.tr("Failed to save session"))
    
    def _load_session(self):
        """Load a mixer session."""
        filename, ok = QFileDialog.getOpenFileName(
            self, self.tr("Load Session"), "sessions", self.tr("JSON Files (*.json)"))
        
        if ok and filename:
            session = self.session_manager.load_session(filename)
            if session:
                self.status_bar.showMessage(self.tr(f"Loaded session: {Path(filename).stem}"), 3000)
    
    def _restore_session(self, session: Dict[str, Any]):
        """Restore mixer state from session data."""
        # Clear existing tracks
        for sound_file in list(self.tracks.keys()):
            self._remove_track(sound_file)
        
        # Add tracks from session
        tracks_data = session.get("tracks", [])
        loaded_count = 0
        
        for track_data in tracks_data:
            sound_file = track_data.get("sound_file")
            if sound_file and os.path.exists(sound_file):
                self._add_track(sound_file)
                if sound_file in self.tracks:
                    self.tracks[sound_file].set_state(track_data)
                    loaded_count += 1
            else:
                print(self.tr(f"Skipping missing sound file: {sound_file}"))
        
        self.status_bar.showMessage(self.tr(f"Restored {loaded_count} tracks from session"), 3000)
    
    def _play_all_tracks(self):
        """Play all tracks in the mixer that are not already playing."""
        if not self.tracks:
            QMessageBox.information(self, self.tr("No Tracks"), self.tr("No tracks to play. Add some sounds to the mixer first."))
            return

        played_count = 0
        for track_widget in self.tracks.values():
            if not track_widget.is_playing:
                track_widget._toggle_playback()
                played_count += 1

        if played_count == 0:
            self.status_bar.showMessage(self.tr("All tracks are already playing"), 2000)
        else:
            self.status_bar.showMessage(self.tr(f"Started {played_count} track{'s' if played_count != 1 else ''}"), 2000)

    def _clear_mixer(self):
        """Clear all tracks from the mixer."""
        if not self.tracks:
            QMessageBox.information(self, self.tr("No Tracks"), self.tr("No tracks to remove. Mixer is already clear."))
            return

        track_count = len(self.tracks)
        # Clear all tracks
        for sound_file in list(self.tracks.keys()):
            self._remove_track(sound_file)

        self.status_bar.showMessage(self.tr(f"Cleared {track_count} track{'s' if track_count != 1 else ''} from mixer"), 2000)

    def closeEvent(self, event):
        """Handle application close event."""
        # Stop all tracks
        for track_widget in self.tracks.values():
            track_widget.stop()

        event.accept()
