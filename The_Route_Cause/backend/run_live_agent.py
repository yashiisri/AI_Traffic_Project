# # import cv2
# # import numpy as np
# # import time
# # import json
# # import os
# # import sys
# # from ultralytics import YOLO
# # import asyncio
# # import websockets
# # from q_learning_agent import AdaptiveQLearningAgent
# # from optimization_engine import OptimizationEngine
# # import threading
# # import queue

# # # =================================================================================
# # # === CONFIGURATION                                                             ===
# # # =================================================================================
# # VIDEO_FILE = "my_video.mp4"; SAVED_AGENT_MODEL_PATH = "traffic_agent"
# # LANE_POLYGONS = {
# #     "Northbound": np.array([[2124, 487], [2830, 514], [2103, 1657], [2829, 1592]], np.int32),
# #     "Southbound": np.array([[966, 1568], [1380, 1574], [1467, 2048], [830, 2085]], np.int32),
# #     "Eastbound": np.array([[0,0], [1,1], [2,2], [3,3]], np.int32),
# #     "Westbound": np.array([[0,0], [1,1], [2,2], [3,3]], np.int32),
# # }
# # LANE_NAMES_ORDER = ["Northbound", "Southbound", "Eastbound", "Westbound"] 
# # CROSSWALK_POLYGONS = { "crosswalk_1": np.array([[1900, 1000], [2100, 1000], [2100, 1200], [1900, 1200]], np.int32) }
# # TRAFFIC_LIGHT_POSITIONS = { "Northbound": (150, 250), "Southbound": (150, 450), "Eastbound": (150, 650), "Westbound": (150, 850) }
# # GREEN_LIGHT_DURATION = 8.0; YELLOW_LIGHT_DURATION = 1.5; EMERGENCY_GREEN_DURATION = 5.0 
# # EMERGENCY_CLEARING_TIME = 2.0; STARVATION_THRESHOLD = 30.0; MAX_QUEUE_LENGTH = 30
# # PEDESTRIAN_THRESHOLD = 10; PEDESTRIAN_CROSSING_DURATION = 15
# # YOLO_MODEL = 'yolov8s.pt'; CONF_THRESHOLD = 0.3
# # PERSON_CLASS_ID = 0; VEHICLE_CLASSES = [2, 3, 5, 7]
# # ALL_DETECTABLE_CLASSES = [PERSON_CLASS_ID] + VEHICLE_CLASSES
# # MAX_VEHICLES_PER_LANE = 40; # In the configuration section of run_live_agent.py

# # # Get the backend URL from an environment variable, with a fallback for local testing.
# # WEBSOCKET_URI = os.getenv("BACKEND_WEBSOCKET_URL", "ws://localhost:8000/ws/ai")

# # # =================================================================================
# # # === NETWORKING THREAD                                                         ===
# # # =================================================================================
# # def websocket_thread(data_queue: queue.Queue, stop_event: threading.Event):
# #     """
# #     Handles all asynchronous WebSocket communication in a dedicated thread.
# #     """
# #     async def sender():
# #         try:
# #             async with websockets.connect(WEBSOCKET_URI) as websocket:
# #                 print("✅ Successfully connected to backend WebSocket.")
# #                 while not stop_event.is_set():
# #                     try:
# #                         # Get data from the queue without blocking the event loop
# #                         output_data = data_queue.get_nowait()
# #                         if output_data:
# #                             await websocket.send(json.dumps(output_data))
# #                     except queue.Empty:
# #                         await asyncio.sleep(0.01) # Yield control
# #                     except websockets.exceptions.ConnectionClosed:
# #                         print("🔴 Backend connection was lost.")
# #                         break
# #         except Exception as e:
# #             print(f"🔴 WebSocket connection failed: {e}")
# #         finally:
# #             stop_event.set()

# #     asyncio.run(sender())

# # # =================================================================================
# # # === MAIN SCRIPT (GUI and AI Logic)                                            ===
# # # =================================================================================
# # def run_live_inference(data_queue: queue.Queue, stop_event: threading.Event):
# #     """
# #     Handles all OpenCV, YOLO, and AI logic in the main thread.
# #     """
# #     def draw_single_traffic_light(frame, position, status):
# #         x, y = position; radius = 35; color = (0, 0, 255)
# #         if status == "GREEN": color = (0, 255, 0)
# #         elif status == "YELLOW": color = (0, 255, 255)
# #         cv2.circle(frame, (x, y), radius, color, -1); cv2.circle(frame, (x, y), radius, (50, 50, 50), 3)

# #     agent = AdaptiveQLearningAgent(action_size=4); agent.load_model(SAVED_AGENT_MODEL_PATH)
# #     engine = OptimizationEngine(starvation_threshold=STARVATION_THRESHOLD)
# #     model = YOLO(YOLO_MODEL)
# #     cap = cv2.VideoCapture(VIDEO_FILE)
# #     if not cap.isOpened(): sys.exit(f"\n[ERROR] Could not open video file '{VIDEO_FILE}'.")
# #     fps = cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 30
    
# #     signal_state = "GREEN"; current_green_lane_index = 0; next_green_lane_index = -1
# #     state_timer = 0.0; pedestrian_crossing_timer = 0
# #     emergency_override_state = None; lane_to_clear_index = -1; emergency_target_lane = -1
    
# #     print("\n[INFO] LIVE MODE: Running agent with SUPERVISOR logic... Press 'q' to exit.")
    
