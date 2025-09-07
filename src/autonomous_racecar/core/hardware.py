#src/autonomous_racecar/core/hardware.py
#CHANGE CALLIBRATIONS FOR YOUR SYSTEM

import time
import smbus
from typing import Optional

class AutonomousRacecar:
    """
    Main hardware interface with personal calibrations(change as needed)
    steering_offset=0.17, steering_gain=-0.65, throttle_gain=0.8
    """
    
    def __init__(self, 
                 steering_offset: float = 0.17, 
                 steering_gain: float = -0.65, 
                 throttle_gain: float = 0.8):
        """Initialize with your calibrated values"""
        
        self.steering_offset = steering_offset
        self.steering_gain = steering_gain  
        self.throttle_gain = throttle_gain
        
        #i2c setup
        self.i2c_address = 0x40
        self.steering_channel = 0
        self.throttle_channel = 1
        self.center_pulse = 1500
        
        #values
        self._steering = 0.0
        self._throttle = 0.0
        
        #Setup hardware
        self._init_hardware()
        
        print(f"racecar ready")
        print(f"steering offset: {self.steering_offset}")
        print(f"steering gain: {self.steering_gain}")
        print(f"throttle gain: {self.throttle_gain}")
    
    def _init_hardware(self):
        """Initialize i2c and pca9685"""
        try:
            #initialize the i2c bus
            self.bus = smbus.SMBus(7)
            
            #pca9685 pwm controller initialization
            self.bus.write_byte_data(self.i2c_address, 0x00, 0x10)
            time.sleep(0.005)
            
            #50hz pwm frequency
            prescale = int(25000000 / (4096 * 50) - 1)
            self.bus.write_byte_data(self.i2c_address, 0xFE, prescale)
            self.bus.write_byte_data(self.i2c_address, 0x00, 0x20)
            time.sleep(0.005)
            self.bus.write_byte_data(self.i2c_address, 0x01, 0x04)
            
            #servo center initialization
            self._set_servo_pulse(self.steering_channel, self.center_pulse)
            self._set_servo_pulse(self.throttle_channel, self.center_pulse)
            
        except Exception as e:
            print(f"hardware initialization failed: {e}")
            raise
    
    def _set_servo_pulse(self, channel: int, pulse_us: int):
        """Set servo pulse width in microseconds"""
        #safety
        pulse_us = max(1000, min(2000, pulse_us))
        
        #convert to pwm  value
        pwm_value = int((pulse_us * 4096) / 20000)
        base_reg = 0x06 + 4 * channel
        
        try:
            self.bus.write_byte_data(self.i2c_address, base_reg, 0)
            self.bus.write_byte_data(self.i2c_address, base_reg + 1, 0)
            self.bus.write_byte_data(self.i2c_address, base_reg + 2, pwm_value & 0xFF)
            self.bus.write_byte_data(self.i2c_address, base_reg + 3, (pwm_value >> 8) & 0xFF)
        except Exception as e:
            print(f"servo control error: {e}")
    
    @property
    def steering(self) -> float:
        """get current stering value (-1.0 to 1.0)"""
        return self._steering
    
    @steering.setter
    def steering(self, value: float):
        """set steering val (-1.0 to 1.0)"""
        #safety
        value = max(-1.0, min(1.0, value))
        self._steering = value
        
        #apply calibration
        scaled = value * self.steering_gain + self.steering_offset
        pulse_us = self.center_pulse + (scaled * 500)
        
        self._set_servo_pulse(self.steering_channel, pulse_us)
    
    @property
    def throttle(self) -> float:
        """get current throttle val (-1.0 to 1.0)"""
        return self._throttle
    
    @throttle.setter
    def throttle(self, value: float):
        """set throttle val (-1.0 to 1.0)"""
        #safety
        value = max(-1.0, min(1.0, value))
        self._throttle = value
        
        #apply callibration
        scaled = value * self.throttle_gain
        
        if scaled > 0:
            pulse_us = self.center_pulse - (scaled * 200)
        elif scaled < 0:
            pulse_us = self.center_pulse + (abs(scaled) * 200)
        else:
            pulse_us = self.center_pulse
        
        self._set_servo_pulse(self.throttle_channel, pulse_us)
    
    def stop(self):
        """safely stop the car"""
        self.throttle = 0.0
        self.steering = 0.0
        time.sleep(0.1)
    
    def test_steering(self, duration: float = 2.0):
        """test steering calibration"""
        print("testing steering")
        
        original = self.steering
        
        self.steering = 0.0
        print("straight")
        time.sleep(duration)
        
        self.steering = 0.5
        print("right turn")
        time.sleep(duration)
        
        self.steering = -0.5
        print("left turn")
        time.sleep(duration)
        
        self.steering = 0.0
        print("back to straight")
        time.sleep(duration)
        
        self.steering = original
        print("steering test complete")
    
    def test_throttle(self, duration: float = 1.0):
        """test throttle calibration"""
        print("testing throttle")
        
        original = self.throttle
        
        self.throttle = 0.0
        print("neutral")
        time.sleep(duration)
        
        self.throttle = 0.2
        print("slow forward")
        time.sleep(duration)
        
        self.throttle = 0.0
        print("neutral")
        time.sleep(duration)
        
        self.throttle = original
        print("throttle test complete")
    
    def __enter__(self):
        """context entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """context safe exit"""
        self.stop()


#easy functions
def create_car(steering_offset: float = 0.17) -> AutonomousRacecar:
    """Create a calibrated Autonomous Racecar instance"""
    return AutonomousRacecar(steering_offset=steering_offset)

def test_hardware() -> bool:
    """hardware test"""
    try:
        print("running tests")
        with create_car() as car:
            car.test_steering(duration=1.0)
            car.test_throttle(duration=0.5)
            print("hardware working")
            return True
    except Exception as e:
        print(f"hardware test failed: {e}")
        return False
