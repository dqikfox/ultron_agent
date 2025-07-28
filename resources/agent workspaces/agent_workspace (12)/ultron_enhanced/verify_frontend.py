#!/usr/bin/env python3
"""
Verify ULTRON frontend assets and configuration
Checks that all required files are in place and properly configured
"""

import os
import json
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and report status"""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"✅ {description}: {file_path} ({size} bytes)")
        return True
    else:
        print(f"❌ {description}: {file_path} (MISSING)")
        return False

def verify_web_assets():
    """Verify all web assets are in place"""
    print("🔍 Verifying ULTRON web assets...\n")
    
    base_dir = os.path.dirname(__file__)
    web_dir = os.path.join(base_dir, "web")
    assets_dir = os.path.join(web_dir, "assets")
    
    # Core web files
    core_files = [
        (os.path.join(web_dir, "index.html"), "Main HTML file"),
        (os.path.join(web_dir, "styles.css"), "Stylesheet"),
        (os.path.join(web_dir, "app.js"), "JavaScript application"),
    ]
    
    # Asset files
    asset_files = [
        (os.path.join(assets_dir, "sounds.js"), "Sound system"),
        (os.path.join(assets_dir, "favicon.ico"), "Favicon ICO"),
        (os.path.join(assets_dir, "favicon.png"), "Favicon PNG"),
        (os.path.join(assets_dir, "wake.wav"), "Wake sound"),
        (os.path.join(assets_dir, "button_press.wav"), "Button sound"),
        (os.path.join(assets_dir, "confirm.wav"), "Confirm sound"),
    ]
    
    print("📁 Core Web Files:")
    core_ok = all(check_file_exists(path, desc) for path, desc in core_files)
    
    print("\n🎵 Asset Files:")
    assets_ok = all(check_file_exists(path, desc) for path, desc in asset_files)
    
    return core_ok and assets_ok

def verify_html_includes():
    """Verify HTML includes required scripts and assets"""
    print("\n🔍 Verifying HTML configuration...")
    
    html_path = os.path.join(os.path.dirname(__file__), "web", "index.html")
    
    if not os.path.exists(html_path):
        print("❌ index.html not found")
        return False
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    checks = [
        ('favicon.ico', 'favicon.ico' in html_content),
        ('favicon.png', 'favicon.png' in html_content),
        ('sounds.js script', 'sounds.js' in html_content),
        ('app.js script', 'app.js' in html_content),
        ('Audio elements', 'audio id=' in html_content),
    ]
    
    all_good = True
    for check_name, condition in checks:
        if condition:
            print(f"✅ {check_name} properly included")
        else:
            print(f"❌ {check_name} missing or incorrect")
            all_good = False
    
    return all_good

def verify_api_endpoints():
    """Check if API endpoints are properly defined"""
    print("\n🔍 Verifying API configuration...")
    
    app_js_path = os.path.join(os.path.dirname(__file__), "web", "app.js")
    
    if not os.path.exists(app_js_path):
        print("❌ app.js not found")
        return False
    
    with open(app_js_path, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    api_checks = [
        ('/api/status', '/api/status' in js_content),
        ('Backend ready check', 'waitForBackendReady' in js_content),
        ('Sound fallback', 'playGeneratedSound' in js_content),
        ('Connection status', 'updateConnectionStatus' in js_content),
    ]
    
    all_good = True
    for check_name, condition in api_checks:
        if condition:
            print(f"✅ {check_name} implemented")
        else:
            print(f"❌ {check_name} missing")
            all_good = False
    
    return all_good

def verify_backend_endpoints():
    """Check if backend properly supports required endpoints"""
    print("\n🔍 Verifying backend API support...")
    
    web_server_path = os.path.join(os.path.dirname(__file__), "core", "web_server.py")
    
    if not os.path.exists(web_server_path):
        print("❌ web_server.py not found")
        return False
    
    with open(web_server_path, 'r', encoding='utf-8') as f:
        server_content = f.read()
    
    endpoint_checks = [
        ('/api/status endpoint', "'api/status'" in server_content),
        ('Status handler', '_handle_status' in server_content),
        ('Static file serving', 'super().do_GET()' in server_content),
        ('JSON responses', 'application/json' in server_content),
    ]
    
    all_good = True
    for check_name, condition in endpoint_checks:
        if condition:
            print(f"✅ {check_name} supported")
        else:
            print(f"❌ {check_name} missing")
            all_good = False
    
    return all_good

def provide_recommendations():
    """Provide recommendations for any issues found"""
    print("\n💡 Recommendations:")
    print("1. Ensure all audio files are accessible via HTTP")
    print("2. Test the /api/status endpoint manually: http://localhost:3000/api/status")
    print("3. Check browser console for JavaScript errors")
    print("4. Verify sounds.js loads before app.js")
    print("5. Test with browser audio enabled (not muted)")
    
def main():
    """Main verification function"""
    print("=" * 60)
    print("🔧 ULTRON FRONTEND VERIFICATION")
    print("=" * 60)
    
    # Run all verifications
    assets_ok = verify_web_assets()
    html_ok = verify_html_includes()
    js_ok = verify_api_endpoints()
    backend_ok = verify_backend_endpoints()
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    results = [
        ("Web Assets", assets_ok),
        ("HTML Configuration", html_ok),
        ("JavaScript API Integration", js_ok),
        ("Backend Endpoint Support", backend_ok),
    ]
    
    overall_status = all(result for _, result in results)
    
    for category, status in results:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {category}: {'PASS' if status else 'FAIL'}")
    
    print("\n" + "=" * 60)
    if overall_status:
        print("🎉 ALL VERIFICATIONS PASSED!")
        print("Frontend should work correctly with proper backend connection.")
    else:
        print("⚠️  SOME ISSUES FOUND")
        print("Please address the failing items above.")
        provide_recommendations()
    
    print("=" * 60)
    
    return overall_status

if __name__ == "__main__":
    main()
