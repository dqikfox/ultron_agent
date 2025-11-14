#!/usr/bin/env python3
"""GUI File Integrity Monitor for ULTRON AETHER NEXUS INTERFACE"""
import os
import hashlib
import json
from datetime import datetime
from pathlib import Path

GUI_FILES = {
    'index.html': 'gui/ultron_enhanced/web/index.html',
    'app.js': 'gui/ultron_enhanced/web/app.js',
    'styles.css': 'gui/ultron_enhanced/web/styles.css'
}

INTEGRITY_FILE = 'gui/ultron_enhanced/web/.integrity.json'
MIN_SIZE_THRESHOLD = 0.5  # Alert if file shrinks by >50%

def get_file_hash(filepath):
    """Calculate SHA256 hash of file"""
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def save_integrity():
    """Save current state as integrity baseline"""
    integrity = {
        'timestamp': datetime.now().isoformat(),
        'files': {}
    }
    
    for name, path in GUI_FILES.items():
        if os.path.exists(path):
            integrity['files'][name] = {
                'hash': get_file_hash(path),
                'size': os.path.getsize(path),
                'modified': datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
            }
            print(f"✓ Saved baseline: {name} ({integrity['files'][name]['size']} bytes)")
        else:
            print(f"⚠ File not found: {name}")
    
    os.makedirs(os.path.dirname(INTEGRITY_FILE), exist_ok=True)
    with open(INTEGRITY_FILE, 'w') as f:
        json.dump(integrity, f, indent=2)
    
    print(f"\n✓ Integrity baseline saved: {INTEGRITY_FILE}")

def check_integrity():
    """Check current state against baseline"""
    if not os.path.exists(INTEGRITY_FILE):
        print("⚠ No integrity baseline found.")
        print("Run with --save to create baseline:")
        print("  python monitor_gui.py --save")
        return False
    
    with open(INTEGRITY_FILE) as f:
        baseline = json.load(f)
    
    print(f"Baseline: {baseline['timestamp']}\n")
    
    issues = []
    warnings = []
    
    for name, path in GUI_FILES.items():
        if not os.path.exists(path):
            issues.append(f"❌ MISSING: {name}")
            continue
        
        current_hash = get_file_hash(path)
        current_size = os.path.getsize(path)
        
        if name in baseline['files']:
            baseline_hash = baseline['files'][name]['hash']
            baseline_size = baseline['files'][name]['size']
            
            if current_hash != baseline_hash:
                warnings.append(f"⚠ MODIFIED: {name}")
            
            if current_size < baseline_size * MIN_SIZE_THRESHOLD:
                issues.append(f"🚨 SIZE REDUCED >50%: {name} ({baseline_size} → {current_size} bytes)")
            elif current_size != baseline_size:
                warnings.append(f"📊 SIZE CHANGED: {name} ({baseline_size} → {current_size} bytes)")
            
            print(f"{'✓' if current_hash == baseline_hash else '⚠'} {name}: {current_size} bytes")
        else:
            warnings.append(f"🆕 NEW FILE: {name}")
    
    print()
    
    if issues:
        print("🚨 CRITICAL ISSUES:")
        for issue in issues:
            print(f"  {issue}")
        print()
    
    if warnings:
        print("⚠ WARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
        print()
    
    if not issues and not warnings:
        print("✓ All GUI files intact - no changes detected")
        return True
    elif issues:
        print("❌ INTEGRITY CHECK FAILED - Critical issues detected!")
        return False
    else:
        print("⚠ INTEGRITY CHECK WARNING - Files modified")
        return True

if __name__ == '__main__':
    import sys
    
    print("═" * 60)
    print("  ULTRON GUI INTEGRITY MONITOR")
    print("═" * 60)
    print()
    
    if '--save' in sys.argv or '-s' in sys.argv:
        save_integrity()
    else:
        success = check_integrity()
        sys.exit(0 if success else 1)
