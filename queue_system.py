import eel
import pyttsx3
import threading
import winsound
import time
import os
import subprocess
import sys
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

def get_app_path(*parts):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, *parts)

# Initialize Eel for both interfaces
eel.init(get_app_path('web'))

# Flag to prevent infinite loops of spawning
os.environ['DTI_OPERATOR_RUNNING'] = 'true'

# Client backend URL
CLIENT_URL = "http://localhost:8002"

# Operator shutdown server (allows client window to close operator too)
OPERATOR_SHUTDOWN_PORT = 8003

# Operator settings state
teller_name = "Operator"
operator_theme = "light"
audio_alerts_enabled = True
teller_gender = "male"
announcement_volume = 50


class OperatorShutdownHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self):
        if self.path != '/api/shutdown':
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()
            return

        self.send_response(200)
        self._send_cors_headers()
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        try:
            self.wfile.write(json.dumps({"status": "shutting_down"}).encode())
        except Exception:
            pass

        def _exit_soon():
            time.sleep(0.2)
            os._exit(0)

        threading.Thread(target=_exit_soon, daemon=True).start()

    def log_message(self, format, *args):
        pass


def start_operator_shutdown_server():
    try:
        server = HTTPServer(('localhost', OPERATOR_SHUTDOWN_PORT), OperatorShutdownHandler)
        print(f"[OK] Operator shutdown server started on port {OPERATOR_SHUTDOWN_PORT}")
        server.serve_forever()
    except Exception as e:
        print(f"[WARN] Could not start operator shutdown server: {e}")

# Launch client display if not already running
def start_client_display():
    """Start client display in a separate process"""
    try:
        if getattr(sys, 'frozen', False):
            client_target = os.path.join(os.path.dirname(sys.executable), 'client_display.exe')
            command = [client_target]
        else:
            client_target = os.path.join(os.path.dirname(__file__), 'client_display.py')
            command = [sys.executable, client_target]

        subprocess.Popen(
            command,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0,
            env={**os.environ, 'DTI_OPERATOR_SPAWNED': 'true'}
        )
        print("[OK] Client Display started in separate window")
    except Exception as e:
        print(f"[WARN] Could not start client display: {e}")

# Start client display on startup (unless this instance was spawned by client)
if not os.environ.get('DTI_CLIENT_SPAWNED'):
    threading.Thread(target=start_client_display, daemon=True).start()
    time.sleep(2)  # Give client time to start

def sync_to_client(action, data):
    """Send updates to client display via HTTP in background thread"""
    def send():
        try:
            print(f"→ Syncing {action}: {data}")
            response = requests.post(f"{CLIENT_URL}/api/update", json={"action": action, "data": data}, timeout=2)
            print(f"[OK] Sync successful (status {response.status_code})")
        except Exception as e:
            print(f"[ERROR] Sync failed: {e}")
    
    # Send in background thread to not block operator
    threading.Thread(target=send, daemon=True).start()


def push_settings_to_client():
    sync_to_client("settings_state", {
        "teller_name": teller_name,
        "teller_gender": teller_gender,
        "theme": operator_theme,
        "audio_announcements": call_announcements_enabled,
        "sound_effects": sound_effects_enabled,
        "volume": announcement_volume,
        "online": True,
    })


@eel.expose
def set_sound_effects(enabled):
    global sound_effects_enabled
    global audio_alerts_enabled
    sound_effects_enabled = bool(enabled)
    audio_alerts_enabled = sound_effects_enabled and call_announcements_enabled
    print(f"[OK] Sound effects {'enabled' if sound_effects_enabled else 'disabled'}")
    push_settings_to_client()


@eel.expose
def set_call_announcements(enabled):
    global call_announcements_enabled
    global audio_alerts_enabled
    call_announcements_enabled = bool(enabled)
    audio_alerts_enabled = sound_effects_enabled and call_announcements_enabled
    print(f"[OK] Call announcements {'enabled' if call_announcements_enabled else 'disabled'}")
    push_settings_to_client()


@eel.expose
def set_audio_alerts(enabled):
    global sound_effects_enabled, call_announcements_enabled, audio_alerts_enabled
    audio_alerts_enabled = bool(enabled)
    sound_effects_enabled = audio_alerts_enabled
    call_announcements_enabled = audio_alerts_enabled
    print(f"[OK] Audio alerts {'enabled' if audio_alerts_enabled else 'disabled'}")
    push_settings_to_client()


