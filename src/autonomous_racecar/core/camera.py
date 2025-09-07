#src/autonomous_racecar/core/camera.py
#placeholder until we implement working solution

import cv2
import time
import numpy as np
from typing import Optional, Tuple

class AutonomousRacecarCamera:
    """placeholder camera class"""
    
    def __init__(self, mode='inference', width=640, height=480, fps=21):
        self.mode = mode
        print(f"camera placeholder created: {mode}")
        
    def start(self):
        print("camera placeholder - not functional yet")
        return False
        
    def stop(self):
        pass
        
    def read(self):
        return None

def create_inference_camera():
    return AutonomousRacecarCamera('inference')

def create_training_camera():
    return AutonomousRacecarCamera('training')

def create_debug_camera():
    return AutonomousRacecarCamera('debug')

def test_camera(mode='debug'):
    print(f"camera test placeholder - {mode}")
    return False
