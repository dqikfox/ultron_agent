"""Startup validation script for ULTRON Agent"""
from utils.config_validator import validate_config, check_environment
from utils.health_check import system_health_check
from utils.ultron_logger import log_info, log_error

def validate_startup():
    """Run all startup validations"""
    print("=" * 50)
    print("ULTRON Agent Startup Validation")
    print("=" * 50)
    
    # 1. Validate configuration
    print("\n[1/3] Validating configuration...")
    try:
        config = validate_config()
        print("[OK] Configuration valid")
    except Exception as e:
        print(f"[FAIL] Configuration error: {e}")
        return False
    
    # 2. Check environment
    print("\n[2/3] Checking environment...")
    env_checks = check_environment()
    for check, passed in env_checks.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status} {check}")
    
    # 3. System health check
    print("\n[3/3] Running health checks...")
    all_passed, checks = system_health_check()
    
    if all_passed:
        print("\n[SUCCESS] All checks passed - ULTRON Agent ready")
        return True
    else:
        print("\n[WARNING] Some checks failed - review errors above")
        return False

if __name__ == '__main__':
    import sys
    sys.exit(0 if validate_startup() else 1)