# #     while not stop_event.is_set():
# #         ret, frame = cap.read()
# #         if not ret: cap.set(cv2.CAP_PROP_POS_FRAMES, 0); continue

# #         # --- Object Detection & State Machine Logic (Unchanged) ---
# #         results = model(frame, verbose=False)
# #         lane_counts = {name: 0 for name in LANE_NAMES_ORDER}; pedestrian_count = 0
# #         for box in results[0].boxes:
# #             class_id = int(box.cls[0].item())
# #             if class_id not in ALL_DETECTABLE_CLASSES or box.conf[0].item() < CONF_THRESHOLD: continue
# #             x1, y1, x2, y2 = [int(coord) for coord in box.xyxy[0].tolist()]; center_point = ((x1 + x2) // 2, (y1 + y2) // 2)
# #             if class_id == PERSON_CLASS_ID:
# #                 for poly in CROSSWALK_POLYGONS.values():
# #                     if cv2.pointPolygonTest(poly, center_point, False) >= 0: pedestrian_count += 1; cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2); break
# #             else:
# #                 for name, poly in LANE_POLYGONS.items():
# #                     if cv2.pointPolygonTest(poly, center_point, False) >= 0: lane_counts[name] += 1; cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2); break
        
# #         key = cv2.waitKey(1) & 0xFF
# #         manual_emergency_lane = -1
# #         if key == ord('1'): manual_emergency_lane = 0
# #         elif key == ord('2'): manual_emergency_lane = 1
# #         elif key == ord('3'): manual_emergency_lane = 2
# #         elif key == ord('4'): manual_emergency_lane = 3
# #         if key == ord('q'): stop_event.set(); break
        
# #         state_timer += 1/fps; decision_reason, send_update_to_backend = "Observing", False
        
# #         if manual_emergency_lane != -1 and emergency_override_state is None:
# #             if not (current_green_lane_index == manual_emergency_lane and signal_state == "GREEN"):
# #                 emergency_override_state, lane_to_clear_index, state_timer, emergency_target_lane = "CLEARING_YELLOW", current_green_lane_index, 0.0, manual_emergency_lane
# #                 decision_reason, send_update_to_backend = f"MANUAL EMERGENCY: Clearing for {LANE_NAMES_ORDER[manual_emergency_lane]}", True
# #         if emergency_override_state is not None:
# #             if emergency_override_state == "CLEARING_YELLOW":
# #                 signal_state = "YELLOW"
# #                 if state_timer >= YELLOW_LIGHT_DURATION: emergency_override_state, state_timer, decision_reason, send_update_to_backend = "CLEARING_ALL_RED", 0.0, "EMERGENCY: All Red", True
# #             elif emergency_override_state == "CLEARING_ALL_RED":
# #                 signal_state = "ALL_RED"
# #                 if state_timer >= EMERGENCY_CLEARING_TIME: emergency_override_state, current_green_lane_index, signal_state, state_timer, decision_reason, send_update_to_backend = "ACTIVE", emergency_target_lane, "GREEN", 0.0, f"EMERGENCY: Green for {LANE_NAMES_ORDER[emergency_target_lane]}", True
# #             elif emergency_override_state == "ACTIVE" and state_timer >= EMERGENCY_GREEN_DURATION:
# #                 emergency_override_state, signal_state, state_timer, decision_reason, send_update_to_backend = None, "YELLOW", 0.0, "Emergency cleared", True
# #         else:
# #             if signal_state == "GREEN" and (state_timer >= GREEN_LIGHT_DURATION or any(lane_counts[name] >= MAX_QUEUE_LENGTH for i, name in enumerate(LANE_NAMES_ORDER) if i != current_green_lane_index)):
# #                 signal_state, state_timer = "YELLOW", 0.0
# #             elif signal_state == "YELLOW" and state_timer >= YELLOW_LIGHT_DURATION:
# #                 counts_ordered = [lane_counts[n] for n in LANE_NAMES_ORDER]; norm_counts = [c/MAX_VEHICLES_PER_LANE for c in counts_ordered]; observation = np.array(norm_counts + [current_green_lane_index/3, 0])
# #                 agent_recommendation = agent.choose_action(observation, training=False)
# #                 context = {'emergency_active': False, 'emergency_lane': None, 'pedestrian_count': pedestrian_count}
# #                 final_action, decision_reason, _ = engine.optimize_action(lane_counts, LANE_NAMES_ORDER[current_green_lane_index], agent_recommendation, context)
# #                 current_green_lane_index, signal_state, state_timer, send_update_to_backend = final_action, "GREEN", 0.0, True
# #                 engine.last_service_times[LANE_NAMES_ORDER[current_green_lane_index]] = time.time(); engine.update_performance(final_action, -sum(lane_counts.values()), False, context)
        
# #         output_data = {"timestamp": time.time(), "lane_counts": lane_counts, "pedestrian_count": pedestrian_count, "decision": {"reason": decision_reason}, "signal_state": {"active_direction": LANE_NAMES_ORDER[current_green_lane_index] if signal_state not in ["PEDESTRIAN", "ALL_RED"] else signal_state, "state": signal_state, "timer": int(state_timer)}}
# #         data_queue.put(output_data)

