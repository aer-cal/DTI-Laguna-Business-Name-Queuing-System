# DTI Laguna Queue Management System - Dual Display Setup

## Overview
The system now runs **two separate windows**:
- **Operator Panel** (Port 8000): Control panel with buttons and statistics
- **Client Display** (Port 8001): Customer-facing display with ticket information

## Features

### Operator Panel Features
- **Queue Controls**: Switch between Regular/Priority modes
- **Ticket Management**: Call next customer with automatic announcements
- **Statistics Dashboard**: View Regular/Priority served counts and waiting customers
- **Media Display**: Embed YouTube videos for waiting room entertainment
- **Waiting Queue Tracker**: Add/track customers waiting
- **Reset Function**: Clear all queue data

### Client Display Features
- **Large Ticket Display**: Current serving ticket number (huge font)
- **Status Indicator**: Shows if "REGULAR" or "PRIORITY" client being served
- **Waiting Queue Bar**: Visual progress bar showing customers waiting
- **Time & Date**: Live clock and date display
- **Weather Information**: Current temperature in Laguna
- **DTI Contact Details**: Phone, email, Facebook, and address information

## Running the System

### Option 1: Automatic (Recommended)
Double-click `run.bat` - This automatically starts BOTH windows:
1. Operator Panel launches first
2. Client Display opens automatically in a separate window
3. Both windows ready to use!

### Option 2: Run Either Window Individually
**Start from Operator Panel:**
```bash
python queue_system.py
```
→ Automatically launches Client Display in a separate window

**Start from Client Display:**
```bash
python client_display.py
```
→ Automatically launches Operator Panel in a separate window

## Local PC App Setup

If you want this to behave like a desktop app on the teller PC, the cleanest setup is:

1. Keep the project folder on the PC, preferably in a fixed local path.
2. Run `install_desktop_shortcut.bat` once, or use `build_windows_app.ps1` if you are packaging a deployment, and the desktop shortcut will be created automatically.
3. Open the app from the shortcut named `DTI Laguna Queue System`.
4. Leave the PC connected to the internet for YouTube and weather updates.

The shortcut points to a quiet Windows launcher, so the app opens without showing the command window and only runs when someone clicks the shortcut.

This keeps the current Python app unchanged while making it feel like a normal local desktop program.

### Option 3: Manual (Both in separate terminals)
**Terminal 1 (Operator Panel):**
```bash
python queue_system.py
```

**Terminal 2 (Client Display):**
```bash
python client_display.py
```

## Setup Instructions

1. **Operator Panel** - Runs on your teller/operator computer
   - Close or minimize to the side of your main monitor
   - Use buttons to control queue flow

2. **Client Display** - Runs on customer-facing monitor/screen
   - Display at full screen on a separate monitor, TV, or projector
   - Shows current ticket, wait status, time, weather, and DTI info

## Using the System

### For Operators:
1. **Switch Mode**: Click "SWITCH REGULAR/PRIORITY" button to toggle between Regular and Priority queues
2. **Add Waiting Customer**: Click "ADD WAITING" when a new customer arrives
3. **Call Next**: Click "NEXT TICKET" to serve the next customer
   - Announcement plays automatically
   - Wait bar updates on client display
4. **Reset**: Click "RESET QUEUE" to clear everything (confirmation required)
5. **Video**: Paste YouTube URL or Video ID to display videos on client screen

### For Customers:
- Watch the large ticket display to see current ticket number
- Monitor the status pill (REGULAR/PRIORITY)
- Check the waiting bar to see how many customers are ahead
- View DTI contact info and weather while waiting

## Display Recommendations

**Operator Panel:**
- Laptop or desktop screen (1920x1440 recommended)
- Keep on teller's desk for control

**Client Display:**
- Large monitor, TV, or projector
- 1920x1080 or higher recommended
- Mount high and visible to all waiting customers

## Customization

### Changing Display Size
Edit the `size=` parameter in Python files:
- `queue_system.py`: Operator panel size
- `client_display.py`: Client display size

### Changing Ports
Default ports are 8000 (operator) and 8001 (client).
Modify the `port=` parameter if these are already in use.

### Styling
Edit the Tailwind CSS classes in:
- `web/index.html` (operator interface)
- `web/client.html` (client display)
- `web/styles.css` (shared styles)

## Troubleshooting

**Both windows not appearing?**
- Check if ports 8000 and 8001 are available
- Try running each script individually in separate terminals

**Video not loading?**
- Ensure internet connection is available
- Try just the video ID instead of full YouTube URL
- Format: `dQw4w9WgXcQ` or `https://www.youtube.com/watch?v=dQw4w9WgXcQ`

**No sound?**
- Check system volume on operator computer
- Ensure speakers are connected and working
- Check microphone/audio output settings in Windows

**Port already in use?**
- Change the port number in `queue_system.py` and `client_display.py`
- Or close other applications using those ports

**Shortcut did not appear?**
- Make sure the project folder is not blocked by OneDrive sync or permissions
- Run `install_desktop_shortcut.bat` again as the current Windows user, or rerun `build_windows_app.ps1` for packaged deployments
- Confirm the desktop shortcut points to the app launcher inside this folder

## Technical Details

- **Backend**: Python with Eel framework
- **Frontend**: HTML5, Tailwind CSS
- **Browser**: Chrome (Chromium-based)
- **Audio**: Text-to-speech with pyttsx3
- **Data**: In-memory queue management
