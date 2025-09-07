#src/autonomous_racecar/core/camera_simple.py
#using the gstreamer format that actually works

import subprocess
import numpy as np
import cv2
import os
import time
from typing import Optional

class SimpleCamera:
    """camera using your working gstreamer format"""
    
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
        print(f"simple camera created: {mode}")
    
    def start(self):
        print("starting simple camera")
        try:
            self._test_capture()
            self._running = True
            print("simple camera started")
            return True
        except Exception as e:
            print(f"camera start failed: {e}")
            return False
    
    def _test_capture(self):
        """test with working format"""
        temp_file = '/tmp/test_frame.raw'
        cmd = [
            'gst-launch-1.0',
            'nvarguscamerasrc', 'num-buffers=1',
            f'! video/x-raw(memory:NVMM), width={self.width}, height={self.height}',
            '! nvvidconv',
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
                '! nvvidconv',
                f'! filesink location={temp_file}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            
            if result.returncode == 0 and os.path.exists(temp_file):
                with open(temp_file, 'rb') as f:
                    data = f.read()
                
                # the default format should be interpretable by opencv
                frame = np.frombuffer(data, dtype=np.uint8)
                # we'll need to figure out the exact dimensions/format
                # but let's test if this basic approach works first
                
                print(f"captured {len(data)} bytes")
                return data  # return raw data for now
            
        except Exception as e:
            print(f"capture error: {e}")
        
        return None
    
    def stop(self):
        self._running = False
        print("simple camera stopped")

def test_simple_camera():
    print("testing simple camera")
    camera = SimpleCamera('debug')
    if camera.start():
        data = camera.read()
        if data is not None:
            print(f"simple camera captured data: {len(data)} bytes")
            camera.stop()
            return True
    camera.stop()
    return False
