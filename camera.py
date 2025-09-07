#src/autonomous_racecar/core/camera.py
#fixed to use your exact working method

import cv2
import time
import numpy as np
import gc
import inspect
from typing import Optional, Tuple
from jetcam.csi_camera import CSICamera

class AutonomousRacecarCamera:
    """
    camera interface using your proven working method
    simple, reliable, no over-engineering
    """

    def __init__(self,
                 mode: str = 'inference',
                 width: int = 640,
                 height: int = 480,
                 fps: int = 21):
        """
        initialize camera with proven settings

        args:
            mode: 'inference', 'training', or 'debug'
            width: camera width (640 works reliably)
            height: camera height (480 works reliably) 
            fps: frames per second (21 is proven stable)
        """
        self.mode = mode
        self.width = width
        self.height = height
        self.fps = fps

        #set target size based on mode
        if mode in ['inference', 'training']:
            self.target_size = (224, 224)  #model input size
        else:
            self.target_size = None  #debug mode - no resizing

        #camera state
        self._camera = None
        self._running = False
        self._last_image = None

        print(f"camera configured:")
        print(f"mode: {mode}")
        print(f"capture: {width}x{height} @ {fps}fps")
        if self.target_size:
            print(f"output: {self.target_size[0]}x{self.target_size[1]}")

    def start(self) -> bool:
        """start camera using your exact working method"""
        print("starting camera using proven method")

        try:
            #step 1: release any existing cameras first (your working pattern)
            self._release_existing_cameras()
            time.sleep(1)

            #step 2: create camera with your exact working settings
            print("creating camera")
            self._camera = CSICamera(
                width=self.width,
                height=self.height, 
                capture_fps=self.fps
            )

            #step 3: start camera (your exact method)
            self._camera.running = True
            self._running = True

            #step 4: wait for initialization (your timing)
            time.sleep(3)

            #step 5: test capture using .value (your working method)
            test_image = self._camera.value
            if test_image is not None:
                print("camera started successfully")
                print(f"raw image: {test_image.shape}")

                #test image processing
                processed = self._process_image(test_image)
                if processed is not None:
                    print(f"processed: {processed.shape}")
                    self._last_image = processed
                    return True
                else:
                    print("image processing failed")
                    return False
            else:
                print("camera not capturing images")
                return False

        except Exception as e:
            print(f"camera start failed: {e}")
            self._running = False
            return False

    def stop(self):
        """stop camera safely"""
        print("stopping camera")

        try:
            self._running = False

            #stop camera
            if self._camera:
                self._camera.running = False
                time.sleep(1)
                self._camera = None

            print("camera stopped")

        except Exception as e:
            print(f"warning during camera stop: {e}")

    def _release_existing_cameras(self):
        """release any existing cameras (from your working utilities)"""
        print("releasing existing cameras")

        try:
            #get globals from calling frame
            frame = inspect.currentframe().f_back.f_back
            caller_globals = frame.f_globals

            #find camera objects
            camera_vars = []
            for var_name in list(caller_globals.keys()):
                try:
                    obj = caller_globals[var_name]
                    if (hasattr(obj, 'running') or
                        'camera' in str(type(obj)).lower()):
                        camera_vars.append(var_name)
                except:
                    pass

            #stop all cameras
            for var_name in camera_vars:
                try:
                    obj = caller_globals[var_name]
                    if hasattr(obj, 'running'):
                        obj.running = False
                    if hasattr(obj, 'stop'):
                        obj.stop()
                    del caller_globals[var_name]
                except:
                    pass

            #force garbage collection
            gc.collect()
            time.sleep(1)

        except Exception as e:
            print(f"warning during camera release: {e}")

    def _process_image(self, image: np.ndarray) -> Optional[np.ndarray]:
        """process raw camera image"""
        if image is None:
            return None

        try:
            #resize if needed
            if self.target_size:
                processed = cv2.resize(image, self.target_size)
                return processed

            return image

        except Exception as e:
            print(f"image processing error: {e}")
            return image

    def read(self) -> Optional[np.ndarray]:
        """read and process current image"""
        try:
            if not self._running or not self._camera:
                return self._last_image

            #use .value method (your working approach)
            raw_image = self._camera.value
            processed = self._process_image(raw_image)

            if processed is not None:
                self._last_image = processed

            return processed

        except Exception as e:
            print(f"error reading from camera: {e}")
            return self._last_image

    @property
    def value(self) -> Optional[np.ndarray]:
        """get current processed camera image"""
        return self.read()

    @property
    def raw_value(self) -> Optional[np.ndarray]:
        """get current raw camera image (full resolution)"""
        if self._camera and hasattr(self._camera, 'value'):
            return self._camera.value
        return None

    @property
    def running(self) -> bool:
        """check if camera is running"""
        return self._running

    @property
    def output_size(self) -> Tuple[int, int]:
        """get output image size"""
        if self.target_size:
            return self.target_size
        return (self.width, self.height)

    def capture_image(self, filepath: str) -> bool:
        """capture and save single image"""
        try:
            image = self.read()
            if image is not None:
                cv2.imwrite(filepath, image)
                print(f"image saved: {filepath}")
                return True
            else:
                print("failed to capture image")
                return False
        except Exception as e:
            print(f"error saving image: {e}")
            return False

    def __enter__(self):
        """context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """context manager exit"""
        self.stop()


#convenience functions
def create_inference_camera() -> AutonomousRacecarCamera:
    """create camera for autonomous driving (224x224 output)"""
    return AutonomousRacecarCamera(mode='inference')

def create_training_camera() -> AutonomousRacecarCamera:
    """create camera for data collection (224x224 output)"""
    return AutonomousRacecarCamera(mode='training')

def create_debug_camera() -> AutonomousRacecarCamera:
    """create camera for debugging (full 640x480 output)"""
    return AutonomousRacecarCamera(mode='debug')

def test_camera(mode: str = 'debug') -> bool:
    """test camera functionality"""
    print(f"testing camera in {mode} mode")

    try:
        with AutonomousRacecarCamera(mode=mode) as camera:
            if camera.running:
                #test multiple captures
                for i in range(3):
                    img = camera.read()
                    if img is not None:
                        print(f"capture {i+1}: {img.shape}")
                    else:
                        print(f"capture {i+1}: failed")
                    time.sleep(0.5)

                print("camera test passed")
                return True
            else:
                print("camera failed to start")
                return False

    except Exception as e:
        print(f"camera test failed: {e}")
        return False

def quick_camera_test() -> bool:
    """quick camera availability test"""
    try:
        print("quick camera test")
        camera = CSICamera(width=640, height=480, capture_fps=21)
        camera.running = True
        time.sleep(2)

        img = camera.value
        result = img is not None

        camera.running = False
        del camera

        if result:
            print(f"camera available: {img.shape}")
        else:
            print("camera not capturing")

        return result

    except Exception as e:
        print(f"camera test failed: {e}")
        return False