# #         # --- FULL VISUALIZATION PANEL (RESTORED) ---
# #         overlay = frame.copy(); cv2.rectangle(overlay, (frame.shape[1] - 700, 0), (frame.shape[1], 800), (0, 0, 0), -1)
# #         alpha = 0.6; frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
# #         for i, (name, pos) in enumerate(TRAFFIC_LIGHT_POSITIONS.items()):
# #             status = "RED"
# #             if emergency_override_state == "CLEARING_YELLOW" and i == lane_to_clear_index: status = "YELLOW"
# #             elif emergency_override_state == "CLEARING_ALL_RED": status = "RED"
# #             elif emergency_override_state == "ACTIVE" and i == current_green_lane_index: status = "GREEN"
# #             elif i == current_green_lane_index and emergency_override_state is None: status = signal_state
# #             draw_single_traffic_light(frame, pos, status)
# #             cv2.putText(frame, name, (pos[0] + 50, pos[1] + 15), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 3)

# #         y_pos, x_pos = 50, frame.shape[1] - 650
# #         status_text = f"{LANE_NAMES_ORDER[current_green_lane_index]}: {signal_state}"
# #         if emergency_override_state is not None: status_text = f"EMERGENCY OVERRIDE ({emergency_override_state})"
        
# #         cv2.putText(frame, "SYSTEM STATUS", (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3); y_pos += 60
# #         cv2.putText(frame, f"Current State: {status_text}", (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2); y_pos += 40
# #         cv2.putText(frame, f"Elapsed Time: {int(state_timer)}s", (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2); y_pos += 60
# #         cv2.putText(frame, "Live Vehicle Counts", (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3); y_pos += 50
# #         for name, count in lane_counts.items():
# #             cv2.putText(frame, f"- {name}: {count}", (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2); y_pos += 40
# #         cv2.putText(frame, "Optimization Engine Stats", (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3); y_pos += 50
# #         engine_stats = engine.get_optimization_stats()
# #         cv2.putText(frame, f"- Avg Reward: {engine_stats['average_reward']}", (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2); y_pos += 40
# #         cv2.putText(frame, f"- Total Decisions: {engine_stats['total_decisions']}", (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2); y_pos += 40
# #         cv2.putText(frame, f"Last Decision: {decision_reason}", (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        
# #         cv2.imshow('AI Traffic System - Final Demo', frame)

# #     print("[INFO] Video processing loop finished.")
# #     cap.release(); cv2.destroyAllWindows()

# # if __name__ == '__main__':
# #     data_queue = queue.Queue()
# #     stop_event = threading.Event()

# #     network_thread = threading.Thread(target=websocket_thread, args=(data_queue, stop_event))
# #     network_thread.start()

# #     print("\n[INFO] Main thread (GUI) started.")
# #     try:
# #         run_live_inference(data_queue, stop_event)
# #     except Exception as e:
# #         print(f"An error occurred in the main thread: {e}")
# #     finally:
# #         print("[INFO] Main thread is shutting down.")
# #         stop_event.set()
# #         network_thread.join()



# import cv2
# import numpy as np
# import time
# import json
# import os
# import sys
# from ultralytics import YOLO
# import asyncio
# import websockets
# from q_learning_agent import AdaptiveQLearningAgent
# from optimization_engine import OptimizationEngine
# import threading
# import queue

# # =================================================================================
# # === CONFIGURATION                                                             ===
# # =================================================================================
# VIDEO_FILE = "my_video.mp4"
# SAVED_AGENT_MODEL_PATH = "traffic_agent"
# # LANE_POLYGONS = {
# #     "Northbound": np.array([[2124, 487], [2830, 514], [2103, 1657], [2829, 1592]], np.int32),
# #     "Southbound": np.array([[966, 1568], [1380, 1574], [1467, 2048], [830, 2085]], np.int32),
# #     "Eastbound": np.array([[0,0], [1,1], [2,2], [3,3]], np.int32),
# #     "Westbound": np.array([[0,0], [1,1], [2,2], [3,3]], np.int32),
# # }
# LANE_POLYGONS = {
#     "Northbound": np.array([
#         [600, 120],   # top-left of northbound lane
#         [1350, 120],  # top-right
#         [1200, 380],  # mid-right
#         [700, 380]    # mid-left
#     ], np.int32),

#     "Southbound": np.array([
#         [650, 600],   # mid-left area
#         [1200, 600],  # mid-right
#         [1300, 900],  # bottom-right
#         [550, 900]    # bottom-left
#     ], np.int32),

#     "Eastbound": np.array([
#         [1450, 350],  # right-top
#         [1900, 350],  # far-right
#         [1900, 700],  # far-right bottom
#         [1450, 700]   # right-bottom
#     ], np.int32),

#     "Westbound": np.array([
#         [0, 350],     # left side
#         [450, 350],
#         [450, 700],
#         [0, 700]
#     ], np.int32),
# }

# LANE_NAMES_ORDER = ["Northbound", "Southbound", "Eastbound", "Westbound"]
# CROSSWALK_POLYGONS = { "crosswalk_1": np.array([[1900, 1000], [2100, 1000], [2100, 1200], [1900, 1200]], np.int32) }
# TRAFFIC_LIGHT_POSITIONS = { "Northbound": (150, 250), "Southbound": (150, 450), "Eastbound": (150, 650), "Westbound": (150, 850) }
# GREEN_LIGHT_DURATION = 8.0
# YELLOW_LIGHT_DURATION = 1.5
# EMERGENCY_GREEN_DURATION = 5.0
# EMERGENCY_CLEARING_TIME = 2.0
# STARVATION_THRESHOLD = 30.0
# MAX_QUEUE_LENGTH = 30
# PEDESTRIAN_THRESHOLD = 10
# PEDESTRIAN_CROSSING_DURATION = 15
# YOLO_MODEL = 'yolov8s.pt'
# CONF_THRESHOLD = 0.3
# PERSON_CLASS_ID = 0
# VEHICLE_CLASSES = [2, 3, 5, 7]
# ALL_DETECTABLE_CLASSES = [PERSON_CLASS_ID] + VEHICLE_CLASSES
# MAX_VEHICLES_PER_LANE = 40

