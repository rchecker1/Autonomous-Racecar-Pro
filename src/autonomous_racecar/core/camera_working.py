#src/autonomous_racecar/core/camera_working.py
#simple working camera using gstreamer subprocess

import cv2
import time
import numpy as np
import subprocess
import tempfile
import os
from typing import Optional, Tuple

class WorkingCamera:
    """simple camera that actually works with your hardware"""
    
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
        print(f"working camera created: {mode}")
    
    def start(self):
        """start camera using gstreamer snapshot method"""
        print("starting working camera")
        
        try:
            # test gstreamer capture
            self._test_capture()
            self._running = True
            print("working camera started")
            return True
        except Exception as e:
            print(f"camera start failed: {e}")
            return False
    
    def _test_capture(self):
        """test single frame capture"""
        cmd = [
            'gst-launch-1.0', 
            'nvarguscamerasrc', 'num-buffers=1',
            f'! video/x-raw(memory:NVMM), width={self.width}, height={self.height}',
            '! nvvidconv ! video/x-raw, format=BGR',
            '! filesink location=/tmp/test_frame.raw'
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=10)
        if result.returncode != 0:
            raise RuntimeError("gstreamer test failed")
    
    def read(self):
        """capture single frame"""
        if not self._running:
            return None
            
        try:
            # capture frame to temp file
            temp_file = '/tmp/camera_frame.raw'
            cmd = [
                'gst-launch-1.0',
                'nvarguscamerasrc', 'num-buffers=1',
                f'! video/x-raw(memory:NVMM), width={self.width}, height={self.height}',
                '! nvvidconv ! video/x-raw, format=BGR',
                f'! filesink location={temp_file}'
            ]
            
            subprocess.run(cmd, capture_output=True, timeout=5)
            
            # read raw frame data
            if os.path.exists(temp_file):
                data = open(temp_file, 'rb').read()
                frame = np.frombuffer(data, dtype=np.uint8)
                frame = frame.reshape((self.height, self.width, 3))
                
                # resize if needed
                if self.target_size:
                    frame = cv2.resize(frame, self.target_size)
                
                return frame
            
        except Exception as e:
            print(f"capture error: {e}")
        
        return None
    
    def stop(self):
        self._running = False
        print("working camera stopped")
    
    @property
    def running(self):
        return self._running
        
    @property 
    def value(self):
        return self.read()

def test_working_camera():
    """test the working camera"""
    print("testing working camera")
    
    camera = WorkingCamera('debug')
    if camera.start():
        img = camera.read()
        if img is not None:
            print(f"working camera success: {img.shape}")
            camera.stop()
            return True
        else:
            print("no image captured")
    
    camera.stop()
    return False
