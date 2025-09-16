import cffi
import os
import sys
from pathlib import Path

def test_dll_loading():
    """Test DLL loading with detailed error reporting"""

    ffi = cffi.FFI()

    # Define minimal interface first
    ffi.cdef("""
        void list_host_apis(void);
        bool is_audio_device_ready(void);
    """)

    dll_path = "./libaudio.dll"

    print(f"Testing DLL: {dll_path}")
    print(f"DLL exists: {os.path.exists(dll_path)}")

    if os.path.exists(dll_path):
        print(f"DLL size: {os.path.getsize(dll_path)} bytes")

    try:
        # Try to load the DLL
        print("Attempting to load DLL...")
        lib = ffi.dlopen(dll_path)
        print("✓ DLL loaded successfully!")

        # Try to call a simple function
        print("Testing function call...")
        ready = lib.is_audio_device_ready()
        print(f"✓ Function call successful: {ready}")

        # Try calling list_host_apis (this initializes PortAudio)
        print("Testing list_host_apis...")
        lib.list_host_apis()
        print("✓ list_host_apis completed")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        print(f"Error type: {type(e).__name__}")

        # Additional debugging
        if "GetLastError" in str(e):
            import ctypes
            error_code = ctypes.windll.kernel32.GetLastError()
            print(f"Windows error code: 0x{error_code:x} ({error_code})")

        return False

if __name__ == "__main__":
    success = test_dll_loading()
    if not success:
        print("\nDebugging steps:")
        print("1. Check DLL dependencies with: python check_deps.py")
        print("2. Ensure all required DLLs are in PATH or same directory")
        print("3. Verify DLL architecture matches Python (64-bit)")
        print("4. Try the minimal test_dll.dll first")
