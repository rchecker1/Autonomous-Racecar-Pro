#src/autonomous_racecar/core/camera_gstreamer.py
#gstreamer-based camera using subprocess (bypasses jetcam issues)

import cv2
import time
import numpy as np
import subprocess
import threading
import tempfile
import os
from typing import Optional, Tuple

class GStreamerCamera:
    """
    gstreamer-based camera using subprocess calls
    bypasses jetcam library issues
    """

    def __init__(self,
                 mode: str = 'inference',
                 width: int = 640,
                 height: int = 480,
                 fps: int = 21):
        """
        initialize camera with gstreamer backend
        """
        self.mode = mode
        self.width = width
        self.height = height
        self.fps = fps

        #set target size based on mode
        if mode in ['inference', 'training']:
            self.target_size = (224, 224)
        else:
            self.target_size = None

        #camera state
        self._running = False
        self._last_image = None
        self._capture_thread = None
        self._temp_fifo = None

        print(f"gstreamer camera configured:")
        print(f"mode: {mode}")
        print(f"capture: {width}x{height} @ {fps}fps")
        if self.target_size:
            print(f"output: {self.target_size[0]}x{self.target_size[1]}")

    def start(self) -> bool:
        """start camera using gstreamer subprocess"""
        print("starting gstreamer camera")

        try:
            #create named pipe for gstreamer output
            self._temp_fifo = tempfile.mktemp(suffix='.raw')
            os.mkfifo(self._temp_fifo)

            #start gstreamer process
            gst_command = [
                'gst-launch-1.0',
                'nvarguscamerasrc',
                f'! video/x-raw(memory:NVMM), width={self.width}, height={self.height}, framerate={self.fps}/1',
                '! nvvidconv',
                '! video/x-raw, format=BGR',
                f'! filesink location={self._temp_fifo}'
            ]

            self._gst_process = subprocess.Popen(
                gst_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            #start capture thread
            self._running = True
            self._capture_thread = threading.Thread(target=self._capture_loop)
            self._capture_thread.daemon = True
            self._capture_thread.start()

            #wait for first frame
            time.sleep(3)

            if self._last_image is not None:
                print("gstreamer camera started successfully")
                print(f"image: {self._last_image.shape}")
                return True
            else:
                print("no image captured")
                return False

        except Exception as e:
            print(f"gstreamer camera start failed: {e}")
            return False

    def _capture_loop(self):
        """capture loop running in thread"""
        frame_size = self.width * self.height * 3  # BGR

        try:
            with open(self._temp_fifo, 'rb') as fifo:
                while self._running:
                    data = fifo.read(frame_size)
                    if len(data) == frame_size:
                        # convert raw BGR data to numpy array
                        frame = np.frombuffer(data, dtype=np.uint8)
                        frame = frame.reshape((self.height, self.width, 3))
                        
                        # process image
                        processed = self._process_image(frame)
                        self._last_image = processed
                    else:
                        time.sleep(0.01)
        except Exception as e:
            print(f"capture loop error: {e}")

    def _process_image(self, image: np.ndarray) -> Optional[np.ndarray]:
        """process raw camera image"""
        if image is None:
            return None

        try:
            if self.target_size:
                processed = cv2.resize(image, self.target_size)
                return processed
            return image
        except Exception as e:
            print(f"image processing error: {e}")
            return image

    def read(self) -> Optional[np.ndarray]:
        """read current image"""
        return self._last_image

    def stop(self):
        """stop camera safely"""
        print("stopping gstreamer camera")
        
        self._running = False
        
        if self._capture_thread:
            self._capture_thread.join(timeout=2)
        
        if hasattr(self, '_gst_process'):
            self._gst_process.terminate()
            self._gst_process.wait()
        
        if self._temp_fifo and os.path.exists(self._temp_fifo):
            os.unlink(self._temp_fifo)
        
        print("gstreamer camera stopped")

    @property
    def running(self):
        return self._running

    @property
    def value(self):
        return self.read()

#test function
def test_gstreamer_camera():
    """test gstreamer camera"""
    print("testing gstreamer camera")
    
    camera = GStreamerCamera('debug')
    if camera.start():
        for i in range(5):
            img = camera.read()
            if img is not None:
                print(f"capture {i+1}: {img.shape}")
            else:
                print(f"capture {i+1}: no image")
            time.sleep(1)
        
        camera.stop()
        print("gstreamer camera test complete")
        return True
    else:
        print("gstreamer camera test failed")
        return False
