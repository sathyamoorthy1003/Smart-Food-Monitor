
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import threading
import time
import serial
import json
import database
import os

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

# Configuration
SERIAL_PORT = "COM3"  # Default, user might need to change
BAUD_RATE = 9600
UPLOAD_FOLDER = '../frontend/uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Global latest data
latest_sensor_data = {
    "gas": 0,
    "temp": 0.0,
    "hum": 0.0,
    "status": "FRESH"
}

def read_from_serial():
    global latest_sensor_data
    ser = None
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to {SERIAL_PORT}")
    except Exception as e:
        print(f"Serial Error: {e}. Running in Mock Mode.")
    
    while True:
        if ser and ser.is_open:
            try:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    if line.startswith("{") and line.endswith("}"):
                        data = json.loads(line)
                        latest_sensor_data = data
                        # Log to DB occasionally (e.g., every 10th reading or time-based) could be added here
                        # For now, we rely on the client or polling logic to save
            except Exception as e:
                print(f"Serial Read Error: {e}")
        time.sleep(1)

# Start Serial Thread
threading.Thread(target=read_from_serial, daemon=True).start()

@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/data')
def get_data():
    return jsonify(latest_sensor_data)

@app.route('/api/slots')
def get_slots():
    slots = database.get_all_slots()
    return jsonify(slots)

@app.route('/api/upload/<int:slot_id>', methods=['POST'])
def upload_image(slot_id):
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        filename = f"slot_{slot_id}_{int(time.time())}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Save relative path for frontend
        rel_path = f"uploads/{filename}"
        database.update_slot_image(slot_id, rel_path)
        
        return jsonify({"success": True, "image_path": rel_path})

if __name__ == '__main__':
    database.init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
