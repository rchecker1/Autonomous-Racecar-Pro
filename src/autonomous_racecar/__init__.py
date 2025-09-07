#src/autonomous_racecar/__init__.py
#Autonomous Racecar main package init
"""
Autonomous Racecar Pro - AI racing system


A clean, modular autonomous racing car system with:
- Clean hardware interfaces
- Rapid data collection
- Efficient model training
- Safe autonomous driving
- Comprehensive testing
Quick Start:

>>> from autonomous_racecar.core.hardware import AutonomousRacecar
>>> from autonomous_racecar.core.camera import create_inference_camera
>>> from autonomous_racecar.data.collection import create_rapid_collector
>>> from autonomous_racecar.training.trainer import ModelTrainer
>>> from autonomous_racecar.autonomous.driver import AutonomousDriver
>>> # Hardware setup
>>> car = AutonomousRacecar(steering_offset=0.17)
>>> camera = create_inference_camera()
>>> # Quick autonomous driving
>>> driver = AutonomousDriver(car, camera)
>>> driver.start_autonomous()
"""
__version__ = "1.0.0"
__author__ = "Rishan Checker"
__email__ = "rishanchecker@gmail.com"

#imports - only existing modules for now
from .core.hardware import AutonomousRacecar
from .core.camera import AutonomousRacecarCamera, create_inference_camera, create_training_camera
#from .data.collection import RapidDataCollector, create_rapid_collector
#from .models.networks import SteeringModel
#from .training.trainer import ModelTrainer
#from .autonomous.driver import AutonomousDriver

#metadata
__all__ = [
    'AutonomousRacecar',
    'AutonomousRacecarCamera',
    'create_inference_camera',
    'create_training_camera',
    #'DataCollector',
    #'create_collector',
    #'SteeringModel',
    #'ModelTrainer',
    #'AutonomousDriver'
]

VERSION_INFO = {
    'major': 1,
    'minor': 0,
    'patch': 0,
    'release': 'stable'
}

def get_version():
    """Get package version"""
    return __version__

def system_info():
    """Get system info"""
    import torch
    import platform
    info = {
        'autonomous_racecar_version': __version__,
        'python_version': platform.python_version(),
        'pytorch_version': torch.__version__,
        'platform': platform.platform(),
        'cuda_available': torch.cuda.is_available()
    }
    return info

def print_banner():
    """Print welcome banner"""
    print(f"""
Autonomous Racecar Pro v{__version__}
    """)

print_banner()
