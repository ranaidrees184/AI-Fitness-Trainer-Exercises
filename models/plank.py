import numpy as np

class PlankCounter:
    def __init__(self):
        self.feedback = "Hold steady"
        self.correct_form = 0
        self.incorrect_form = 0

    def calculate_angle(self, a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        if angle > 180:
            angle = 360 - angle
        return angle

    def process_pose(self, landmarks, mp_pose):
        # Right side: Shoulder–Hip–Ankle
        shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
               landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

        angle = self.calculate_angle(shoulder, hip, ankle)
        feedback = ""

        if 160 <= angle <= 175:
            feedback = "Perfect posture!"
            self.correct_form += 1
        elif angle < 160:
            feedback = "Raise your hips!"
            self.incorrect_form += 1
        else:
            feedback = "Lower your hips!"

        return {
            "angle": int(angle),
            "feedback": feedback,
            "correct_frames": self.correct_form,
            "incorrect_frames": self.incorrect_form
        }