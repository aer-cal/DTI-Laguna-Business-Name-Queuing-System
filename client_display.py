"""
DTI Laguna Queue System - Client Display Window
Runs on separate port to show customer information
"""
import eel
import os
import subprocess
import sys
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

def get_app_path(*parts):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, *parts)

# Initialize Eel for client display
eel.init(get_app_path('web'))

# Flag to prevent infinite loops
os.environ['DTI_CLIENT_RUNNING'] = 'true'

# Store current state
client_state = {
    "ticket": "R-000",
    "status": "REGULAR CLIENT",
    "waiting": 0,
    "video_id": "",
    "announcement_active": False,
    "bn_teller": "",
    "bn_teller_gender": "unknown",
    "theme": "light",
    "sound_effects": True,
    "audio_announcements": True,
    "volume": 50,
    "online": True,
}

# HTTP Request Handler for receiving updates
class UpdateHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        # Allow the operator UI (8000) and client UI (8001) to call this server (8002)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        # CORS preflight
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/shutdown':
            # Close the client_display process (and thus the client window)
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
            return

        if self.path == '/api/update':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
                action = data.get('action')
                update_data = data.get('data', {})
                print(f"[RECV] /api/update action={action} data={update_data}")
                
                # Handle different action types
                if action == 'update_display':
                    client_state['ticket'] = update_data.get('ticket', 'R-000')
                    client_state['status'] = update_data.get('status', 'REGULAR CLIENT')
                    if 'waiting' in update_data:
                        client_state['waiting'] = int(update_data.get('waiting', client_state.get('waiting', 0)))
                    try:
                        eel.updateClientDisplay(client_state['ticket'], client_state['status'])
                        eel.updateWaitingCount(client_state['waiting'])
                    except Exception as e:
                        print(f"Error calling updateClientDisplay: {e}")
                
                elif action == 'update_waiting':
                    client_state['waiting'] = update_data.get('waiting', 0)
                    try:
                        eel.updateWaitingCount(client_state['waiting'])
                    except Exception as e:
                        print(f"Error calling updateWaitingCount: {e}")
                
                elif action == 'update_video':
                    client_state['video_id'] = update_data.get('video_id', '')
                    print(f"[OK] Received video update: {client_state['video_id']}")
                    try:
                        eel.updateClientVideo(client_state['video_id'])
                    except Exception as e:
                        print(f"Error calling updateClientVideo: {e}")
                
                elif action == 'reset':
                    client_state['ticket'] = update_data.get('ticket', 'R-000')
                    client_state['status'] = update_data.get('status', 'REGULAR CLIENT')
                    client_state['waiting'] = update_data.get('waiting', 0)
                    client_state['video_id'] = update_data.get('video_id', update_data.get('video', ''))
                    try:
                        eel.updateClientDisplay(client_state['ticket'], client_state['status'])
                        eel.updateWaitingCount(client_state['waiting'])
                        eel.updateClientVideo(client_state['video_id'])
                    except Exception as e:
                        print(f"Error calling reset functions: {e}")

                elif action == 'announcement_state':
                    client_state['announcement_active'] = bool(update_data.get('active', False))
                    try:
                        eel.setAnnouncementActive(client_state['announcement_active'])
                    except Exception as e:
                        print(f"Error calling setAnnouncementActive: {e}")

                elif action == 'set_bn_teller':
                    # Update BN Teller name on client display and store in state
                    name = update_data.get('name', '')
                    gender = update_data.get('gender', 'unknown')
                    theme = update_data.get('theme', client_state.get('theme', 'light'))
                    client_state['bn_teller'] = name
                    client_state['bn_teller_gender'] = gender
                    client_state['theme'] = theme
                    print(f"[OK] Received BN Teller name: {name}, gender: {gender}, theme: {theme}")
                    try:
                        eel.updateBnTellerName(name, gender)
                        eel.updateTheme(theme)
                    except Exception as e:
                        print(f"Error calling updateBnTellerName: {e}")

                elif action == 'settings_state':
                    client_state['bn_teller'] = update_data.get('teller_name', client_state.get('bn_teller', ''))
                    client_state['bn_teller_gender'] = update_data.get('teller_gender', client_state.get('bn_teller_gender', 'unknown'))
                    client_state['theme'] = update_data.get('theme', client_state.get('theme', 'light'))
                    client_state['sound_effects'] = bool(update_data.get('sound_effects', client_state.get('sound_effects', True)))
                    client_state['audio_announcements'] = bool(update_data.get('audio_announcements', client_state.get('audio_announcements', True)))
                    client_state['volume'] = int(update_data.get('volume', client_state.get('volume', 50)))
                    client_state['online'] = bool(update_data.get('online', True))
                    try:
                        eel.updateSettingsState(
                            client_state['bn_teller'],
                            client_state['bn_teller_gender'],
                            client_state['theme'],
                            client_state['sound_effects'],
                            client_state['audio_announcements'],
                            client_state['volume'],
                            client_state['online']
                        )
                        eel.updateBnTellerName(client_state['bn_teller'], client_state['bn_teller_gender'])
                        eel.updateTheme(client_state['theme'])
                    except Exception as e:
                        print(f"Error calling updateSettingsState: {e}")

                elif action == 'update_theme':
                    theme = update_data.get('theme', 'light')
                    client_state['theme'] = theme
                    print(f"[OK] Received theme update: {theme}")
                    try:
                        eel.updateTheme(theme)
                    except Exception as e:
                        print(f"Error calling updateTheme: {e}")
                
                # Send success response
                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode())
            except Exception as e:
                print(f"Error processing update: {e}")
                self.send_response(400)
                self._send_cors_headers()
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()
    
    def do_GET(self):
        if self.path == '/api/state':
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(client_state).encode())
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress HTTP server logs

# Start HTTP server in background thread
def start_http_server():
    """Start HTTP server to receive updates from operator"""
    try:
        server = HTTPServer(('localhost', 8002), UpdateHandler)
        print("[OK] Client update server started on port 8002")
        server.serve_forever()
    except Exception as e:
        print(f"[WARN] Could not start HTTP server: {e}")

# Start HTTP server before Eel
http_thread = threading.Thread(target=start_http_server, daemon=True)
http_thread.start()
time.sleep(0.5)

# Launch operator panel if not already running
def start_operator_panel():
    """Start operator panel in a separate process"""
    try:
        if getattr(sys, 'frozen', False):
            operator_target = os.path.join(os.path.dirname(sys.executable), 'queue_system.exe')
            command = [operator_target]
        else:
            operator_target = os.path.join(os.path.dirname(__file__), 'queue_system.py')
            command = [sys.executable, operator_target]

        subprocess.Popen(
            command,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0,
            env={**os.environ, 'DTI_CLIENT_SPAWNED': 'true'}
        )
        print("[OK] Operator Panel started in separate window")
    except Exception as e:
        print(f"[WARN] Could not start operator panel: {e}")

# Start operator panel on startup (unless this instance was spawned by operator)
if not os.environ.get('DTI_OPERATOR_SPAWNED'):
    threading.Thread(target=start_operator_panel, daemon=True).start()
    time.sleep(1)  # Give operator time to start

# Start the client display on port 8001
if __name__ == '__main__':
    print("Starting Client Display Window...")
    print("Listening for updates from Operator Panel...")
    eel.start('loading.html', mode='chrome', port=8001, size=(450, 450))

