"""
Mixer Track Widget

Represents an individual sound track in the mixer panel.
Contains QMediaPlayer for playback, volume control, loop toggle, and automation features.
"""

import random
from typing import Optional, Callable, Dict, Any
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QPushButton, QComboBox, QCheckBox,
                             QGroupBox, QSpinBox)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import Qt, QTimer, QUrl, Signal
import qtawesome as qta


class MixerTrackWidget(QWidget):
    """Individual track widget for the mixer panel."""
    
    track_removed = Signal(str)  # Emitted when track is removed
    
    def __init__(self, sound_file: str, parent=None):
        super().__init__(parent)
        self.sound_file = sound_file
        self.player = None
        self.audio_output = None
        self.automation_timer = QTimer()
        self.playback_timer = QTimer()
        
        # Track state
        self.volume_direction = 1  # 1 for increasing, -1 for decreasing
        self.original_volume = 50
        self.is_playing = False
        
        self._setup_audio()
        self._setup_ui()
        self._setup_timers()
        # Set default loop
        self._on_loop_toggled(self.loop_check.isChecked())

    def _setup_audio(self):
        """Initialize QMediaPlayer and audio output."""
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        # Set the sound file
        url = QUrl.fromLocalFile(self.sound_file)
        self.player.setSource(url)
        
        # Set initial volume
        self.audio_output.setVolume(0.5)
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Track info
        from pathlib import Path
        sound_name = Path(self.sound_file).stem
        
        info_group = QGroupBox(self.tr(sound_name))
        info_layout = QVBoxLayout(info_group)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel(self.tr("Volume:")))
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.volume_slider.setTickInterval(10)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("50%")
        self.volume_label.setFixedWidth(40)
        volume_layout.addWidget(self.volume_label)
        
        info_layout.addLayout(volume_layout)
        
        # Controls row
        controls_layout = QHBoxLayout()

        # Play/Stop button
        self.play_icon = qta.icon('fa5s.play', color='#555555')
        self.stop_icon = qta.icon('fa5s.stop', color='#555555')
        self.play_button = QPushButton(self.play_icon, self.tr(" Play"))
        self.play_button.clicked.connect(self._toggle_playback)
        controls_layout.addWidget(self.play_button)
        
        # Remove button
        remove_icon = qta.icon('fa5s.times', color='#e74c3c')
        self.remove_button = QPushButton(remove_icon, "")
        self.remove_button.setFixedWidth(40)
        self.remove_button.clicked.connect(self._remove_track)
        controls_layout.addWidget(self.remove_button)
        
        info_layout.addLayout(controls_layout)
        
        # Automation controls
        automation_group = QGroupBox(self.tr("Automation"))
        automation_layout = QVBoxLayout(automation_group)
        
        # Volume automation
        vol_auto_layout = QHBoxLayout()
        self.volume_auto_check = QCheckBox(self.tr("Volume Auto"))
        self.volume_auto_check.toggled.connect(self._on_volume_auto_toggled)
        vol_auto_layout.addWidget(self.volume_auto_check)
        
        # Automation speed
        vol_auto_layout.addWidget(QLabel(self.tr("Speed:")))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems([self.tr("Slow (10s)"), self.tr("Medium (5s)"), self.tr("Fast (2s)")])
        self.speed_combo.setCurrentIndex(1)  # Default to Medium
        self.speed_combo.currentTextChanged.connect(self._on_speed_changed)
        vol_auto_layout.addWidget(self.speed_combo)
        
        automation_layout.addLayout(vol_auto_layout)
        
        # Playback automation
        playback_layout = QHBoxLayout()
        self.playback_auto_check = QCheckBox(self.tr("Auto Playback"))
        self.playback_auto_check.toggled.connect(self._on_playback_auto_toggled)
        playback_layout.addWidget(self.playback_auto_check)
        
        # Interval type
        self.interval_combo = QComboBox()
        self.interval_combo.addItems([self.tr("Fixed"), self.tr("Random")])
        self.interval_combo.setCurrentIndex(0)
        playback_layout.addWidget(self.interval_combo)
        
        # Interval settings
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 120)
        self.interval_spin.setValue(20)
        self.interval_spin.setSuffix(self.tr("s"))
        playback_layout.addWidget(QLabel(self.tr("Every")))
        playback_layout.addWidget(self.interval_spin)
        
        automation_layout.addLayout(playback_layout)

        # Loop toggle
        self.loop_check = QCheckBox(self.tr("Loop"))
        self.loop_check.setChecked(True)
        self.loop_check.toggled.connect(self._on_loop_toggled)
        automation_layout.addWidget(self.loop_check)

        layout.addWidget(info_group)
        layout.addWidget(automation_group)
        
        # Set touch-friendly sizes
        self.setMinimumWidth(300)
        for child in self.findChildren(QPushButton):
            child.setMinimumHeight(35)
        for child in self.findChildren(QComboBox):
            child.setMinimumHeight(30)
    
    def _setup_timers(self):
        """Set up automation timers."""
        self.automation_timer.timeout.connect(self._update_volume_automation)
        self.playback_timer.timeout.connect(self._handle_auto_playback)
    
    def _on_volume_changed(self, value: int):
        """Handle volume slider changes."""
        if self.audio_output:
            self.audio_output.setVolume(value / 100.0)
        self.volume_label.setText(f"{value}%")
        
        if not self.volume_auto_check.isChecked():
            self.original_volume = value
    
    def _on_loop_toggled(self, checked: bool):
        """Handle loop toggle."""
        if checked and self.playback_auto_check.isChecked():
            # Disable auto playback when loop is enabled
            self.playback_auto_check.setChecked(False)
        if self.player:
            self.player.setLoops(-1 if checked else 1)
    
    def _toggle_playback(self):
        """Toggle playback state."""
        if not self.player:
            return
            
        if self.is_playing:
            self.player.pause()
            self.play_button.setText(self.tr("▶️ Play"))
            self.is_playing = False
        else:
            self.player.play()
            self.play_button.setText(self.tr("⏸️ Pause"))
            self.is_playing = True
    
    def _remove_track(self):
        """Remove this track from the mixer."""
        if self.player:
            self.player.stop()
        self.track_removed.emit(self.sound_file)
    
    def _on_volume_auto_toggled(self, checked: bool):
        """Handle volume automation toggle."""
        if checked:
            self.original_volume = self.volume_slider.value()
            interval = self._get_automation_interval()
            self.automation_timer.start(interval)
        else:
            self.automation_timer.stop()
            # Restore original volume
            self.volume_slider.setValue(self.original_volume)
    
    def _on_speed_changed(self):
        """Handle automation speed change."""
        if self.volume_auto_check.isChecked():
            interval = self._get_automation_interval()
            self.automation_timer.start(interval)
    
    def _get_automation_interval(self) -> int:
        """Get automation interval in milliseconds based on speed selection."""
        speed_index = self.speed_combo.currentIndex()
        intervals = [10000, 5000, 2000]  # Slow, Medium, Fast
        return intervals[speed_index]
    
    def _update_volume_automation(self):
        """Update volume during automation."""
        current_volume = self.volume_slider.value()
        
        # Smooth volume changes between 20% and 80%
        new_volume = current_volume + (self.volume_direction * 5)
        
        if new_volume >= 80:
            new_volume = 80
            self.volume_direction = -1
        elif new_volume <= 20:
            new_volume = 20
            self.volume_direction = 1
        
        self.volume_slider.setValue(new_volume)
    
    def _on_playback_auto_toggled(self, checked: bool):
        """Handle playback automation toggle."""
        if checked:
            self._schedule_next_playback()
            # Disable loop when auto playback is active
            self.loop_check.setChecked(False)
        else:
            self.playback_timer.stop()
    
    def _schedule_next_playback(self):
        """Schedule the next automatic playback."""
        if not self.playback_auto_check.isChecked():
            return
            
        interval_seconds = self.interval_spin.value()
        
        if self.interval_combo.currentText() == "Random":
            # Random interval between half and double the specified value
            min_interval = max(1, interval_seconds // 2)
            max_interval = interval_seconds * 2
            interval_seconds = random.randint(min_interval, max_interval)
        
        self.playback_timer.start(interval_seconds * 1000)
    
    def _handle_auto_playback(self):
        """Handle automatic playback trigger."""
        if not self.is_playing:
            self._toggle_playback()
        
        # Schedule next playback
        self._schedule_next_playback()

    def _start_playback(self):
        """Start playback."""
        if not self.player:
            return
            
        self.player.play()
        self.play_button.setText(self.tr(" Pause"))
        self.play_button.setIcon(self.stop_icon)
        self.is_playing = True

    def _stop_playback(self):
        """Stop playback."""
        if not self.player:
            return
            
        self.player.pause()
        self.play_button.setText(self.tr(" Play"))
        self.play_button.setIcon(self.play_icon)
        self.is_playing = False

    def get_state(self) -> Dict[str, Any]:
        """Get current track state for session saving."""
        return {
            "sound_file": self.sound_file,
            "volume": self.volume_slider.value(),
            "loop": self.loop_check.isChecked(),
            "volume_auto": self.volume_auto_check.isChecked(),
            "playback_auto": self.playback_auto_check.isChecked(),
            "speed": self.speed_combo.currentIndex(),
            "interval_type": self.interval_combo.currentIndex(),
            "interval": self.interval_spin.value()
        }
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """Restore track state from session data."""
        self.volume_slider.setValue(state.get("volume", 50))
        self.loop_check.setChecked(state.get("loop", True))
        self.volume_auto_check.setChecked(state.get("volume_auto", False))
        self.playback_auto_check.setChecked(state.get("playback_auto", False))
        self.speed_combo.setCurrentIndex(state.get("speed", 1))
        self.interval_combo.setCurrentIndex(state.get("interval_type", 0))
        self.interval_spin.setValue(state.get("interval", 20))

        # Apply loop setting to player
        self._on_loop_toggled(self.loop_check.isChecked())
    
    def stop(self):
        """Stop playback and cleanup."""
        if self.player:
            try:
                self.player.stop()
            except RuntimeError:
                pass  # Player might be already deleted
        self.automation_timer.stop()
        self.playback_timer.stop()