@eel.expose
def set_bn_teller(name):
    global teller_name
    teller_name = (name or "").strip() or "Operator"
    print(f"[OK] Teller name set to: {teller_name}")
    push_settings_to_client()


@eel.expose
def set_teller_gender(gender):
    global teller_gender
    teller_gender = "female" if str(gender).lower() == "female" else "male"
    print(f"[OK] Teller gender set to: {teller_gender}")
    push_settings_to_client()


@eel.expose
def set_announcement_volume(volume):
    global announcement_volume
    try:
        announcement_volume = max(0, min(100, int(volume)))
    except Exception:
        announcement_volume = 50
    print(f"[OK] Announcement volume set to: {announcement_volume}")
    push_settings_to_client()


@eel.expose
def set_theme(theme):
    global operator_theme
    operator_theme = "dark" if str(theme).lower() == "dark" else "light"
    print(f"[OK] Operator theme set to: {operator_theme}")
    push_settings_to_client()


def speak_by_gender(text):
    if teller_gender == "female":
        speak_female(text)
    else:
        speak(text)


def play_sound_effect():
    if not sound_effects_enabled:
        return

    errors = []

    try:
        winsound.Beep(1200, 250)
        return
    except Exception:
        errors.append("Beep failed")

    try:
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
        return
    except Exception as e:
        errors.append(f"MessageBeep failed: {e}")

    try:
        winsound.PlaySound(
            "SystemAsterisk",
            winsound.SND_ALIAS | winsound.SND_SYNC
        )
    except Exception as e:
        errors.append(f"PlaySound(SystemAsterisk) failed: {e}")
        if errors:
            print(f"Sound effect error: {'; '.join(errors)}")

# Global queue state
reg_count = 0
pri_count = 0
waiting_count = 0  # Track waiting customers
mode = "REGULAR"
is_speaking = False
current_video_id = ""  # Track current video being displayed
sound_effects_enabled = True
call_announcements_enabled = True

# Track all eel JavaScript instances for both operator and client windows
operator_objects = []
client_objects = []


def speak(text, maintain_client_pause=False):
    """Speak immediately without delay - Male voice for regular clients"""
    global is_speaking
    if not call_announcements_enabled:
        return
    try:
        is_speaking = True
        sync_to_client("announcement_state", {"active": True})
        # Try to disable buttons on both interfaces
        try:
            eel.disableButtons()
        except:
            pass
        
        temp_engine = pyttsx3.init()
        temp_engine.setProperty("rate", 180)  # Faster but still clear
        temp_engine.setProperty("volume", max(0.0, min(1.0, announcement_volume / 100.0)))
        
        # Set male voice (default)
        voices = temp_engine.getProperty('voices')
        if voices:
            temp_engine.setProperty('voice', voices[0].id)  # Male voice
        
        temp_engine.say(text)
        temp_engine.runAndWait()
        
        # Properly shut down this temporary instance
        temp_engine.stop()
        del temp_engine
        
        is_speaking = False
        if not maintain_client_pause:
            time.sleep(0.5)  # Small delay before re-enabling
            sync_to_client("announcement_state", {"active": False})
            try:
                eel.enableButtons()
            except:
                pass
        
    except Exception as e:
        print(f"Speech error: {e}")
        is_speaking = False
        if not maintain_client_pause:
            sync_to_client("announcement_state", {"active": False})
            try:
                eel.enableButtons()
            except:
                pass


def speak_female(text, maintain_client_pause=False):
    """Speak immediately without delay - Female voice for priority clients"""
    global is_speaking
    if not call_announcements_enabled:
        return
    try:
        is_speaking = True
        sync_to_client("announcement_state", {"active": True})
        try:
            eel.disableButtons()
        except:
            pass
        
        temp_engine = pyttsx3.init()
        temp_engine.setProperty("rate", 180)  # Faster but still clear
        temp_engine.setProperty("volume", max(0.0, min(1.0, announcement_volume / 100.0)))
        
        # Set female voice
        voices = temp_engine.getProperty('voices')
        if len(voices) > 1:
            temp_engine.setProperty('voice', voices[1].id)  # Female voice
        
        temp_engine.say(text)
        temp_engine.runAndWait()
        
        # Properly shut down this temporary instance
        temp_engine.stop()
        del temp_engine
        
        is_speaking = False
        if not maintain_client_pause:
            time.sleep(0.5)  # Small delay before re-enabling
            sync_to_client("announcement_state", {"active": False})
            try:
                eel.enableButtons()
            except:
                pass
        
    except Exception as e:
        print(f"Speech error: {e}")
        is_speaking = False
        if not maintain_client_pause:
            sync_to_client("announcement_state", {"active": False})
            try:
                eel.enableButtons()
            except:
                pass