# # Get the backend URL from an environment variable, with a fallback for local testing.
# WEBSOCKET_URI = os.getenv("BACKEND_WEBSOCKET_URL", "ws://localhost:8000/ws/ai")

# # =================================================================================
# # === NETWORKING THREAD                                                         ===
# # =================================================================================
# def websocket_thread(data_queue: queue.Queue, stop_event: threading.Event):
#     """
#     Handles WebSocket communication in a dedicated thread.
#     NOTE: On connection failure we DON'T set stop_event, so the main loop keeps running.
#     """
#     async def sender():
#         try:
#             async with websockets.connect(WEBSOCKET_URI) as websocket:
#                 print("✅ Successfully connected to backend WebSocket.")
#                 while not stop_event.is_set():
#                     try:
#                         # non-blocking get
#                         output_data = data_queue.get_nowait()
#                         if output_data:
#                             await websocket.send(json.dumps(output_data))
#                     except queue.Empty:
#                         await asyncio.sleep(0.01)
#                     except websockets.exceptions.ConnectionClosed:
#                         print("🔴 Backend connection was lost.")
#                         break
#         except Exception as e:
#             # Don't stop the whole program on websocket error; just report it.
#             print(f"🔴 WebSocket connection failed: {e}")
#             # return quietly; the main thread continues
#             return

#     # Run the async sender once (if it fails, we don't retry here; could add retry logic)
#     try:
#         asyncio.run(sender())
#     except Exception as e:
#         print(f"🔴 Async websocket runner error: {e}")

# # =================================================================================
# # === MAIN SCRIPT (GUI and AI Logic)                                            ===
# # =================================================================================
# def run_live_inference(data_queue: queue.Queue, stop_event: threading.Event):
#     """
#     Handles OpenCV, YOLO, and AI logic in the main thread.
#     """
#     def draw_single_traffic_light(frame, position, status):
#         x, y = position
#         radius = 35
#         color = (0, 0, 255)
#         if status == "GREEN":
#             color = (0, 255, 0)
#         elif status == "YELLOW":
#             color = (0, 255, 255)
#         cv2.circle(frame, (x, y), radius, color, -1)
#         cv2.circle(frame, (x, y), radius, (50, 50, 50), 3)

#     # Initialize agent and engine
#     agent = AdaptiveQLearningAgent(action_size=4)
#     try:
#         agent.load_model(SAVED_AGENT_MODEL_PATH)
#     except Exception:
#         print("[WARN] Could not load agent model (continuing with untrained agent).")

#     engine = OptimizationEngine(starvation_threshold=STARVATION_THRESHOLD)

#     # Load YOLO model
#     try:
#         model = YOLO(YOLO_MODEL)
#     except Exception as e:
#         print(f"[ERROR] Could not load YOLO model '{YOLO_MODEL}': {e}")
#         model = None

#     cap = cv2.VideoCapture(VIDEO_FILE)
#     if not cap.isOpened():
#         # Provide helpful message; do not call sys.exit() here because we want graceful handling in main.
#         raise RuntimeError(f"\n[ERROR] Could not open video file '{VIDEO_FILE}'. Make sure the file exists in the backend folder and is accessible.")

#     fps = cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 30
#     wait_ms = max(1, int(1000 / fps))

#     signal_state = "GREEN"
#     current_green_lane_index = 0
#     next_green_lane_index = -1
#     state_timer = 0.0
#     pedestrian_crossing_timer = 0
#     emergency_override_state = None
#     lane_to_clear_index = -1
#     emergency_target_lane = -1

#     paused = False

#     print("\n[INFO] LIVE MODE: Running agent with SUPERVISOR logic... Press 'q' to exit, 'p' to pause.")

#     while not stop_event.is_set():
#         if paused:
#             key = cv2.waitKey(100) & 0xFF
#             if key == ord('p'):
#                 paused = False
#             elif key == ord('q'):
#                 stop_event.set()
#                 break
#             else:
#                 continue

#         ret, frame = cap.read()
#         if not ret:
#             # Reached end or read error. Try to loop the video with a small sleep so the window doesn't flash.
#             print("[INFO] Reached end of video or cannot read frame. Rewinding to start...")
#             cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
#             time.sleep(0.5)
#             continue

#         # --- Object Detection & State Machine Logic ---
#         try:
#             if model:
#                 results = model(frame, verbose=False)
#             else:
#                 results = [type("R", (), {"boxes": []})()]  # dummy if model missing
#         except Exception as e:
#             print(f"[WARN] YOLO inference failed on frame: {e}")
#             results = [type("R", (), {"boxes": []})()]

#         lane_counts = {name: 0 for name in LANE_NAMES_ORDER}
#         pedestrian_count = 0

