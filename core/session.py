"""
Session Management Module

Handles saving and loading mixer sessions to/from JSON files.
Preserves track states, file paths, volume levels, and automation settings.
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from PySide6.QtCore import QObject, Signal as pyqtSignal


class SessionManager(QObject):
    """Manages saving and loading of mixer sessions."""
    
    session_loaded = pyqtSignal(dict)
    session_saved = pyqtSignal(str)
    
    def __init__(self, sessions_dir: str = "sessions"):
        super().__init__()
        self.sessions_dir = Path(sessions_dir)
        self._ensure_sessions_dir()
    
    def _ensure_sessions_dir(self) -> None:
        """Ensure the sessions directory exists."""
        self.sessions_dir.mkdir(exist_ok=True)
    
    def save_session(self, session_data: Dict[str, Any], filename: str) -> bool:
        """
        Save the current mixer session to a JSON file.
        
        Args:
            session_data: Dictionary containing session information
            filename: Name of the session file (without extension)
        
        Returns:
            True if save was successful, False otherwise
        """
        try:
            session_file = self.sessions_dir / f"{filename}.json"
            
            # Ensure we have a valid session structure
            session = {
                "version": "1.0",
                "tracks": session_data.get("tracks", []),
                "metadata": session_data.get("metadata", {
                    "name": filename,
                    "created": "",
                    "description": ""
                })
            }
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session, f, indent=2, ensure_ascii=False)
            
            self.session_saved.emit(str(session_file))
            return True
            
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def load_session(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Load a mixer session from a JSON file.
        
        Args:
            filename: Name of the session file (with or without extension)
        
        Returns:
            Session data dictionary if successful, None otherwise
        """
        try:
            if not filename.endswith('.json'):
                filename = f"{filename}.json"
            
            session_file = self.sessions_dir / filename
            
            if not session_file.exists():
                print(f"Session file not found: {session_file}")
                return None
            
            with open(session_file, 'r', encoding='utf-8') as f:
                session = json.load(f)
            
            # Validate session structure
            if "tracks" not in session:
                print("Invalid session format: missing 'tracks' key")
                return None
            
            self.session_loaded.emit(session)
            return session
            
        except json.JSONDecodeError as e:
            print(f"Error parsing session file: {e}")
            return None
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
    
    def list_sessions(self) -> List[str]:
        """Get a list of available session files."""
        try:
            return [f.stem for f in self.sessions_dir.glob("*.json")]
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []
    
    def delete_session(self, filename: str) -> bool:
        """
        Delete a session file.
        
        Args:
            filename: Name of the session file (with or without extension)
        
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            if not filename.endswith('.json'):
                filename = f"{filename}.json"
            
            session_file = self.sessions_dir / filename
            
            if session_file.exists():
                session_file.unlink()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    def get_session_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Get basic information about a session without loading all tracks.
        
        Args:
            filename: Name of the session file
        
        Returns:
            Dictionary with session metadata if successful, None otherwise
        """
        try:
            session = self.load_session(filename)
            if session:
                return {
                    "name": session.get("metadata", {}).get("name", filename),
                    "track_count": len(session.get("tracks", [])),
                    "metadata": session.get("metadata", {})
                }
            return None
        except Exception:
            return None
