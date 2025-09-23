
# GUI Testing Environment Setup Guide

## For Developers

### Local Development (with GUI)
```bash
# Install required packages
pip install pillow tkinter

# Run with GUI
python stable_diffusion_gui.py
```

### Headless Environments (CI/Docker)
```bash
# Install headless testing dependencies
pip install pillow

# For virtual display (if needed)
sudo apt-get install xvfb
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &

# Run headless tests
python test_gui_headless.py
```

### Testing Strategy
1. **Full GUI Testing**: Available when tkinter and display are present
2. **Import Testing**: Verify modules can be imported without GUI
3. **Mock Testing**: Use mocks for GUI components in unit tests
4. **Integration Testing**: Test API endpoints and business logic

### Environment Detection
The system automatically detects:
- Display availability (DISPLAY environment variable)
- tkinter module availability  
- PIL/Pillow availability
- CI environment markers

### Fallback Behavior
- GUI components gracefully fallback to headless mode
- Critical functionality remains testable
- Clear error messages guide users to solutions
