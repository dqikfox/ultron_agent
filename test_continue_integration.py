# Test Continue Extension Integration

def test_ultron_automation():
    """
    Test function for Continue extension to analyze.
    This demonstrates the Ultron automation capabilities.
    """
    import pyautogui
    import time
    
    # Safety configuration
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    
    def move_mouse_smooth(x, y, duration=1.0):
        """Move mouse smoothly to coordinates"""
        pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeInOutQuad)
        return f"Moved mouse to ({x}, {y})"
    
    def take_screenshot_with_timestamp():
        """Take screenshot with timestamp"""
        timestamp = int(time.time())
        filename = f"ultron_screenshot_{timestamp}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return f"Screenshot saved as {filename}"
    
    def get_pixel_analysis(x, y):
        """Analyze pixel color at coordinates"""
        pixel = pyautogui.pixel(x, y)
        if hasattr(pixel, 'red'):
            return f"Pixel at ({x}, {y}): RGB({pixel.red}, {pixel.green}, {pixel.blue})"
        else:
            return f"Pixel at ({x}, {y}): RGB({pixel[0]}, {pixel[1]}, {pixel[2]})"
    
    # Test automation features
    results = []
    results.append(move_mouse_smooth(500, 300))
    results.append(take_screenshot_with_timestamp())
    results.append(get_pixel_analysis(100, 100))
    
    return results

# Ask Continue to analyze this code!
