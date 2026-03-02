import numpy as np

class PullupCounter:
    def __init__(self):
        self.counter = 0
        self.stage = None
        self.feedback = ""

    def calculate_angle(self, a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        if angle > 180:
            angle = 360 - angle
        return angle

    def process_pose(self, landmarks, mp_pose):
        # Shoulder, Elbow, Wrist (right arm)
        shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

        angle = self.calculate_angle(shoulder, elbow, wrist)
        feedback = ""

        # Detect stages
        if angle > 150:
            self.stage = "down"
            feedback = "Move up!"
        if angle < 70 and self.stage == "down":
            self.stage = "up"
            self.counter += 1
            feedback = "Good rep!"
        elif angle > 70 and self.stage == "up":
            feedback = "Go lower for full range!"

        return {
            "angle": int(angle),
            "count": self.counter,
            "feedback": feedback
        }