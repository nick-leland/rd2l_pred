#!/usr/bin/env python3
"""
Player Stats - A tool to view combined stats from OpenDota and Stratz for a Dota 2 player
"""

import pandas as pd
import re
import os
import time
import json
import requests
from dotenv import load_dotenv

# Import feature engineering functions
from feature_engineering import hero_information, get_stratz_features, combine_features

# Check if Stratz module is available
try:
    import stratz
    STRATZ_AVAILABLE = True
except ImportError:
    STRATZ_AVAILABLE = False

# Global variables
HERO_MAPPING = {}

# RD2L league IDs for different seasons
RD2L_LEAGUE_IDS = [16436, 16435, 16434, 15578, 15577, 15246, 14906, 14507, 14137, 13780, 13375, 13185, 12762, 11984]

def load_hero_mapping():
    """
    Load hero ID to name mapping from OpenDota API or local cache.
    """
    global HERO_MAPPING
    
    # Path for cached mapping
    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hero_mapping.json')
    
    # Try to load from cache first
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r') as f:
                HERO_MAPPING = json.load(f)
                print(f"Loaded {len(HERO_MAPPING)} heroes from cache.")
                return
        except Exception as e:
            print(f"Error loading hero cache: {e}")
    
    # If cache doesn't exist or failed to load, fetch from API
    try:
        print("Fetching hero data from OpenDota API...")
        response = requests.get("https://api.opendota.com/api/heroes")
        if response.status_code == 200:
            heroes = response.json()
            # Create mapping from ID to name
            HERO_MAPPING = {str(hero['id']): hero['localized_name'] for hero in heroes}
            
            # Save to cache for future use
            with open(cache_path, 'w') as f:
                json.dump(HERO_MAPPING, f)
                
            print(f"Fetched and cached {len(HERO_MAPPING)} heroes.")
        else:
            print(f"Failed to fetch heroes: {response.status_code}")
    except Exception as e:
        print(f"Error fetching hero data: {e}")
        
    # If still empty, provide a small default mapping for common heroes
    if not HERO_MAPPING:
        print("Using default hero mapping...")
        HERO_MAPPING = {
            "1": "Anti-Mage", "2": "Axe", "3": "Bane", "4": "Bloodseeker", "5": "Crystal Maiden",
            "6": "Drow Ranger", "7": "Earthshaker", "8": "Juggernaut", "9": "Mirana", "10": "Morphling",
            "11": "Shadow Fiend", "12": "Phantom Lancer", "13": "Puck", "14": "Pudge", "15": "Razor",
            "16": "Sand King", "17": "Storm Spirit", "18": "Sven", "19": "Tiny", "20": "Vengeful Spirit"
        }

def get_hero_name(hero_id):
    """Get hero name from ID, returning ID if not found."""
    if not HERO_MAPPING:
        load_hero_mapping()
    
    hero_id = str(hero_id)
    return HERO_MAPPING.get(hero_id, f"Hero {hero_id}")


def extract_player_id(input_str):
    """
    Extract player ID from various input formats.
    
    Args:
        input_str (str): Player ID or URL containing player ID
        
    Returns:
        str: Extracted player ID
    """
    # If input is just a number, return it
    if input_str.isdigit():
        return input_str
    
    # Try to extract from URL
    patterns = [
        r'dotabuff\.com/players/(\d+)',  # Dotabuff
        r'opendota\.com/players/(\d+)',  # OpenDota
        r'stratz\.com/players/(\d+)'     # Stratz
    ]
    
    for pattern in patterns:
        match = re.search(pattern, input_str)
        if match:
            return match.group(1)
    
    # If no match found
    raise ValueError("Could not extract player ID from input. Please provide a valid player ID or URL.")


