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
                             QTreeView, QSizePolicy, QStatusBar, QScrollArea, QApplication)
from PySide6.QtCore import Qt, Signal, QSize, QTimer, QLocale
from PySide6.QtGui import QAction, QIcon
import qtawesome as qta
from core.sound_manager import SoundManager
from core.session import SessionManager
from core.themes import ThemeManager
from ui.mixer_track_widget import MixerTrackWidget
from ui.sound_library_widget import SoundLibraryWidget


class MainWindow(QMainWindow):
    """Main application window."""

    language_changed = Signal(str) # Signal to notify main.py of language change
    
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
        self.setWindowTitle("Ambient Sound Mixer") # Set initial title without tr()
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create splitter for resizable panels
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Sound Library
        self.left_panel = self._create_sound_library_panel()
        self.splitter.addWidget(self.left_panel)
        
        # Right panel - Mixer
        self.right_panel = self._create_mixer_panel()
        self.splitter.addWidget(self.right_panel)
        
        # Set splitter proportions
        self.splitter.setStretchFactor(0, 1)  # Left panel
        self.splitter.setStretchFactor(1, 2)  # Right panel
        self.splitter.setSizes([400, 800])
        
        self.main_layout.addWidget(self.splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Add sounds from the library to start mixing")
    
    def _create_sound_library_panel(self) -> QWidget:
        """Create the sound library panel with category tree view."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        self.sound_library_header = QLabel(self.tr("Sound Library"))
        layout.addWidget(self.sound_library_header)
        
        # Sound library tree view
        self.sound_library = SoundLibraryWidget()
        self.sound_library.set_sound_manager(self.sound_manager)
        self.sound_library.sound_selected.connect(self._on_sound_selected)
        
        
        
        layout.addWidget(self.sound_library)
        
        # Refresh button with qtawesome icon
        refresh_icon = qta.icon('fa5s.sync-alt', color='#555555')
        self.refresh_btn = QPushButton(refresh_icon, self.tr(" Refresh Library"))
        self.refresh_btn.clicked.connect(self._refresh_sound_library)
        self.refresh_btn.setMinimumHeight(35)
        layout.addWidget(self.refresh_btn)
        
        return panel
    
    def _create_mixer_panel(self) -> QWidget:
        """Create the mixer panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        self.mixer_panel_header = QLabel(self.tr("Mixer Panel"))
        header_layout.addWidget(self.mixer_panel_header)
        
        header_layout.addStretch()
        
        # Play All button
        play_all_icon = qta.icon('fa5s.play-circle', color='#ff9800')
        self.play_all_btn = QPushButton(play_all_icon, self.tr(" Play All"))
        self.play_all_btn.clicked.connect(self._play_all_tracks)
        self.play_all_btn.setMinimumHeight(35)
        header_layout.addWidget(self.play_all_btn)

        # Clear Mixer button
        clear_icon = qta.icon('fa5s.trash-alt', color='#f44336')
        self.clear_btn = QPushButton(clear_icon, self.tr(" Clear Mixer"))
        self.clear_btn.clicked.connect(self._clear_mixer)
        self.clear_btn.setMinimumHeight(35)
        header_layout.addWidget(self.clear_btn)

        # Session controls
        save_icon = qta.icon('fa5s.save', color='#2e7d32')
        self.save_btn = QPushButton(save_icon, self.tr(" Save Session"))
        self.save_btn.clicked.connect(self._save_session)
        self.save_btn.setMinimumHeight(35)
        header_layout.addWidget(self.save_btn)

        load_icon = qta.icon('fa5s.folder-open', color='#1976d2')
        self.load_btn = QPushButton(load_icon, self.tr(" Load Session"))
        self.load_btn.clicked.connect(self._load_session)
        self.load_btn.setMinimumHeight(35)
        header_layout.addWidget(self.load_btn)
        
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
        self.file_menu = menubar.addMenu(self.tr("&File"))
        
        # Icons for menu actions
        save_icon = qta.icon('fa5s.save', color='#2e7d32')
        load_icon = qta.icon('fa5s.folder-open', color='#1976d2')
        import_icon = qta.icon('fa5s.file-import', color='#2196f3')

        # Import sounds action
        self.import_action = QAction(import_icon, self.tr("&Import Sounds"), self)
        self.import_action.setShortcut("Ctrl+I")
        self.import_action.triggered.connect(self._import_sounds)
        self.file_menu.addAction(self.import_action)

        # Save session action
        self.save_action = QAction(save_icon, self.tr("&Save Session"), self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self._save_session)
        self.file_menu.addAction(self.save_action)

        # Load session action
        self.load_action = QAction(load_icon, self.tr("&Load Session"), self)
        self.load_action.setShortcut("Ctrl+O")
        self.load_action.triggered.connect(self._load_session)
        self.file_menu.addAction(self.load_action)

        self.file_menu.addSeparator()
        
        # Exit action
        self.exit_action = QAction(self.tr("E&xit"), self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)
        
        # View menu
        self.view_menu = menubar.addMenu(self.tr("&View"))

        # Theme submenu
        self.theme_menu = self.view_menu.addMenu(self.tr("&Theme"))

        # Light theme action
        self.light_theme_action = QAction(self.tr("&Light Theme"), self)
        self.light_theme_action.triggered.connect(lambda: self._set_theme(ThemeManager.LIGHT_THEME))
        self.theme_menu.addAction(self.light_theme_action)

        # Dark theme action
        self.dark_theme_action = QAction(self.tr("&Dark Theme"), self)
        self.dark_theme_action.triggered.connect(lambda: self._set_theme(ThemeManager.DARK_THEME))
        self.theme_menu.addAction(self.dark_theme_action)

        self.view_menu.addSeparator()

        # Refresh library action
        self.refresh_action = QAction(self.tr("&Refresh Library"), self)
        self.refresh_action.setShortcut("F5")
        self.refresh_action.triggered.connect(self._refresh_sound_library)
        self.view_menu.addAction(self.refresh_action)
        
        # Language submenu
        self.language_menu = self.view_menu.addMenu(self.tr("&Language"))

        # English language action
        self.en_action = QAction(self.tr("&English"), self)
        self.en_action.triggered.connect(lambda: self._set_language("en_US"))
        self.language_menu.addAction(self.en_action)

        # Italian language action
        self.it_action = QAction(self.tr("&Italian"), self)
        self.it_action.triggered.connect(lambda: self._set_language("it_IT"))
        self.language_menu.addAction(self.it_action)
    
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
        
    def _set_language(self, locale: str):
        """Set the application language."""
        self.language_changed.emit(locale)

    def _retranslate_ui(self):
        """Retranslate all UI elements."""
        self.setWindowTitle(self.tr("Ambient Sound Mixer"))
        self.sound_library_header.setText(self.tr("Sound Library"))
        self.refresh_btn.setText(self.tr(" Refresh Library"))
        self.mixer_panel_header.setText(self.tr("Mixer Panel"))
        self.play_all_btn.setText(self.tr(" Play All"))
        self.clear_btn.setText(self.tr(" Clear Mixer"))
        self.save_btn.setText(self.tr(" Save Session"))
        self.load_btn.setText(self.tr(" Load Session"))
        self._update_track_count()
        
        # Retranslate menus
        self.file_menu.setTitle(self.tr("&File"))
        self.import_action.setText(self.tr("&Import Sounds"))
        self.save_action.setText(self.tr("&Save Session"))
        self.load_action.setText(self.tr("&Load Session"))
        self.exit_action.setText(self.tr("E&xit"))
        
        self.view_menu.setTitle(self.tr("&View"))
        self.theme_menu.setTitle(self.tr("&Theme"))
        self.light_theme_action.setText(self.tr("&Light Theme"))
        self.dark_theme_action.setText(self.tr("&Dark Theme"))
        self.refresh_action.setText(self.tr("&Refresh Library"))
        self.language_menu.setTitle(self.tr("&Language"))
        self.en_action.setText(self.tr("&English"))
        self.it_action.setText(self.tr("&Italian"))

        # Update status bar message
        self.status_bar.showMessage(self.tr("Ready - Add sounds from the library to start mixing"))

        # Retranslate children widgets if they have their own tr() calls
        for track_widget in self.tracks.values():
            track_widget.retranslate_ui() # Assuming MixerTrackWidget has a retranslate_ui method
        self.sound_library.retranslate_ui() # Assuming SoundLibraryWidget has a retranslate_ui method

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
                    self.status_bar.showMessage(self.tr("Imported {} sound(s) successfully").format(successful_imports), 3000)
                else:
                    QMessageBox.warning(self, self.tr("Import Failed"),
                                      self.tr("No valid audio files were imported."))
            else:
                self.status_bar.showMessage(self.tr("Import cancelled"), 2000)
    
    def _add_track(self, sound_file: str):
        """Add a sound track to the mixer."""
        if sound_file in self.tracks:
            QMessageBox.information(self, self.tr("Already Added"),
                                  self.tr("{} is already in the mixer.").format(Path(sound_file).stem))
            return
        
        # Check if sound file exists
        if not os.path.exists(sound_file):
            QMessageBox.warning(self, self.tr("File Not Found"),
                              self.tr("Sound file not found: {}").format(sound_file))
            return
        
        # Create track widget
        track_widget = MixerTrackWidget(sound_file)
        track_widget.track_removed.connect(self._remove_track)
        
        # Insert before the stretch
        self.mixer_layout.insertWidget(self.mixer_layout.count() - 1, track_widget)
        
        self.tracks[sound_file] = track_widget
        self._update_track_count()
        
        sound_name = Path(sound_file).stem
        self.status_bar.showMessage(self.tr("Added {} to mixer").format(sound_name), 2000)
    
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
            self.status_bar.showMessage(self.tr("Removed {} from mixer").format(sound_name), 2000)
    
    def _update_track_count(self):
        """Update the track count label."""
        count = len(self.tracks)
        if count == 0:
            self.track_count_label.setText(self.tr("No tracks loaded"))
        elif count == 1:
            self.track_count_label.setText(self.tr("1 track loaded"))
        else:
            self.track_count_label.setText(self.tr("{} tracks loaded").format(count))
    
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
                                      self.tr("Session saved as {}").format(Path(filename).stem))
            else:
                QMessageBox.warning(self, self.tr("Error"), self.tr("Failed to save session"))
    
    def _load_session(self):
        """Load a mixer session."""
        filename, ok = QFileDialog.getOpenFileName(
            self, self.tr("Load Session"), "sessions", self.tr("JSON Files (*.json)"))
        
        if ok and filename:
            session = self.session_manager.load_session(filename)
            if session:
                self.status_bar.showMessage(self.tr("Loaded session: {}").format(Path(filename).stem), 3000)
    
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
                print(self.tr("Skipping missing sound file: {}").format(sound_file))

        self.status_bar.showMessage(self.tr("Restored {} tracks from session").format(loaded_count), 3000)
    
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
            self.status_bar.showMessage(self.tr("Started {} track(s)").format(played_count), 2000)

    def _clear_mixer(self):
        """Clear all tracks from the mixer."""
        if not self.tracks:
            QMessageBox.information(self, self.tr("No Tracks"), self.tr("No tracks to remove. Mixer is already clear."))
            return

        track_count = len(self.tracks)
        # Clear all tracks
        for sound_file in list(self.tracks.keys()):
            self._remove_track(sound_file)

        self.status_bar.showMessage(self.tr("Cleared {} track(s) from mixer").format(track_count), 2000)

    def closeEvent(self, event):
        """Handle application close event."""
        # Stop all tracks
        for track_widget in self.tracks.values():
            track_widget.stop()

        event.accept()
