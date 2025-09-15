# Autonomous Racecar Pro

Autonomous racing car system.

## Quick Start

1. **Install package**: `pip install -e .`
2. **Hardware setup**: `python scripts/setup_hardware.py`
3. **Collect data**: `python scripts/collect_data.py`
4. **Train model**: `python scripts/train_model.py`
5. **Autonomous drive**: `python scripts/autonomous_drive.py`

## Project Structure

```
Autonomous-Racecar-Pro/
├── src/autonomous_racecar/     # Main Python package
├── data/                       # Data storage
├── notebooks/                  # Interactive development
├── scripts/                    # Standalone scripts
└── config/                     # Configuration files
```

## Features

- Modular hardware interfaces
- Rapid data collection system  
- Training pipeline
- Safe autonomous driving
- Comprehensive testing
- Config managment


## Commands

- Live camera feed(THIS WILL NOT WORK IF YOU ARE USING SECURE SHELL) - gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM),width=640,height=480' ! nvvidconv ! autovideosink
- Check if cam is recognized - ls /dev/video0*
- Open Jupyter - jupyter lab --ip=0.0.0.0 --port=8888 --allow-root
- shut down orin - sudo shutdown -h now
- check for camera usage - sudo dmesg | tail -20 | grep -i imx219 and sudo dmesg | tail -20 | grep -i camera