#         for box in results[0].boxes:
#             try:
#                 class_id = int(box.cls[0].item())
#             except Exception:
#                 continue
#             if class_id not in ALL_DETECTABLE_CLASSES or box.conf[0].item() < CONF_THRESHOLD:
#                 continue
#             x1, y1, x2, y2 = [int(coord) for coord in box.xyxy[0].tolist()]
#             center_point = ((x1 + x2) // 2, (y1 + y2) // 2)
#             if class_id == PERSON_CLASS_ID:
#                 for poly in CROSSWALK_POLYGONS.values():
#                     if cv2.pointPolygonTest(poly, center_point, False) >= 0:
#                         pedestrian_count += 1
#                         cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
#                         break
#             else:
#                 for name, poly in LANE_POLYGONS.items():
#                     if cv2.pointPolygonTest(poly, center_point, False) >= 0:
#                         lane_counts[name] += 1
#                         cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                         break

#         # Input handling
#         key = cv2.waitKey(wait_ms) & 0xFF
#         manual_emergency_lane = -1
#         if key == ord('1'): manual_emergency_lane = 0
#         elif key == ord('2'): manual_emergency_lane = 1
#         elif key == ord('3'): manual_emergency_lane = 2
#         elif key == ord('4'): manual_emergency_lane = 3
#         elif key == ord('p'):
#             paused = True
#         elif key == ord('q'):
#             stop_event.set()
#             break

#         state_timer += 1.0 / fps
#         decision_reason, send_update_to_backend = "Observing", False

#         # Emergency/manual override handling
#         if manual_emergency_lane != -1 and emergency_override_state is None:
#             if not (current_green_lane_index == manual_emergency_lane and signal_state == "GREEN"):
#                 emergency_override_state, lane_to_clear_index, state_timer, emergency_target_lane = "CLEARING_YELLOW", current_green_lane_index, 0.0, manual_emergency_lane
#                 decision_reason, send_update_to_backend = f"MANUAL EMERGENCY: Clearing for {LANE_NAMES_ORDER[manual_emergency_lane]}", True

#         if emergency_override_state is not None:
#             if emergency_override_state == "CLEARING_YELLOW":
#                 signal_state = "YELLOW"
#                 if state_timer >= YELLOW_LIGHT_DURATION:
#                     emergency_override_state, state_timer, decision_reason, send_update_to_backend = "CLEARING_ALL_RED", 0.0, "EMERGENCY: All Red", True
#             elif emergency_override_state == "CLEARING_ALL_RED":
#                 signal_state = "ALL_RED"
#                 if state_timer >= EMERGENCY_CLEARING_TIME:
#                     emergency_override_state, current_green_lane_index, signal_state, state_timer, decision_reason, send_update_to_backend = "ACTIVE", emergency_target_lane, "GREEN", 0.0, f"EMERGENCY: Green for {LANE_NAMES_ORDER[emergency_target_lane]}", True
#             elif emergency_override_state == "ACTIVE" and state_timer >= EMERGENCY_GREEN_DURATION:
#                 emergency_override_state, signal_state, state_timer, decision_reason, send_update_to_backend = None, "YELLOW", 0.0, "Emergency cleared", True
#         else:
#             if signal_state == "GREEN" and (state_timer >= GREEN_LIGHT_DURATION or any(lane_counts[name] >= MAX_QUEUE_LENGTH for i, name in enumerate(LANE_NAMES_ORDER) if i != current_green_lane_index)):
#                 signal_state, state_timer = "YELLOW", 0.0
#             elif signal_state == "YELLOW" and state_timer >= YELLOW_LIGHT_DURATION:
#                 counts_ordered = [lane_counts[n] for n in LANE_NAMES_ORDER]
#                 norm_counts = [c / MAX_VEHICLES_PER_LANE for c in counts_ordered]
#                 observation = np.array(norm_counts + [current_green_lane_index / 3, 0])
#                 try:
#                     agent_recommendation = agent.choose_action(observation, training=False)
#                 except Exception:
#                     agent_recommendation = 0
#                 context = {'emergency_active': False, 'emergency_lane': None, 'pedestrian_count': pedestrian_count}
#                 final_action, decision_reason, _ = engine.optimize_action(lane_counts, LANE_NAMES_ORDER[current_green_lane_index], agent_recommendation, context)
#                 current_green_lane_index, signal_state, state_timer, send_update_to_backend = final_action, "GREEN", 0.0, True
#                 engine.last_service_times[LANE_NAMES_ORDER[current_green_lane_index]] = time.time()
#                 engine.update_performance(final_action, -sum(lane_counts.values()), False, context)

#         output_data = {
#             "timestamp": time.time(),
#             "lane_counts": lane_counts,
#             "pedestrian_count": pedestrian_count,
#             "decision": {"reason": decision_reason},
#             "signal_state": {
#                 "active_direction": LANE_NAMES_ORDER[current_green_lane_index] if signal_state not in ["PEDESTRIAN", "ALL_RED"] else signal_state,
#                 "state": signal_state,
#                 "timer": int(state_timer)
#             }
#         }
#         # Non-blocking put (if queue full it will discard the oldest)
#         try:
#             data_queue.put_nowait(output_data)
#         except queue.Full:
#             pass

#         # --- VISUALIZATION PANEL ---
#         PANEL_WIDTH = 350
#         PANEL_X = frame.shape[1] - PANEL_WIDTH - 200 
#         overlay = frame.copy()
#         cv2.rectangle(overlay, (frame.shape[1] - 700, 0), (frame.shape[1], 800), (0, 0, 0), -1)
#         # Narrower sidebar: 350px instead of 700px
      

