import ctypes
import ctypes.wintypes
import os
import sys
from pathlib import Path
import struct

# Windows API constants
LOAD_LIBRARY_AS_DATAFILE = 0x00000002
DONT_RESOLVE_DLL_REFERENCES = 0x00000001

def check_dll_architecture(dll_path):
    """Check if DLL is 32-bit or 64-bit"""
    try:
        with open(dll_path, 'rb') as f:
            # Read DOS header
            dos_header = f.read(64)
            if dos_header[:2] != b'MZ':
                return "Not a valid PE file"

            # Get PE header offset
            pe_offset = struct.unpack('<L', dos_header[60:64])[0]
            f.seek(pe_offset)

            # Read PE signature and COFF header
            pe_sig = f.read(4)
            if pe_sig != b'PE\x00\x00':
                return "Not a valid PE file"

            machine = struct.unpack('<H', f.read(2))[0]

            if machine == 0x014c:
                return "32-bit (i386)"
            elif machine == 0x8664:
                return "64-bit (AMD64)"
            else:
                return f"Unknown architecture (0x{machine:04x})"

    except Exception as e:
        return f"Error reading file: {e}"

def check_dll_dependencies_windows(dll_path):
    """Check DLL dependencies using Windows API"""

    print(f"Analyzing: {dll_path}")

    if not os.path.exists(dll_path):
        print(f"ERROR: {dll_path} not found!")
        return

    # Check basic file info
    size = os.path.getsize(dll_path)
    arch = check_dll_architecture(dll_path)
    print(f"DLL Size: {size} bytes")
    print(f"Architecture: {arch}")

    # Try to load the DLL to check for missing dependencies
    kernel32 = ctypes.windll.kernel32

    print("\n=== Dependency Check ===")

    # Try loading with DONT_RESOLVE_DLL_REFERENCES to avoid initializing
    try:
        handle = kernel32.LoadLibraryExW(
            ctypes.c_wchar_p(dll_path),
            None,
            LOAD_LIBRARY_AS_DATAFILE | DONT_RESOLVE_DLL_REFERENCES
        )

        if handle:
            print("✓ DLL can be loaded as data file")
            kernel32.FreeLibrary(handle)
        else:
            error = kernel32.GetLastError()
            print(f"✗ Failed to load as data file. Error: 0x{error:x}")

    except Exception as e:
        print(f"✗ Exception during data file load: {e}")

    # Try normal loading
    try:
        handle = kernel32.LoadLibraryW(ctypes.c_wchar_p(dll_path))
        if handle:
            print("✓ DLL loads successfully with full resolution")
            kernel32.FreeLibrary(handle)
        else:
            error = kernel32.GetLastError()
            print(f"✗ Failed to load DLL normally. Error: 0x{error:x}")
            print_windows_error(error)

    except Exception as e:
        print(f"✗ Exception during normal load: {e}")

def print_windows_error(error_code):
    """Print human-readable Windows error message"""
    error_messages = {
        0x7e: "The specified module could not be found",
        0x57: "The parameter is incorrect",
        0x7f: "The specified procedure could not be found",
        0xc1: "The application cannot run in Win32 mode",
        0x485: "Attempt to access invalid address",
    }

    if error_code in error_messages:
        print(f"   Meaning: {error_messages[error_code]}")

    # Try to get system error message
    try:
        import ctypes.wintypes
        kernel32 = ctypes.windll.kernel32

        buffer = ctypes.create_unicode_buffer(512)
        kernel32.FormatMessageW(
            0x00001000,  # FORMAT_MESSAGE_FROM_SYSTEM
            None,
            error_code,
            0,
            buffer,
            512,
            None
        )

        if buffer.value:
            print(f"   System message: {buffer.value.strip()}")

    except:
        pass

def check_python_architecture():
    """Check if Python is 32-bit or 64-bit"""
    import platform
    return platform.architecture()[0]

def test_cffi_loading(dll_path):
    """Test CFFI loading specifically"""
    print("\n=== CFFI Loading Test ===")

    try:
        import cffi
        ffi = cffi.FFI()

        # Try to load without any function definitions
        print("Testing CFFI dlopen...")
        lib = ffi.dlopen(dll_path)
        print("✓ CFFI can load the DLL")

        # Test with a simple function definition
        ffi.cdef("void list_host_apis(void);")
        lib = ffi.dlopen(dll_path)
        print("✓ CFFI can load with function definition")

        return True

    except Exception as e:
        print(f"✗ CFFI loading failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    dll_path = "libaudio.dll"
    if len(sys.argv) > 1:
        dll_path = sys.argv[1]

    print(f"Python Architecture: {check_python_architecture()}")
    print()

    check_dll_dependencies_windows(dll_path)
    test_cffi_loading(dll_path)
