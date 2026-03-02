from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import cv2
import mediapipe as mp
import threading
from mediapipe import solutions as mp_solutions
import time
import numpy as np
# Direct submodule imports
from mediapipe.python.solutions.pose import Pose
from mediapipe.python.solutions.drawing_utils import DrawingSpec, draw_landmarks
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- State Management ---
camera = None
latest_frame = None
camera_active = False
frame_lock = threading.Lock()
state_lock = threading.Lock()

reps = 0
stage = "UP"
target_reps = 10
exercise_done = False
current_exercise = "squats"

# --- MediaPipe Setup --

# Initialize pose detector
mp_pose = Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Use draw_landmarks directly in your frame processing
mp_drawing = draw_landmarks
def capture_frames():
    global latest_frame, camera, camera_active
    while camera_active and camera is not None:
        success, frame = camera.read()
        if success:
            frame = cv2.flip(frame, 1)
            with frame_lock:
                latest_frame = frame
        time.sleep(0.01)

def stop_camera_hardware():
    global camera, latest_frame, camera_active
    time.sleep(3.0) 
    camera_active = False 
    with frame_lock:
        if camera is not None:
            camera.release()
            camera = None
        latest_frame = None
    print("🛑 Camera Hardware Released")

def start_camera():
    global camera, camera_active
    with frame_lock:
        if camera is None:
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                camera = cv2.VideoCapture(1)
            camera_active = True
            threading.Thread(target=capture_frames, daemon=True).start()

def calc_angle(a, b, c):
    a = np.array([a.x, a.y]); b = np.array([b.x, b.y]); c = np.array([c.x, c.y])
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180 else angle

def process_frame():
    global reps, stage, exercise_done
    with frame_lock:
        if latest_frame is None: return None
        frame = latest_frame.copy()

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame, 
            results.pose_landmarks, 
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
        )

        lm = results.pose_landmarks.landmark
        with state_lock:
            # 1. SQUATS LOGIC
            if "squat" in current_exercise:
                angle = calc_angle(lm[23], lm[25], lm[27]) # Hip, Knee, Ankle
                if angle < 90 and stage == "UP": stage = "DOWN"
                if angle > 160 and stage == "DOWN": stage = "UP"; reps += 1

            # 2. PULL-UPS LOGIC
            elif "pullup" in current_exercise or "pull-up" in current_exercise:
                # Track the elbow angle (Shoulder, Elbow, Wrist)
                angle = calc_angle(lm[11], lm[13], lm[15]) 
                # Stage "DOWN" = Arms extended (>160 deg)
                # Stage "UP" = Chin over bar (<60 deg)
                if angle > 160: stage = "DOWN"
                if angle < 60 and stage == "DOWN":
                    stage = "UP"
                    reps += 1

            # 3. PUSH-UPS LOGIC (Default)
            else: 
                angle = calc_angle(lm[11], lm[13], lm[15])
                if angle < 70 and stage == "UP": stage = "DOWN"
                if angle > 160 and stage == "DOWN": stage = "UP"; reps += 1

            if reps >= target_reps and not exercise_done:
                exercise_done = True
                threading.Thread(target=stop_camera_hardware).start()

    cv2.putText(frame, f"{current_exercise.upper()}: {reps}/{target_reps}", (30, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    
    _, jpeg = cv2.imencode(".jpg", frame)
    return jpeg.tobytes()

@app.get("/video_feed")
async def video_feed():
    def gen():
        while camera_active:
            frame = process_frame()
            if frame: 
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.03)
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/exercise_status")
def get_status():
    with state_lock:
        return {"reps": reps, "done": exercise_done, "exercise": current_exercise}

@app.get("/reset")
def reset():
    global reps, stage, exercise_done
    with state_lock:
        reps = 0; stage = "UP"; exercise_done = False
    start_camera()
    return {"status": "reset"}

@app.post("/set_target")
def set_target(target: int):
    global target_reps
    target_reps = target
    return {"status": "target set"}

@app.post("/set_exercise")
def set_ex(name: str):
    global current_exercise
    current_exercise = name.lower()
    return {"status": "exercise set"}

if __name__ == "__main__":
    import uvicorn
    # Start camera on launch
    start_camera()
    uvicorn.run(app, host="127.0.0.1", port=8000)
