#src/autonomous_racecar/core/sys_test.py
#SYSTEM TESTS

import time

def test_hardware():
    """test hardware system"""
    print("testing hardware")
    
    try:
        from .hardware import create_car
        
        print("creating car with calibrations")
        car = create_car(steering_offset=0.17)
        
        print("testing steering")
        car.test_steering(duration=0.5)
        
        print("testing throttle") 
        car.test_throttle(duration=0.3)
        
        car.stop()
        print("hardware test passed")
        return True
        
    except Exception as e:
        print(f"hardware test failed: {e}")
        return False

def test_camera():
    """test camera system"""
    print("testing camera")
    
    try:
        from .camera import test_camera
        
        if test_camera(mode='debug'):
            print("camera test passed")
            return True
        else:
            print("camera test failed")
            return False
            
    except Exception as e:
        print(f"camera test failed: {e}")
        return False

def test_integration():
    """test hardware + camera together"""
    print("testing integration")
    
    try:
        from .hardware import create_car
        from .camera import create_inference_camera
        
        car = create_car(steering_offset=0.17)
        camera = create_inference_camera()
        
        if camera.start():
            print("camera started")
            
            #test autonomous-ready loop
            for i in range(3):
                img = camera.read()
                if img is not None:
                    print(f"frame {i+1}: {img.shape}")
                    
                    #simulate ai steering
                    ai_steering = 0.1 if i == 1 else 0.0
                    car.steering = ai_steering
                    print(f"steering: {ai_steering}")
                    time.sleep(0.5)
            
            car.stop()
            camera.stop()
            print("integration test passed")
            return True
        else:
            print("camera failed to start")
            return False
            
    except Exception as e:
        print(f"integration test failed: {e}")
        return False

def run_all_tests():
    """run complete system test"""
    print("SYSTEM TEST")
    print("=" * 20)
    
    tests = [
        ("hardware", test_hardware),
        ("camera", test_camera), 
        ("integration", test_integration)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n--- {test_name} test ---")
        if test_func():
            passed += 1
        else:
            print(f"{test_name} test failed")
    
    print(f"\n--- results ---")
    print(f"passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("all tests passed")
        print("system ready")
        return True
    else:
        print("some tests failed")
        return False

def quick_test():
    """quick hardware + camera test"""
    print("quick system test")
    
    #quick hardware test
    try:
        from .hardware import create_car
        car = create_car()
        car.steering = 0.0
        car.stop()
        print("hardware: ok")
    except Exception as e:
        print(f"hardware: failed - {e}")
        return False
    
    #quick camera test
    try:
        from .camera import create_debug_camera
        camera = create_debug_camera()
        if camera.start():
            img = camera.read()
            camera.stop()
            if img is not None:
                print(f"camera: ok - {img.shape}")
            else:
                print("camera: no image")
                return False
        else:
            print("camera: failed to start")
            return False
    except Exception as e:
        print(f"camera: failed - {e}")
        return False
    
    print("quick test passed")
    return True

#make it easy to run
if __name__ == "__main__":
    run_all_tests()
