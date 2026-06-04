import sys
try:
    from app.main import app
    print("APP IMPORT OK")
    sys.exit(0)
except Exception as e:
    print(f"APP IMPORT FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)