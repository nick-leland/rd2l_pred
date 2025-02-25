#!/usr/bin/env python3
"""
Launcher script for RD2L Team Scout tool
"""
import os
import sys

# Add the project root to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Import and run the actual tool
try:
    from utilities.team_scout import main
    main()
except ImportError as e:
    print(f"Error importing team_scout module: {e}")
    print("Make sure you are running this script from the project root directory")
    sys.exit(1)