@eel.expose
def toggle_mode():
    global mode
    mode = "PRIORITY" if mode == "REGULAR" else "REGULAR"
    # Update operator UI
    current_num = f"R-{reg_count:03d}" if mode == "REGULAR" else f"P-{pri_count:03d}"
    try:
        eel.updateDisplay(current_num, f"{mode} CLIENT", "")
    except:
        pass
    
    # Sync to client display
    sync_to_client("update_display", {
        "ticket": current_num,
        "status": f"{mode} CLIENT"
    })
    
    # Announce the mode change with appropriate voice
    if mode == "PRIORITY":
        speak_female("Priority client")
    else:
        speak("Regular client")


@eel.expose
def get_next_ticket():
    global reg_count, pri_count, waiting_count, mode
    
    if mode == "REGULAR":
        reg_count += 1
        ticket = f"R-{reg_count:03d}"
        queue_type = "Regular"
    else:
        pri_count += 1
        ticket = f"P-{pri_count:03d}"
        queue_type = "Priority"

    if waiting_count > 0:
        waiting_count -= 1

    # Update operator interface
    try:
        eel.updateDisplay(ticket, f"{mode} CLIENT", "")
        eel.updateWaitingCount(waiting_count)
    except:
        pass
    
    # Sync to client display
    sync_to_client("update_display", {
        "ticket": ticket,
        "status": f"{mode} CLIENT",
        "waiting": waiting_count
    })
    
    # Announce the ticket
    formatted_ticket = ticket.replace("-", " ")
    announcement = f"ATTENTION. {queue_type} client number {formatted_ticket}, please come to the counter."

    play_sound_effect()
    
    if queue_type == "Priority":
        speak_female(announcement, maintain_client_pause=True)
        speak_female(announcement, maintain_client_pause=True)
    else:
        speak(announcement, maintain_client_pause=True)
        speak(announcement, maintain_client_pause=True)

    sync_to_client("announcement_state", {"active": False})
    try:
        eel.enableButtons()
    except:
        pass


@eel.expose
def add_waiting_customer():
    """Add a customer to waiting queue (called from operator panel)"""
    global waiting_count
    waiting_count += 1
    try:
        eel.updateWaitingCount(waiting_count)
    except:
        pass
    
    # Sync to client
    sync_to_client("update_waiting", {"waiting": waiting_count})


@eel.expose
def set_display_video(video_id):
    """Set video to display on client screen"""
    global current_video_id
    print(f"set_display_video called with: {video_id}")
    current_video_id = video_id
    try:
        print(f"Calling eel.updateClientVideo({video_id})")
        eel.updateClientVideo(video_id)
    except Exception as e:
        print(f"Error calling eel.updateClientVideo: {e}")
    
    # Sync to client
    print(f"Syncing to client port 8002 with video_id: {video_id}")
    sync_to_client("update_video", {"video_id": video_id})


@eel.expose
def reset_queue():
    global reg_count, pri_count, mode, waiting_count
    reg_count = 0
    pri_count = 0
    waiting_count = 0
    mode = "REGULAR"
    try:
        eel.updateDisplay("R-000", "REGULAR CLIENT", "")
        eel.updateWaitingCount(0)
    except:
        pass
    
    # Sync to client
    sync_to_client("reset", {
        "ticket": "R-000",
        "status": "REGULAR CLIENT",
        "waiting": 0,
        "video": ""
    })
    
    speak("Queue has been reset")


# Start the Operator Panel
if __name__ == '__main__':
    print("=" * 60)
    print("DTI LAGUNA QUEUE MANAGEMENT SYSTEM")
    print("=" * 60)
    print("\nOperator Panel: http://localhost:8000")
    print("Client Display: http://localhost:8001")
    print("\nMake sure to run client_display.py in a separate terminal")
    print("for the customer-facing display!")
    print("\n" + "=" * 60)
    
    # Start shutdown server (so closing either window closes both)
    threading.Thread(target=start_operator_shutdown_server, daemon=True).start()
    time.sleep(0.2)

    # Start operator panel with splash screen
    eel.start('loading_operator.html', mode='chrome', port=8000, size=(450, 450))