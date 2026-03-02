import numpy as np
from utils.pose_utils import calculate_angle

class BaseExerciseMonitor:
    def __init__(self, assigned_reps=10):
        self.counter = 0
        self.stage = None
        self.started = False
        self.assigned_reps = assigned_reps
        self.feedback = ""

    def update_feedback(self, angle, min_angle, max_angle):
        """
        Basic feedback depending on range of motion.
        Override this for exercise-specific behavior.
        """
        if angle > max_angle:
            self.feedback = "Lower down!"
        elif angle < min_angle:
            self.feedback = "Push up fully!"
        else:
            self.feedback = "Good form!"

    def is_complete(self):
        return self.counter >= self.assigned_reps