#         alpha = 0.6
#         frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

#         for i, (name, pos) in enumerate(TRAFFIC_LIGHT_POSITIONS.items()):
#             status = "RED"
#             if emergency_override_state == "CLEARING_YELLOW" and i == lane_to_clear_index:
#                 status = "YELLOW"
#             elif emergency_override_state == "CLEARING_ALL_RED":
#                 status = "RED"
#             elif emergency_override_state == "ACTIVE" and i == current_green_lane_index:
#                 status = "GREEN"
#             elif i == current_green_lane_index and emergency_override_state is None:
#                 status = signal_state
#             draw_single_traffic_light(frame, pos, status)
#             cv2.putText(frame, name, (pos[0] + 50, pos[1] + 15), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 3)

#         y_pos, x_pos = 50, frame.shape[1] - 1000
#         status_text = f"{LANE_NAMES_ORDER[current_green_lane_index]}: {signal_state}"
#         if emergency_override_state is not None:
#             status_text = f"EMERGENCY OVERRIDE ({emergency_override_state})"

#         cv2.putText(frame, "SYSTEM STATUS", (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3); y_pos += 60
#         cv2.putText(frame, f"Current State: {status_text}", (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2); y_pos += 40
#         cv2.putText(frame, f"Elapsed Time: {int(state_timer)}s", (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2); y_pos += 60
#         cv2.putText(frame, "Live Vehicle Counts", (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3); y_pos += 50
#         for name, count in lane_counts.items():
#             cv2.putText(frame, f"- {name}: {count}", (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2); y_pos += 40
#         cv2.putText(frame, "Optimization Engine Stats", (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3); y_pos += 50
#         engine_stats = engine.get_optimization_stats()
#         cv2.putText(frame, f"- Avg Reward: {engine_stats['average_reward']}", (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2); y_pos += 40
#         cv2.putText(frame, f"- Total Decisions: {engine_stats['total_decisions']}", (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2); y_pos += 40
#         cv2.putText(frame, f"Last Decision: {decision_reason}", (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

#         cv2.imshow('AI Traffic System - Final Demo', frame)

#     print("[INFO] Video processing loop finished.")
#     cap.release()
#     cv2.destroyAllWindows()

# if __name__ == '__main__':
#     data_queue = queue.Queue(maxsize=10)
#     stop_event = threading.Event()

#     # Start websocket thread as daemon so it won't block shutdown if main thread ends.
#     network_thread = threading.Thread(target=websocket_thread, args=(data_queue, stop_event), daemon=True)
#     network_thread.start()

#     print("\n[INFO] Main thread (GUI) started.")
#     try:
#         run_live_inference(data_queue, stop_event)
#     except RuntimeError as e:
#         print(e)
#     except Exception as e:
#         print(f"An error occurred in the main thread: {e}")
#     finally:
#         print("[INFO] Main thread is shutting down.")
#         stop_event.set()
#         # no join needed for daemon thread; but if you change daemon=False then join.



import cv2
import numpy as np
import time
import json
import os
import sys
from ultralytics import YOLO
import asyncio
import websockets
from q_learning_agent import AdaptiveQLearningAgent
from optimization_engine import OptimizationEngine
import threading
import queue

# =================================================================================
# === CONFIGURATION                                                             ===
# =================================================================================
VIDEO_FILE = "my_video.mp4"
SAVED_AGENT_MODEL_PATH = "traffic_agent"

LANE_POLYGONS = {
    "Northbound": np.array([[600, 120], [1350, 120], [1200, 380], [700, 380]], np.int32),
    "Southbound": np.array([[650, 600], [1200, 600], [1300, 900], [550, 900]], np.int32),
    "Eastbound": np.array([[1450, 350], [1900, 350], [1900, 700], [1450, 700]], np.int32),
    "Westbound": np.array([[0, 350], [450, 350], [450, 700], [0, 700]], np.int32),
}

LANE_NAMES_ORDER = ["Northbound", "Southbound", "Eastbound", "Westbound"]

CROSSWALK_POLYGONS = {
    "crosswalk_1": np.array([[1900, 1000], [2100, 1000], [2100, 1200], [1900, 1200]], np.int32)
}

# SHIFT TRAFFIC LIGHT LABELS UPWARDS (fix #2)
TRAFFIC_LIGHT_POSITIONS = {
    "Northbound": (150, 130),
    "Southbound": (150, 330),
    "Eastbound": (150, 530),
    "Westbound": (150, 730)
}

GREEN_LIGHT_DURATION = 8.0
YELLOW_LIGHT_DURATION = 1.5
EMERGENCY_GREEN_DURATION = 5.0
EMERGENCY_CLEARING_TIME = 2.0
STARVATION_THRESHOLD = 30.0
MAX_QUEUE_LENGTH = 30

PERSON_CLASS_ID = 0
VEHICLE_CLASSES = [2, 3, 5, 7]
ALL_DETECTABLE_CLASSES = [PERSON_CLASS_ID] + VEHICLE_CLASSES
MAX_VEHICLES_PER_LANE = 40
YOLO_MODEL = 'yolov8s.pt'
CONF_THRESHOLD = 0.3

WEBSOCKET_URI = os.getenv("BACKEND_WEBSOCKET_URL", "ws://localhost:8000/ws/ai")

