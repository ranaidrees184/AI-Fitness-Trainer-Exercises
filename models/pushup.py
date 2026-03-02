import math

class PushupCounter:
    def __init__(self):
        self.counter = 0
        self.stage = None

    def calculate_angle(self, a, b, c):
        angle = math.degrees(
            math.atan2(c.y - b.y, c.x - b.x) -
            math.atan2(a.y - b.y, a.x - b.x)
        )
        return abs(angle)

    def process_pose(self, landmarks, mp_pose):
        # Example: Left arm points
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]

        angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)

        feedback = ""
        correct = True

        # Pushup logic
        if angle > 160:
            self.stage = "up"
            feedback = "Go Down"
        if angle < 90 and self.stage == "up":
            self.stage = "down"
            self.counter += 1
            feedback = "Good! Keep going"

        # Return structured output
        return {
            "performed_reps": self.counter,
            "assigned_reps": 10,
            "feedback": feedback or "Adjust your position",
            "is_correct": correct
        }
