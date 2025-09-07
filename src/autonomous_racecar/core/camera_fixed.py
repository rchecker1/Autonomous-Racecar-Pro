#src/autonomous_racecar/core/camera_fixed.py
#fixed gstreamer pipeline

import subprocess
import numpy as np
import cv2
import os
import time
from typing import Optional

class FixedCamera:
    """camera with corrected gstreamer pipeline"""
    
    def __init__(self, mode='inference', width=640, height=480, fps=21):
        self.mode = mode
        self.width = width
        self.height = height
        self.fps = fps
        
        if mode in ['inference', 'training']:
            self.target_size = (224, 224)
        else:
            self.target_size = None
            
        self._running = False
        print(f"fixed camera created: {mode}")
    
    def start(self):
        print("starting fixed camera")
        try:
            self._test_capture()
            self._running = True
            print("fixed camera started")
            return True
        except Exception as e:
            print(f"camera start failed: {e}")
            return False
    
    def _test_capture(self):
        """test with corrected pipeline"""
        temp_file = '/tmp/test_frame.raw'
        cmd = [
            'gst-launch-1.0',
            'nvarguscamerasrc', 'num-buffers=1',
            f'! video/x-raw(memory:NVMM), width={self.width}, height={self.height}',
            '! nvvidconv ! video/x-raw, format=BGRx',
            '! videoconvert ! video/x-raw, format=BGR',
            f'! filesink location={temp_file}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=10)
        if result.returncode != 0:
            raise RuntimeError(f"gstreamer failed: {result.stderr.decode()}")
    
    def read(self):
        if not self._running:
            return None
            
        try:
            temp_file = '/tmp/camera_frame.raw'
            cmd = [
                'gst-launch-1.0',
                'nvarguscamerasrc', 'num-buffers=1',
                f'! video/x-raw(memory:NVMM), width={self.width}, height={self.height}',
                '! nvvidconv ! video/x-raw, format=BGRx',
                '! videoconvert ! video/x-raw, format=BGR',
                f'! filesink location={temp_file}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            
            if result.returncode == 0 and os.path.exists(temp_file):
                with open(temp_file, 'rb') as f:
                    data = f.read()
                
                frame = np.frombuffer(data, dtype=np.uint8)
                frame = frame.reshape((self.height, self.width, 3))
                
                if self.target_size:
                    frame = cv2.resize(frame, self.target_size)
                
                return frame
            
        except Exception as e:
            print(f"capture error: {e}")
        
        return None
    
    def stop(self):
        self._running = False
        print("fixed camera stopped")
    
    @property
    def running(self):
        return self._running
        
    @property
    def value(self):
        return self.read()

def test_fixed_camera():
    print("testing fixed camera")
    camera = FixedCamera('debug')
    if camera.start():
        img = camera.read()
        if img is not None:
            print(f"fixed camera working: {img.shape}")
            camera.stop()
            return True
    camera.stop()
    return False
