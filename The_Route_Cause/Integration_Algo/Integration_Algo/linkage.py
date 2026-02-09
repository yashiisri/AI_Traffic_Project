import cv2
import time
import requests
import json
import numpy as np #

# Replace with Gov.in camera's RTSP URL
RTSP_URL = "rtsp://username:password@192.168.1.100:554/stream_path" 
API_URL = "http://127.0.0.1:8000/traffic_data" 

def run_agent():
    cap = cv2.VideoCapture(RTSP_URL)

    if not cap.isOpened():
        print(f"ERROR: Could not open RTSP stream at {RTSP_URL}. Exiting.")
        return

    print(f"Successfully connected to RTSP stream: {RTSP_URL}")

    frame_count = 0
    while True:
        ret, frame = cap.read() 

        if not ret:
            print("ERROR: Failed to grab frame, stream may have ended or disconnected. Attempting to reconnect...")
            cap.release()
            time.sleep(5)
            cap = cv2.VideoCapture(RTSP_URL)
            if not cap.isOpened():
                print("ERROR: Reconnection failed. Exiting.")
                break
            else:
                print("Reconnected successfully.")
                continue


        frame_count += 1

        simulated_detections = {
            "cars": np.random.randint(5, 20),
            "pedestrians": np.random.randint(0, 5),
            "motorcycles": np.random.randint(0, 3),
            "emergency_vehicle_detected": np.random.rand() < 0.01 
        }

        signal_decision = "green_lane_1" if simulated_detections["cars"] > 10 else "green_lane_2"

        payload = {
            "camera_id": "intersection_A", 
            "timestamp": time.time(),
            "detections": simulated_detections,
            "signal_command": signal_decision
        }

        try:
            response = requests.post(API_URL, json=payload)
            response.raise_for_status() 
            
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Could not send data to FastAPI: {e}")

        time.sleep(0.1) 

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_agent()