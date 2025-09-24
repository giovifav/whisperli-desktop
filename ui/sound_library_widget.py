"""
Sound Library Widget

A tree view widget that displays sound files organized by category.
"""

import os
from typing import Dict, List, Optional, Any

from PySide6.QtWidgets import (QTreeView, QVBoxLayout,
                             QWidget, QAbstractItemView, QMenu)
from PySide6.QtCore import Qt, QDir, Signal, QModelIndex, QPoint, QSize
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction, QIcon, QFont, QColor
import qtawesome as qta

# Mapping of categories to qtawesome icon names (using Font Awesome 5 free icons)
CATEGORY_ICONS = {
    "animals": "fa5s.paw",
    "nature": "fa5s.tree",
    "noise": "fa5s.volume-up",
    "places": "fa5s.building",
    "rain": "fa5s.cloud-rain",
    "things": "fa5s.cogs",
    "transport": "fa5s.car",
    "urban": "fa5s.city",
    "walking": "fa5s.walking",
    "User Sounds": "fa5s.user",
}


class SoundLibraryWidget(QWidget):
    """Widget that displays sound files in a tree view by category."""
    
    sound_selected = Signal(str)  # Emitted when a sound is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sound_manager = None
        self._setup_ui()

    def tr(self, text: str) -> str:
        """Translate text using QApplication's translate method."""
        return QApplication.translate("SoundLibraryWidget", text)
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tree view
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        
        self._apply_styling()
        
        # Set up model
        self.model = QStandardItemModel()
        self.tree_view.setModel(self.model)
        
        layout.addWidget(self.tree_view)
    
    def _apply_styling(self):
        """Set up the tree view."""
        self.tree_view.setSelectionBehavior(QTreeView.SelectionBehavior.SelectRows)
        self.tree_view.setSelectionMode(QTreeView.SelectionMode.SingleSelection)
    
    def set_sound_manager(self, sound_manager):
        """Set the sound manager and connect signals."""
        self.sound_manager = sound_manager
        self.sound_manager.sounds_updated.connect(self._update_tree)
        self._update_tree()
    
    def _update_tree(self):
        """Update the tree view with current sounds from sound manager."""
        if not self.sound_manager:
            return
            
        self.model.clear()
        
        # Get categories and sort them
        categories = self.sound_manager.get_categories()
        categories.sort()
        
        for category in categories:
            # Create category item with icon
            # Translate category name if it's "User Sounds"
            display_category = self.tr(category) if category == "User Sounds" else category
            category_item = QStandardItem(display_category)
            category_item.setData(None, Qt.ItemDataRole.UserRole)  # No path for categories
            
            # Set icon for category using qtawesome
            if category in CATEGORY_ICONS:
                try:
                    # For Material Design Icons, use 'mdi.' prefix
                    icon_name = CATEGORY_ICONS[category]
                    if icon_name.startswith('mdi6.'):
                        # Remove the '6' as it's not needed in the icon name
                        icon_name = 'mdi.' + icon_name[5:]
                    
                    # Create the icon with the correct name and colors
                    # Note: icons will be styled by the overall theme
                    icon = qta.icon(icon_name,
                                 color='#555555',  # Default color (will be overridden by theme)
                                 color_active='#4CAF50')  # Green for active state
                    category_item.setIcon(icon)
                except Exception as e:
                    print(self.tr(f"Error loading icon '{CATEGORY_ICONS[category]}' for {category}: {str(e)}"))
            
            # Add sound files as children
            sounds = self.sound_manager.get_sounds_in_category(category)
            for sound_path in sounds:
                # Removed Path import, using os.path.splitext for stem
                sound_name = os.path.splitext(os.path.basename(sound_path))[0]
                sound_item = QStandardItem(sound_name)
                sound_item.setData(sound_path, Qt.ItemDataRole.UserRole)  # Store full path
                category_item.appendRow(sound_item)
            
            self.model.appendRow(category_item)
        
        # Collapse all categories by default
        self.tree_view.collapseAll()
    
    def _on_item_double_clicked(self, index: QModelIndex):
        """Handle double-click on an item."""
        item = self.model.itemFromIndex(index)
        if not item:
            return
            
        sound_path = item.data(Qt.ItemDataRole.UserRole)
        if sound_path:  # Only emit if it's a sound file (not a category)
            self.sound_selected.emit(sound_path)
    
    def _show_context_menu(self, position: QPoint):
        """Show context menu for sound items."""
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return
            
        item = self.model.itemFromIndex(index)
        sound_path = item.data(Qt.ItemDataRole.UserRole)
        
        if not sound_path:  # Category item
            return
            
        menu = QMenu(self)
        
        # Add to new track
        add_new_action = QAction(self.tr("Add to New Track"), self)
        add_new_action.triggered.connect(lambda: self.sound_selected.emit(sound_path))
        menu.addAction(add_new_action)
        
        # Show menu
        menu.exec(self.tree_view.viewport().mapToGlobal(position))
