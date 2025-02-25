#!/usr/bin/env python3
"""
Launcher script for RD2L Player Stats tool
"""
import os
import sys

# Add the project root to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Define a main function to call player_stats functionality
def main():
    try:
        # Import the module to verify it works first
        from utilities.player_stats import load_hero_mapping, get_player_stats, format_output
        import pandas as pd
        from dotenv import load_dotenv
        
        # Load environment vars and hero mapping
        load_dotenv()
        load_hero_mapping()
        
        print("=" * 60)
        print("Player Stats - View combined stats from OpenDota and Stratz")
        print("=" * 60)
        
        while True:
            # Get player input
            player_input = input("\nEnter player ID or URL (or 'q' to quit): ")
            
            if player_input.lower() in ['q', 'quit', 'exit']:
                break
            
            # Get player stats
            player_stats = get_player_stats(player_input)
            
            if not player_stats.empty:
                # Format and display stats
                formatted_stats = format_output(player_stats)
                print(formatted_stats)
            else:
                print("No stats available for this player.")
            
            print("\n" + "=" * 60)
    except ImportError as e:
        print(f"Error importing player_stats module: {e}")
        print("Make sure you are running this script from the project root directory")
        print(f"Current directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        sys.exit(1)

if __name__ == "__main__":
    main()