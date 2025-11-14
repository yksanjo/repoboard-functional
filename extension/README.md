# RepoBoard Browser Extension

Chrome/Firefox extension to access RepoBoard directly from GitHub.

## Features

- Browse curated boards from extension popup
- See similar repositories on GitHub repo pages
- Quick access to RepoBoard from any GitHub page

## Installation

### Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `extension` folder
5. Click the RepoBoard icon in toolbar
6. Set your API URL (default: http://localhost:8000)

### Firefox

1. Open Firefox and go to `about:debugging`
2. Click "This Firefox"
3. Click "Load Temporary Add-on"
4. Select `manifest.json` from the extension folder

## Usage

1. Click the RepoBoard icon in your browser toolbar
2. Set your RepoBoard API URL (if not using localhost:8000)
3. Browse curated boards
4. Visit any GitHub repository to see similar repos in the sidebar

## Development

To build icons, create:
- `icons/icon16.png` (16x16)
- `icons/icon48.png` (48x48)
- `icons/icon128.png` (128x128)

Or use a tool like:
```bash
# Generate icons from a single image
convert icon.png -resize 16x16 icons/icon16.png
convert icon.png -resize 48x48 icons/icon48.png
convert icon.png -resize 128x128 icons/icon128.png
```