# =================================================================================
# === NETWORK THREAD                                                           ===
# =================================================================================
def websocket_thread(data_queue: queue.Queue, stop_event: threading.Event):
    async def sender():
        try:
            async with websockets.connect(WEBSOCKET_URI) as websocket:
                print("✅ WebSocket connected")
                while not stop_event.is_set():
                    try:
                        output_data = data_queue.get_nowait()
                        await websocket.send(json.dumps(output_data))
                    except queue.Empty:
                        await asyncio.sleep(0.01)
        except Exception as e:
            print(f"⚠️ WS Error: {e}")

    asyncio.run(sender())
# =================================================================================
# === MAIN SCRIPT (AI + YOLO + STATE MACHINE)                                   ===
# =================================================================================
def run_live_inference(data_queue: queue.Queue, stop_event: threading.Event):

    def draw_single_traffic_light(frame, position, status):
        x, y = position
        radius = 35

        # Colors
        color = (0, 0, 255)  # RED
        if status == "GREEN":
            color = (0, 255, 0)
        elif status == "YELLOW":
            color = (0, 255, 255)

        cv2.circle(frame, (x, y), radius, color, -1)
        cv2.circle(frame, (x, y), radius, (40, 40, 40), 3)

    # Load Q-learning agent
    agent = AdaptiveQLearningAgent(action_size=4)
    try:
        agent.load_model(SAVED_AGENT_MODEL_PATH)
    except:
        print("⚠️ Agent model not found, running untrained.")

    engine = OptimizationEngine(starvation_threshold=STARVATION_THRESHOLD)

    # Load YOLO
    try:
        model = YOLO(YOLO_MODEL)
    except Exception as e:
        print(f"❌ Failed loading YOLO: {e}")
        model = None

    # Load video
    cap = cv2.VideoCapture(VIDEO_FILE)
    if not cap.isOpened():
        raise RuntimeError(f"❌ Video not found: {VIDEO_FILE}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    wait_ms = max(1, int(1000 / fps))

    # INITIAL STATE
    signal_state = "GREEN"
    current_green_lane_index = 0
    emergency_override_state = None
    lane_to_clear_index = -1
    emergency_target_lane = -1
    state_timer = 0
    paused = False

    print("\n🔵 LIVE MODE STARTED — Press 'q' to quit, 'p' to pause.\n")

    while not stop_event.is_set():

        # Pause logic
        if paused:
            key = cv2.waitKey(100) & 0xFF
            if key == ord('p'):
                paused = False
            elif key == ord('q'):
                stop_event.set()
                break
            continue

        # Read frame
        ret, frame = cap.read()
        if not ret:
            print("🔁 End of video — restarting...")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            time.sleep(0.3)
            continue

        # YOLO detection
        if model:
            try:
                results = model(frame, verbose=False)
            except:
                results = [type("R", (), {"boxes": []})()]
        else:
            results = [type("R", (), {"boxes": []})()]

        lane_counts = {name: 0 for name in LANE_NAMES_ORDER}
        pedestrian_count = 0

        # Loop through detected objects
        for box in results[0].boxes:
            try:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
            except:
                continue

            if cls not in ALL_DETECTABLE_CLASSES or conf < CONF_THRESHOLD:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            if cls == PERSON_CLASS_ID:
                # Pedestrian check
                for poly in CROSSWALK_POLYGONS.values():
                    if cv2.pointPolygonTest(poly, (cx, cy), False) >= 0:
                        pedestrian_count += 1
                        break
            else:
                # Vehicle lane detection
                for name, poly in LANE_POLYGONS.items():
                    if cv2.pointPolygonTest(poly, (cx, cy), False) >= 0:
                        lane_counts[name] += 1
                        break

        # Key input
        key = cv2.waitKey(wait_ms) & 0xFF
        manual_emergency = -1
        if key == ord('1'): manual_emergency = 0
        if key == ord('2'): manual_emergency = 1
        if key == ord('3'): manual_emergency = 2
        if key == ord('4'): manual_emergency = 3
        if key == ord('p'): paused = True
        if key == ord('q'):
            stop_event.set()
            break

        state_timer += 1 / fps
        decision_reason = "Observing"
        send_update = False

        # --- EMERGENCY LOGIC ---
        if manual_emergency != -1 and emergency_override_state is None:
            if not (current_green_lane_index == manual_emergency and signal_state == "GREEN"):
                emergency_override_state = "CLEARING_YELLOW"
                lane_to_clear_index = current_green_lane_index
                emergency_target_lane = manual_emergency
                state_timer = 0
                decision_reason = f"Manual emergency → {LANE_NAMES_ORDER[manual_emergency]}"
                send_update = True

        if emergency_override_state:
            if emergency_override_state == "CLEARING_YELLOW":
                signal_state = "YELLOW"
                if state_timer >= 1.5:
                    emergency_override_state = "CLEARING_ALL_RED"
                    state_timer = 0
            elif emergency_override_state == "CLEARING_ALL_RED":
                signal_state = "ALL_RED"
                if state_timer >= 2.0:
                    current_green_lane_index = emergency_target_lane
                    signal_state = "GREEN"
                    emergency_override_state = "ACTIVE"
                    state_timer = 0
            elif emergency_override_state == "ACTIVE" and state_timer >= EMERGENCY_GREEN_DURATION:
                emergency_override_state = None
                signal_state = "YELLOW"
                state_timer = 0

        else:
            # Normal signal switching
            if signal_state == "GREEN" and state_timer >= GREEN_LIGHT_DURATION:
                signal_state = "YELLOW"
                state_timer = 0

            elif signal_state == "YELLOW" and state_timer >= YELLOW_LIGHT_DURATION:
                observation = np.array([
                    lane_counts[name] / MAX_VEHICLES_PER_LANE
                    for name in LANE_NAMES_ORDER
                ] + [current_green_lane_index / 3, 0])

                try:
                    rec = agent.choose_action(observation, training=False)
                except:
                    rec = 0

                ctx = {"emergency_active": False, "pedestrian_count": pedestrian_count}
                action, decision_reason, _ = engine.optimize_action(
                    lane_counts,
                    LANE_NAMES_ORDER[current_green_lane_index],
                    rec,
                    ctx
                )

                current_green_lane_index = action
                signal_state = "GREEN"
                state_timer = 0

        # Send backend update
        try:
            data_queue.put_nowait({
                "timestamp": time.time(),
                "lane_counts": lane_counts,
                "pedestrian_count": pedestrian_count,
                "decision": {"reason": decision_reason},
                "signal_state": {
                    "active_direction": LANE_NAMES_ORDER[current_green_lane_index],
                    "state": signal_state,
                    "timer": int(state_timer)
                }
            })
        except queue.Full:
            pass
        # =================================================================================
        # === VISUALIZATION PANEL (FIXED & SHIFTED LEFT + LIGHTS MOVED UP)               ===
        # =================================================================================

        PANEL_WIDTH = 350
        PANEL_X = frame.shape[1] - PANEL_WIDTH - 400    # shifted left 300 px
        PANEL_Y = 0
        PANEL_H = frame.shape[0]

        # Create overlay for dark panel
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (PANEL_X, PANEL_Y),
            (PANEL_X + PANEL_WIDTH, PANEL_H),
            (0, 0, 0),
            -1
        )

        # Blend the black panel
        frame = cv2.addWeighted(overlay, 0.60, frame, 0.40, 0)

        # Draw traffic lights (positions were shifted UP in part 1)
        for i, (name, pos) in enumerate(TRAFFIC_LIGHT_POSITIONS.items()):
            status = "RED"

            # emergency states
            if emergency_override_state == "CLEARING_YELLOW" and i == lane_to_clear_index:
                status = "YELLOW"
            elif emergency_override_state == "CLEARING_ALL_RED":
                status = "RED"
            elif emergency_override_state == "ACTIVE" and i == current_green_lane_index:
                status = "GREEN"

            # normal mode
            elif i == current_green_lane_index and emergency_override_state is None:
                status = signal_state

            draw_single_traffic_light(frame, pos, status)

            # Label next to each light
            cv2.putText(
                frame,
                name,
                (pos[0] + 60, pos[1] + 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.1,
                (255, 255, 255),
                3
            )

        # ============================
        # TEXT PANEL CONTENT
        # ============================

        x_text = PANEL_X + 20     # margin from left of the panel
        y_text = 40               # start higher so everything fits

        status_text = f"{LANE_NAMES_ORDER[current_green_lane_index]}: {signal_state}"
        if emergency_override_state:
            status_text = f"EMERGENCY ({emergency_override_state})"

        # TITLE
        cv2.putText(frame, "SYSTEM STATUS", (x_text, y_text),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 255), 3)
        y_text += 55

        # Current State
        cv2.putText(frame, f"Current: {status_text}", (x_text, y_text),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.90, (255, 255, 255), 2)
        y_text += 40

        # Timer
        cv2.putText(frame, f"Timer: {int(state_timer)} sec", (x_text, y_text),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.90, (255, 255, 255), 2)
        y_text += 50

        # Vehicle Counts
        cv2.putText(frame, "Vehicle Counts:", (x_text, y_text),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 255), 3)
        y_text += 45

        for lane, count in lane_counts.items():
            cv2.putText(frame, f"- {lane}: {count}", (x_text, y_text),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.95, (255, 255, 255), 2)
            y_text += 35

        # Optimization Stats
        cv2.putText(frame, "Optimization Stats:", (x_text, y_text),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 255), 3)
        y_text += 45

        stats = engine.get_optimization_stats()

        cv2.putText(frame, f"Avg Reward: {stats['average_reward']}", (x_text, y_text),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.95, (255, 255, 255), 2)
        y_text += 35

        cv2.putText(frame, f"Decisions: {stats['total_decisions']}", (x_text, y_text),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.95, (255, 255, 255), 2)
        y_text += 35

        cv2.putText(frame, f"Last: {decision_reason}", (x_text, y_text),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.95, (255, 255, 255), 2)

        # Show window
        cv2.imshow("AI Traffic System - Final Demo", frame)

    # END WHILE LOOP
    cap.release()
    cv2.destroyAllWindows()


# =================================================================================
# === PROGRAM ENTRY POINT                                                       ===
# =================================================================================
if __name__ == "__main__":
    data_queue = queue.Queue(maxsize=10)
    stop_event = threading.Event()

    ws_thread = threading.Thread(
        target=websocket_thread,
        args=(data_queue, stop_event),
        daemon=True
    )
    ws_thread.start()

    print("🚦 Starting System...")

    try:
        run_live_inference(data_queue, stop_event)
    except Exception as e:
        print("❌ ERROR:", e)
    finally:
        stop_event.set()
        print("🛑 System shut down.")
