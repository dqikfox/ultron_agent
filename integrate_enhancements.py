"""Integration script for ULTRON Agent enhancements"""
import shutil
from pathlib import Path

def backup_file(filepath):
    """Create backup of file before modification"""
    if Path(filepath).exists():
        backup = f"{filepath}.backup"
        shutil.copy2(filepath, backup)
        print(f"✓ Backed up {filepath} to {backup}")

def integrate_enhancements():
    """Integrate enhancements into existing codebase"""
    print("=" * 60)
    print("ULTRON Agent Enhancement Integration")
    print("=" * 60)
    
    # Step 1: Backup critical files
    print("\n[1/4] Creating backups...")
    files_to_backup = ['Ultron_Live.py', 'run.bat', 'main.py']
    for file in files_to_backup:
        backup_file(file)
    
    # Step 2: Run tests
    print("\n[2/4] Running enhancement tests...")
    import subprocess
    result = subprocess.run(['pytest', 'tests/test_enhancements.py', '-v'], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    if result.returncode != 0:
        print("⚠ Some tests failed. Review before proceeding.")
        return False
    
    # Step 3: Validate startup
    print("\n[3/4] Running startup validation...")
    result = subprocess.run(['python', 'startup_validator.py'], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    # Step 4: Integration instructions
    print("\n[4/4] Manual integration required:")
    print("""
    Add to Ultron_Live.py (after imports):
    
    from utils.error_recovery import retry_on_failure
    from utils.command_history import CommandHistory
    from utils.performance_tracker import track_performance
    
    # Initialize (after engine setup)
    command_history = CommandHistory()
    
    # Wrap execute function:
    @retry_on_failure(max_retries=3)
    @track_performance
    def execute(command):
        # ... existing code ...
        command_history.add(command, result)
        return result
    """)
    
    print("\n✓ Integration preparation complete!")
    print("Review ENHANCEMENTS.md for detailed instructions.")
    return True

if __name__ == '__main__':
    integrate_enhancements()
