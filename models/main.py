from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pushup import run_pushup_detection

app = FastAPI()

# ✅ Enable CORS so frontend can call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Backend is running"}

@app.post("/start_exercise")
def start_exercise(reps: int = 10):
    """
    Starts push-up detection session.
    This opens webcam and runs MediaPipe for rep counting.
    """
    result = run_pushup_detection(reps)
    return {"message": "Exercise complete", "result": result}
