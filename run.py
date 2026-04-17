#!/usr/bin/env python3
# Cyber Scanner Loader - Full Version

import sys
import os

# .so ဖိုင်ရှိလား စစ်မယ်
so_files = [f for f in os.listdir('.') if f.endswith('.so')]
if not so_files:
    print("Error: .so file not found!")
    sys.exit(1)

# import လုပ်မယ်
module_name = so_files[0].replace('.cpython-311.so', '').replace('.so', '')
scanner = __import__(module_name)

# Scanner စမယ်
try:
    # Option 1: main() ရှိရင်
    if hasattr(scanner, 'main'):
        scanner.main()
    # Option 2: run_scanner() ရှိရင် (license မပါ)
    elif hasattr(scanner, 'run_scanner'):
        print("Warning: License verification may be skipped!")
        scanner.run_scanner()
    # Option 3: original main logic ကိုယ်တိုင်လုပ်
    else:
        if hasattr(scanner, 'verify_key') and hasattr(scanner, 'run_scanner'):
            if scanner.verify_key():
                scanner.run_scanner()
        else:
            print("Error: No valid entry point found")
            print(f"Available: {dir(scanner)}")
except KeyboardInterrupt:
    print("\n[!] Stopped by user")
except Exception as e:
    print(f"[!] Error: {e}")