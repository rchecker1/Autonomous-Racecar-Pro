#src/autonomous_racecar/core/camera_opencv.py
#using your working opencv gstreamer approach

import cv2
import time
import numpy as np
from typing import Optional, Tuple

class OpenCVCamera:
    """camera using your working opencv gstreamer pipeline"""
    
    def __init__(self, mode='inference', width=640, height=480, fps=21):
        self.mode = mode
        self.width = width
        self.height = height
        self.fps = fps
        
        if mode in ['inference', 'training']:
            self.target_size = (224, 224)
        else:
            self.target_size = None
            
        self._camera = None
        self._running = False
        
        # your working gstreamer pipeline
        self.pipeline = f"nvarguscamerasrc ! video/x-raw(memory:NVMM), width={width}, height={height}, format=(string)NV12, framerate=(fraction){fps}/1 ! nvvidconv flip-method=0 ! video/x-raw, width={width}, height={height}, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"
        
        print(f"opencv camera configured: {mode}")
    
    def start(self):
        print("starting opencv camera")
        try:
            self._camera = cv2.VideoCapture(self.pipeline, cv2.CAP_GSTREAMER)
            
            if self._camera.isOpened():
                # test capture
                ret, frame = self._camera.read()
                if ret and frame is not None:
                    print(f"opencv camera started: {frame.shape}")
                    self._running = True
                    return True
                else:
                    print("camera opened but no frame")
                    return False
            else:
                print("camera failed to open")
                return False
                
        except Exception as e:
            print(f"camera start failed: {e}")
            return False
    
    def read(self):
        if not self._running or not self._camera:
            return None
        
        try:
            ret, frame = self._camera.read()
            if ret and frame is not None:
                # resize if needed
                if self.target_size:
                    frame = cv2.resize(frame, self.target_size)
                return frame
            return None
        except Exception as e:
            print(f"read error: {e}")
            return None
    
    def stop(self):
        self._running = False
        if self._camera:
            self._camera.release()
        print("opencv camera stopped")
    
    @property
    def running(self):
        return self._running
        
    @property
    def value(self):
        return self.read()
        
    def __enter__(self):
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

# convenience functions
def create_inference_camera():
    return OpenCVCamera('inference')

def create_training_camera():
    return OpenCVCamera('training')

def create_debug_camera():
    return OpenCVCamera('debug')

def test_opencv_camera():
    print("testing opencv camera")
    try:
        with OpenCVCamera('debug') as camera:
            if camera.running:
                for i in range(3):
                    img = camera.read()
                    if img is not None:
                        print(f"capture {i+1}: {img.shape}")
                    else:
                        print(f"capture {i+1}: failed")
                    time.sleep(0.5)
                print("opencv camera test passed")
                return True
        return False
    except Exception as e:
        print(f"test failed: {e}")
        return False
