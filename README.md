# Ambient Sound Mixer

A modular desktop application for creating relaxing ambient soundscapes by layering audio files with volume control, loop behavior, and automation features.

## Features

- **Sound Library Panel**: Browse sounds organized by categories (Nature, City, Water, etc.)
- **Mixer Panel**: Add tracks with individual controls for volume, looping, and automation
- **Volume Automation**: Automatic volume changes with adjustable speed (Slow/Medium/Fast)
- **Playback Automation**: Auto-play sounds at fixed or random intervals
- **Session Management**: Save and load complete mixer configurations as JSON files
- **Touch-Friendly UI**: Large, responsive controls suitable for touch screens
- **Multiple Audio Support**: Play multiple sounds simultaneously using PyQt6.QtMultimedia

## Requirements

- Python 3.10 or higher
- PyQt6
- No external audio libraries required (uses PyQt6.QtMultimedia only)

## Installation

1. Clone or extract the project to your desired location
2. Install PyQt6:
   ```bash
   pip install PyQt6
   ```

## Usage

### Running the Application

```bash
python main.py
```

### Adding Sounds

1. Place your audio files (.mp3, .wav, .ogg) in the `sounds/` directory, organized by categories:
   ```
   sounds/
   ├── animals/
   │   ├── birds.mp3
   │   └── dog.mp3
   ├── nature/
   │   ├── forest.wav
   │   └── rain.mp3
   ├── urban/
   │   └── traffic.ogg
   └── rain/
       └── thunderstorm.mp3
   ```

2. Launch the application - it will automatically scan the sounds directory
3. Click "Add to Mixer" next to any sound to add it to your mix

### Using the Mixer

Each track in the mixer includes:
- **Volume Slider**: Adjust individual track volume
- **Loop Toggle**: Enable/disable continuous looping
- **Volume Automation**: Automatically varies volume up and down
- **Playback Automation**: Auto-play at specified intervals
- **Speed Control**: Adjust automation speed (Slow ≈10s, Medium ≈5s, Fast ≈2s)
- **Interval Settings**: Set fixed or random playback intervals

### Session Management

- **Save Session**: Save your current mixer configuration including all tracks and settings
- **Load Session**: Restore a previously saved session
- Sessions are saved as JSON files in the `sessions/` directory

## Project Structure

```
ambient_mixer/
├── main.py                 # Application entry point
├── ui/
│   ├── main_window.py      # Main application window
│   └── mixer_track_widget.py  # Individual track controls
├── core/
│   ├── sound_manager.py    # Sound file discovery and management
│   └── session.py          # Session save/load functionality
├── sounds/                 # Sound files organized by category
├── sessions/               # Saved session files
└── README.md              # This documentation
```

## Keyboard Shortcuts

- **Ctrl+S**: Save session
- **Ctrl+O**: Load session
- **Ctrl+Q**: Quit application
- **F5**: Refresh sound library

## Technical Details

- **Audio Engine**: PyQt6.QtMultimedia.QMediaPlayer
- **Supported Formats**: .mp3, .wav, .ogg files
- **GUI Framework**: PyQt6
- **State Persistence**: JSON format
- **Automation**: QTimer-based volume and playback control

## Creating Custom Sounds

To add your own sounds:

1. Create folders in the `sounds/` directory for your categories
2. Add audio files (.mp3, .wav, .ogg) to the appropriate folders
3. Restart the application or click "Refresh Library"

## Troubleshooting

### No Sounds Appear
- Ensure audio files (.mp3, .wav, .ogg) are in the `sounds/` directory
- Check that the directory structure follows the category format
- Click "Refresh Library" to rescan

### Audio Issues
- Verify audio files are valid and playable
- Check system audio settings
- Ensure no other applications are blocking audio

### Session Loading Issues
- Verify the session JSON file exists and is valid
- Ensure all referenced sound files still exist
- Check the console for error messages

## Development

The application is designed to be modular:
- **UI components** are in the `ui/` directory
- **Core functionality** is in the `core/` directory
- **State management** uses JSON for easy inspection and editing

## License

This project is provided as-is for educational and personal use.
