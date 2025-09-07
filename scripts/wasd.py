#!/usr/bin/env python3

import smbus
import time
import sys
import tty
import termios
import threading

class ServoController:
    def __init__(self):
        self.bus = smbus.SMBus(7)
        self.address = 0x40
        
        # channels
        self.steering_channel = 0
        self.throttle_channel = 1
        
        # current pos
        self.current_steering = 1500
        self.current_throttle = 1500
        
        # step sizes
        self.steering_step = 25
        self.throttle_step = 50  # even bigger steps
        
        # limits
        self.min_pulse = 1000
        self.max_pulse = 2000
        self.center_pulse = 1500
        
        # throttle limits for my esc
        self.max_forward = 1400
        self.max_reverse = 1600
        
        # terminal stuff
        self.old_settings = None
        
        # refresh thread
        self.keep_refreshing = False
        self.refresh_thread = None
        
        # esc state
        self.esc_armed = False
        self.last_direction = "neutral"
        
        self.init_pca()
        self.init_esc()
        
        print("servo controller ready")

    def init_pca(self):
        # basic pca9685 setup
        self.bus.write_byte_data(self.address, 0x00, 0x10)
        time.sleep(0.005)
        
        prescale = int(25000000 / (4096 * 50) - 1)
        self.bus.write_byte_data(self.address, 0xFE, prescale)
        
        self.bus.write_byte_data(self.address, 0x00, 0x20)
        time.sleep(0.005)
        
        self.bus.write_byte_data(self.address, 0x01, 0x04)
        
        # enable outputs
        self.bus.write_byte_data(self.address, 0xFA, 0x00)
        self.bus.write_byte_data(self.address, 0xFB, 0x00)
        self.bus.write_byte_data(self.address, 0xFC, 0x00)
        self.bus.write_byte_data(self.address, 0xFD, 0x00)
        
        # center steering
        self.set_servo(self.steering_channel, self.center_pulse)

    def init_esc(self):
        # esc startup sequence
        print("arming esc...")
        
        # neutral first
        self.set_servo(self.throttle_channel, self.center_pulse)
        time.sleep(1.0)
        
        # slight forward to arm
        self.set_servo(self.throttle_channel, 1480)
        time.sleep(0.5)
        
        # back to neutral
        self.set_servo(self.throttle_channel, self.center_pulse)
        time.sleep(0.5)
        
        self.esc_armed = True
        print("esc armed")

    def set_servo(self, channel, pulse_us):
        pulse_us = max(self.min_pulse, min(self.max_pulse, pulse_us))
        pwm_val = int((pulse_us * 4096) / 20000)
        base_reg = 0x06 + 4 * channel
        
        try:
            self.bus.write_byte_data(self.address, base_reg, 0)
            self.bus.write_byte_data(self.address, base_reg + 1, 0)
            self.bus.write_byte_data(self.address, base_reg + 2, pwm_val & 0xFF)
            self.bus.write_byte_data(self.address, base_reg + 3, (pwm_val >> 8) & 0xFF)
        except Exception as e:
            print(f"servo error: {e}")

    def reset_esc(self):
        print("resetting esc...")
        
        # neutral for reset
        self.set_servo(self.throttle_channel, self.center_pulse)
        time.sleep(0.3)
        
        # quick rearm
        self.set_servo(self.throttle_channel, 1480)
        time.sleep(0.2)
        
        # back to current position
        self.set_servo(self.throttle_channel, self.current_throttle)
        print("esc reset done")

    def check_direction_change(self, new_throttle):
        # figure out directions
        current_dir = "forward" if self.current_throttle < self.center_pulse else "reverse" if self.current_throttle > self.center_pulse else "neutral"
        new_dir = "forward" if new_throttle < self.center_pulse else "reverse" if new_throttle > self.center_pulse else "neutral"
        
        # reset on direction change
        if (current_dir == "forward" and new_dir == "reverse") or (current_dir == "reverse" and new_dir == "forward"):
            print(f"direction change: {current_dir} -> {new_dir}")
            self.reset_esc()

    def start_refresh(self):
        self.keep_refreshing = True
        def refresh_loop():
            while self.keep_refreshing:
                self.set_servo(self.throttle_channel, self.current_throttle)
                self.set_servo(self.steering_channel, self.current_steering)
                time.sleep(0.02)
        
        self.refresh_thread = threading.Thread(target=refresh_loop, daemon=True)
        self.refresh_thread.start()

    def stop_refresh(self):
        self.keep_refreshing = False

    def setup_terminal(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())

    def restore_terminal(self):
        if self.old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def get_key(self):
        return sys.stdin.read(1).lower()

    def stop_all(self):
        self.current_steering = self.center_pulse
        self.current_throttle = self.center_pulse
        self.set_servo(self.steering_channel, self.current_steering)
        self.set_servo(self.throttle_channel, self.current_throttle)
        print("stopped - all centered")

    def show_status(self):
        # calc percentages
        steering_pct = ((self.current_steering - self.center_pulse) / 500) * 100
        throttle_pct = ((self.current_throttle - self.center_pulse) / 500) * 100
        
        # direction labels
        steer_dir = "LEFT" if steering_pct < -5 else "RIGHT" if steering_pct > 5 else "CENTER"
        throttle_dir = "FORWARD" if throttle_pct < -5 else "REVERSE" if throttle_pct > 5 else "NEUTRAL"
        
        print(f"\rsteering: {self.current_steering}us ({steering_pct:+5.1f}% {steer_dir}) | "
              f"throttle: {self.current_throttle}us ({throttle_pct:+5.1f}% {throttle_dir})",
              end="", flush=True)

    def run_control(self):
        print("\nwasd control active")
        print("w/s = forward/back, a/d = left/right")
        print("space = stop, r = reset esc, q = quit")
        print("make sure car has room to move")
        
        try:
            self.setup_terminal()
            self.start_refresh()
            
            while True:
                key = self.get_key()
                
                if key == 'q':
                    print("\nquitting...")
                    self.stop_all()
                    break
                
                elif key == 'w':
                    # forward
                    new_throttle = self.current_throttle - self.throttle_step
                    new_throttle = max(self.max_forward, new_throttle)
                    self.check_direction_change(new_throttle)
                    self.current_throttle = new_throttle
                    self.set_servo(self.throttle_channel, self.current_throttle)
                
                elif key == 's':
                    # reverse
                    new_throttle = self.current_throttle + self.throttle_step
                    new_throttle = min(self.max_reverse, new_throttle)
                    self.check_direction_change(new_throttle)
                    self.current_throttle = new_throttle
                    self.set_servo(self.throttle_channel, self.current_throttle)
                
                elif key == 'a':
                    # left
                    self.current_steering = max(self.min_pulse, self.current_steering - self.steering_step)
                    self.set_servo(self.steering_channel, self.current_steering)
                
                elif key == 'd':
                    # right
                    self.current_steering = min(self.max_pulse, self.current_steering + self.steering_step)
                    self.set_servo(self.steering_channel, self.current_steering)
                
                elif key == ' ':
                    # stop
                    self.stop_all()
                
                elif key == 'r':
                    # manual esc reset
                    self.reset_esc()
                
                elif key == '+' or key == '=':
                    # bigger steps
                    self.steering_step = min(100, self.steering_step + 5)
                    self.throttle_step = min(100, self.throttle_step + 5)
                    print(f"\nstep size: {self.steering_step}us")
                
                elif key == '-':
                    # smaller steps
                    self.steering_step = max(5, self.steering_step - 5)
                    self.throttle_step = max(5, self.throttle_step - 5)
                    print(f"\nstep size: {self.steering_step}us")
                
                self.show_status()
        
        except KeyboardInterrupt:
            print("\nctrl+c pressed")
            self.stop_all()
        
        except Exception as e:
            print(f"\nerror: {e}")
            self.stop_all()
        
        finally:
            self.stop_refresh()
            self.restore_terminal()
            print("\ncontrol ended")

def main():
    print("wasd servo controller")
    
    response = input("car has space to move? (y/N): ")
    if response.lower() != 'y':
        print("cancelled")
        return
    
    try:
        controller = ServoController()
        controller.run_control()
    except Exception as e:
        print(f"init failed: {e}")

if __name__ == "__main__":
    main()