def format_output(player_series):
    """
    Format player stats for readable terminal output.
    
    Args:
        player_series (pd.Series): Series containing player stats
        
    Returns:
        str: Formatted string for terminal output
    """
    # Extract name for title
    player_name = player_series.get('player_name', 'Unknown Player')
    player_id = player_series.get('player_id', 'Unknown ID')
    
    # Create title
    output = [f"\n==== Player Stats: {player_name} (ID: {player_id}) ===="]
    
    # Group stats by category
    categories = {
        "General Info": ['total_games_played', 'total_winrate'],
        "Stratz Performance": [col for col in player_series.index if col.startswith('stratz_') and 
                              col not in ['stratz_player_id', 'stratz_player_name', 'stratz_has_rd2l_experience', 
                                         'stratz_rd2l_match_count', 'stratz_first_rd2l_match', 'stratz_last_rd2l_match', 
                                         'stratz_top_heroes']],
        "RD2L Experience": ['stratz_has_rd2l_experience', 'stratz_rd2l_match_count', 
                           'stratz_first_rd2l_match', 'stratz_last_rd2l_match'] 
    }
    
    # Format each category
    for category, fields in categories.items():
        category_fields = [f for f in fields if f in player_series.index]
        if category_fields:
            output.append(f"\n=== {category} ===")
            for field in category_fields:
                value = player_series.get(field, "N/A")
                
                # Format percentages
                if 'rate' in field and isinstance(value, float):
                    value = f"{value:.2%}"
                # Format timestamps
                elif field in ['stratz_first_rd2l_match', 'stratz_last_rd2l_match'] and value:
                    try:
                        # Convert Unix timestamp to readable date
                        from datetime import datetime
                        date_str = datetime.fromtimestamp(value).strftime('%Y-%m-%d')
                        value = date_str
                    except:
                        pass
                # Format floats with precision
                elif isinstance(value, float):
                    value = f"{value:.2f}"
                
                # Clean up field names for display
                display_name = field.replace('stratz_', '').replace('_', ' ').title()
                output.append(f"{display_name}: {value}")
    
    # Add top heroes section if available
    if 'stratz_top_heroes' in player_series.index:
        output.append("\n=== Top Heroes by Performance (Stratz) ===")
        hero_ids = player_series['stratz_top_heroes']
        if isinstance(hero_ids, list):
            for i, hero_id in enumerate(hero_ids[:5], 1):
                hero_name = get_hero_name(hero_id)
                output.append(f"{i}. {hero_name}")
    
    # Add most played heroes from OpenDota
    hero_games_cols = [col for col in player_series.index if col.startswith('games_')]
    if hero_games_cols:
        hero_games = {col.split('_')[1]: player_series[col] for col in hero_games_cols if player_series[col] > 0}
        if hero_games:
            output.append("\n=== Most Played Heroes (OpenDota) ===")
            # Sort by games played
            sorted_heroes = sorted(hero_games.items(), key=lambda x: x[1], reverse=True)
            for i, (hero_id, games) in enumerate(sorted_heroes[:5], 1):
                hero_name = get_hero_name(hero_id)
                winrate_col = f"winrate_{hero_id}"
                winrate = player_series.get(winrate_col, 0)
                winrate_str = f"{winrate:.2%}" if isinstance(winrate, float) else "N/A"
                output.append(f"{i}. {hero_name} - {games:.0f} games, {winrate_str} winrate")
    
    return '\n'.join(output)


def get_player_name(player_id):
    """
    Get player name from OpenDota API.
    
    Args:
        player_id (str): Player's Steam ID
        
    Returns:
        str: Player name or None if not found
    """
    try:
        url = f"https://api.opendota.com/api/players/{player_id}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Try to get name from different fields
            if 'profile' in data:
                profile = data['profile']
                # Try different name fields in order of preference
                if 'personaname' in profile and profile['personaname']:
                    return profile['personaname']
                elif 'name' in profile and profile['name']:
                    return profile['name']
                else:
                    return "Unknown Player"
            else:
                return "Unknown Player"
        else:
            print(f"Failed to get player name: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting player name: {e}")
        return None


def get_player_stats(player_input):
    """
    Get and process stats for a player from OpenDota and Stratz.
    
    Args:
        player_input (str): Player ID or URL
        
    Returns:
        pd.Series: Combined player stats
    """
    try:
        # Extract player ID
        player_id = extract_player_id(player_input)
        print(f"Getting stats for player ID: {player_id}")
        
        # Get player name
        player_name = get_player_name(player_id)
        if not player_name:
            player_name = "Unknown Player"
        
        print(f"Player: {player_name}")
            
        # Create base player info
        player_info = pd.Series({
            'player_id': player_id,
            'player_name': player_name
        })
        
        # Get OpenDota hero stats
        print("Fetching hero stats from OpenDota...")
        try:
            hero_stats = hero_information(player_id)
            print("Successfully fetched OpenDota data.")
        except Exception as e:
            print(f"Error fetching OpenDota data: {e}")
            hero_stats = pd.Series()
        
        # Get Stratz stats if available
        stratz_stats = pd.Series()
        if STRATZ_AVAILABLE:
            print("Fetching player data from Stratz...")
            try:
                # Use all RD2L league IDs for checking player history
                stratz_stats = get_stratz_features(player_id, RD2L_LEAGUE_IDS)
                print("Successfully fetched Stratz data.")
            except Exception as e:
                print(f"Error fetching Stratz data: {e}")
        else:
            print("Stratz module not available. Skipping Stratz data.")
        
        # Combine all stats
        all_stats = combine_features(player_info, hero_stats)
        all_stats = combine_features(all_stats, stratz_stats)
        
        return all_stats
        
    except Exception as e:
        print(f"Error getting player stats: {e}")
        return pd.Series()


if __name__ == "__main__":
    # Load environment variables for Stratz API
    load_dotenv()
    
    # Load hero mapping at startup
    load_hero_mapping()
    
    print("=" * 60)
    print("Player Stats - View combined stats from OpenDota and Stratz")
    print(f"Checking RD2L history across {len(RD2L_LEAGUE_IDS)} league IDs")
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