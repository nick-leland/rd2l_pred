#!/usr/bin/env python3
"""
RD2L Team Scouting Tool

Generates comprehensive scouting reports on teams in the RD2L leagues, 
including player hero preferences, recent activity, and team drafting patterns.
"""

import pandas as pd
import numpy as np
import requests
import os
import json
import time
import datetime
from dotenv import load_dotenv
from tabulate import tabulate  # For formatted console output

# Import features from other modules
try:
    import stratz
    from player_stats import load_hero_mapping, get_hero_name
    STRATZ_AVAILABLE = True
except ImportError:
    STRATZ_AVAILABLE = False
    print("Warning: Stratz module not available. Some features will be limited.")

# Current RD2L league ID (Season 33)
CURRENT_LEAGUE_ID = 16436

# All RD2L league IDs for full history
RD2L_LEAGUE_IDS = [16436, 16435, 16434, 15578, 15577, 15246, 14906, 14507, 14137, 13780, 13375, 13185, 12762, 11984]

# Hero mapping for names
HERO_MAPPING = {}

class TeamScout:
    """Class to handle team scouting operations"""
    
    def __init__(self):
        """Initialize the scouting tool"""
        load_dotenv()
        self.load_hero_mapping()
        
        # Verify Stratz API access
        if not STRATZ_AVAILABLE:
            print("ERROR: Stratz module is required for team scouting")
            print("Please ensure you have the Stratz module installed and API key set")
            return
        
        # Recent time threshold (30 days)
        self.recent_threshold = int(time.time()) - (30 * 24 * 60 * 60)
        
    def load_hero_mapping(self):
        """Load hero names mapping"""
        global HERO_MAPPING
        
        # Check if already loaded by player_stats
        if HERO_MAPPING:
            return
            
        try:
            # Try to load from existing mapping
            load_hero_mapping()
            HERO_MAPPING = globals().get('HERO_MAPPING', {})
        except:
            # Fetch directly if needed
            try:
                print("Fetching hero data from OpenDota API...")
                response = requests.get("https://api.opendota.com/api/heroes")
                if response.status_code == 200:
                    heroes = response.json()
                    HERO_MAPPING = {str(hero['id']): hero['localized_name'] for hero in heroes}
                    print(f"Loaded {len(HERO_MAPPING)} heroes")
                else:
                    print(f"Failed to fetch heroes: {response.status_code}")
                    HERO_MAPPING = {}
            except Exception as e:
                print(f"Error loading heroes: {e}")
                HERO_MAPPING = {}
    
    def get_hero_name(self, hero_id):
        """Get hero name from ID"""
        hero_id = str(hero_id)
        return HERO_MAPPING.get(hero_id, f"Hero {hero_id}")

    def get_league_teams(self, league_id=CURRENT_LEAGUE_ID):
        """
        Get all teams participating in the specified league
        
        Args:
            league_id (int): League ID to fetch teams for
            
        Returns:
            dict: Dictionary of teams with team details
        """
        print(f"Fetching teams for league {league_id}...")
        
        # GraphQL query for league teams
        query = f"""
        {{
          league(id: {league_id}) {{
            id
            displayName
            teams {{
              id
              name
              tag
              logo
            }}
          }}
        }}
        """
        
        # Execute query
        try:
            # Use stratz request with empty players list as we're only querying league info
            response = stratz.stratz_request([], None)
            
            # TODO: Replace this with actual league teams query
            # This is a placeholder - need to implement league query in stratz.py
            # For now, return some demo data
            
            # Mock teams data
            teams = {
                "123456": {"id": "123456", "name": "Team Juicy", "players": [162015739, 80266369, 27676663]},
                "789012": {"id": "789012", "name": "The Dumpster Fire", "players": [110119494, 97079776, 27676663]},
            }
            
            print(f"Found {len(teams)} teams")
            return teams
            
        except Exception as e:
            print(f"Error fetching league teams: {e}")
            return {}
    
    def get_team_matches(self, team_id, league_id=CURRENT_LEAGUE_ID):
        """
        Get all matches for a team in the specified league
        
        Args:
            team_id (str): Team ID to fetch matches for
            league_id (int): League ID to filter matches
            
        Returns:
            list: List of match data
        """
        print(f"Fetching matches for team {team_id} in league {league_id}...")
        
        # TODO: Implement team match lookup - for now return demo data
        
        # Mock match data
        matches = [
            {
                "id": "1234567890",
                "startDateTime": int(time.time()) - (7 * 24 * 60 * 60),  # 7 days ago
                "didRadiantWin": True,
                "isRadiant": True,
                "players": [162015739, 80266369, 27676663, 110119494, 97079776],
                "picks": [14, 10, 1, 5, 2],  # Hero IDs
                "bans": [8, 9, 11, 22, 44],   # Hero IDs
                "draft_order": [(0, 14), (0, 10), (1, 21), (1, 32), (0, 1), (0, 5), (1, 45), (1, 67), (0, 2)]
            },
            {
                "id": "9876543210",
                "startDateTime": int(time.time()) - (14 * 24 * 60 * 60),  # 14 days ago
                "didRadiantWin": False,
                "isRadiant": False, 
                "players": [162015739, 80266369, 27676663, 110119494, 97079776],
                "picks": [2, 5, 53, 64, 41],  # Hero IDs
                "bans": [8, 9, 1, 10, 43],    # Hero IDs
                "draft_order": [(1, 2), (1, 5), (0, 19), (0, 23), (1, 53), (1, 64), (0, 37), (0, 55), (1, 41)]
            }
        ]
        
        return matches
    
    def get_player_data(self, player_id):
        """
        Get comprehensive player data including heroes and performance
        
        Args:
            player_id (int): Player Steam ID
            
        Returns:
            dict: Player data including heroes and performance
        """
        print(f"Fetching data for player {player_id}...")
        
        try:
            # Get basic player data
            player_data = {"id": player_id}
            
            # Get player profile from OpenDota
            try:
                profile_url = f"https://api.opendota.com/api/players/{player_id}"
                response = requests.get(profile_url)
                if response.status_code == 200:
                    profile = response.json()
                    if "profile" in profile:
                        player_data["name"] = profile["profile"].get("personaname", "Unknown")
                    else:
                        player_data["name"] = "Unknown"
                else:
                    player_data["name"] = "Unknown"
            except:
                player_data["name"] = "Unknown"
            
            # Get recent hero performance from OpenDota
            try:
                heroes_url = f"https://api.opendota.com/api/players/{player_id}/heroes"
                response = requests.get(heroes_url)
                if response.status_code == 200:
                    heroes_raw = response.json()
                    
                    # Process heroes data
                    heroes = []
                    for hero in heroes_raw:
                        hero_id = hero.get("hero_id")
                        if hero_id:
                            heroes.append({
                                "hero_id": hero_id,
                                "hero_name": self.get_hero_name(hero_id),
                                "games": hero.get("games", 0),
                                "win": hero.get("win", 0),
                                "winrate": hero.get("win", 0) / hero.get("games", 1) if hero.get("games", 0) > 0 else 0
                            })
                    
                    # Sort by games played
                    heroes.sort(key=lambda x: x["games"], reverse=True)
                    player_data["top_heroes"] = heroes[:10]  # Top 10 heroes
                else:
                    player_data["top_heroes"] = []
            except Exception as e:
                print(f"Error getting player heroes: {e}")
                player_data["top_heroes"] = []
            
            # Get RD2L performance using Stratz API
            try:
                # Get player data from current league
                res = stratz.stratz_request([player_id], [CURRENT_LEAGUE_ID])
                
                # Process the data for league hero performance
                data = res.get("data", {})
                if data:
                    p_key = next(iter(data.keys()))
                    p_data = data[p_key]
                    
                    # Get league matches if available
                    if "matches" in p_data and p_data["matches"]:
                        # Count heroes played in league
                        league_heroes = {}
                        
                        # TODO: Extract hero ID from match data when API is complete
                        # For now, use placeholder data
                        league_heroes = {
                            1: {"hero_id": 1, "games": 3, "wins": 2},
                            2: {"hero_id": 2, "games": 2, "wins": 1},
                            14: {"hero_id": 14, "games": 4, "wins": 3}
                        }
                        
                        # Convert to list and sort
                        league_hero_list = []
                        for hero_id, stats in league_heroes.items():
                            league_hero_list.append({
                                "hero_id": hero_id,
                                "hero_name": self.get_hero_name(hero_id),
                                "games": stats["games"],
                                "wins": stats["wins"],
                                "winrate": stats["wins"] / stats["games"] if stats["games"] > 0 else 0
                            })
                        
                        # Sort by games played
                        league_hero_list.sort(key=lambda x: x["games"], reverse=True)
                        player_data["league_heroes"] = league_hero_list
                    else:
                        player_data["league_heroes"] = []
                else:
                    player_data["league_heroes"] = []
                
                # Get recent heroes (last 30 days)
                res = stratz.stratz_request([player_id], None)  # No league filter for recent games
                
                # TODO: Extract recent hero data when API is complete
                # For now, use placeholder data
                recent_heroes = [
                    {"hero_id": 1, "hero_name": self.get_hero_name(1), "games": 5, "wins": 3, "winrate": 0.6},
                    {"hero_id": 2, "hero_name": self.get_hero_name(2), "games": 7, "wins": 4, "winrate": 0.57},
                    {"hero_id": 14, "hero_name": self.get_hero_name(14), "games": 3, "wins": 1, "winrate": 0.33}
                ]
                
                player_data["recent_heroes"] = recent_heroes
                
            except Exception as e:
                print(f"Error getting RD2L data: {e}")
                player_data["league_heroes"] = []
                player_data["recent_heroes"] = []
            
            return player_data
            
        except Exception as e:
            print(f"Error fetching player data: {e}")
            return {"id": player_id, "name": "Unknown", "error": str(e)}
    
    def generate_team_report(self, team_id=None, team_name=None, players=None, league_id=CURRENT_LEAGUE_ID):
        """
        Generate a comprehensive scouting report for a team
        
        Args:
            team_id (str, optional): Team ID to scout
            team_name (str, optional): Team name (used for output)
            players (list, optional): List of player IDs if team_id not provided
            league_id (int): League ID for scouting
            
        Returns:
            dict: Complete scouting report
        """
        # Get team info if ID provided
        if team_id:
            teams = self.get_league_teams(league_id)
            if team_id not in teams:
                print(f"Team {team_id} not found in league {league_id}")
                return None
            
            team_info = teams[team_id]
            team_name = team_info.get("name", f"Team {team_id}")
            players = team_info.get("players", [])
        
        # Validate player list
        if not players:
            print("No players provided for scouting")
            return None
        
        print(f"Generating scouting report for {team_name}...")
        
        # Initialize report
        report = {
            "team_name": team_name,
            "league_id": league_id,
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "players": [],
            "team_heroes": {},
            "team_picks": [],
            "team_bans": [],
            "team_draft_patterns": []
        }
        
        # Get data for each player
        for player_id in players:
            player_data = self.get_player_data(player_id)
            report["players"].append(player_data)
        
        # Get team match data
        if team_id:
            matches = self.get_team_matches(team_id, league_id)
            
            # Process team picks and bans
            pick_counts = {}
            ban_counts = {}
            draft_orders = []
            
            for match in matches:
                # Track picks
                for hero_id in match.get("picks", []):
                    if hero_id not in pick_counts:
                        pick_counts[hero_id] = 0
                    pick_counts[hero_id] += 1
                
                # Track bans
                for hero_id in match.get("bans", []):
                    if hero_id not in ban_counts:
                        ban_counts[hero_id] = 0
                    ban_counts[hero_id] += 1
                    
                # Track draft order
                if "draft_order" in match:
                    draft_orders.append(match["draft_order"])
            
            # Convert pick counts to list and sort
            pick_list = []
            for hero_id, count in pick_counts.items():
                pick_list.append({
                    "hero_id": hero_id,
                    "hero_name": self.get_hero_name(hero_id),
                    "count": count
                })
            pick_list.sort(key=lambda x: x["count"], reverse=True)
            report["team_picks"] = pick_list
            
            # Convert ban counts to list and sort
            ban_list = []
            for hero_id, count in ban_counts.items():
                ban_list.append({
                    "hero_id": hero_id,
                    "hero_name": self.get_hero_name(hero_id),
                    "count": count
                })
            ban_list.sort(key=lambda x: x["count"], reverse=True)
            report["team_bans"] = ban_list
            
            # Analyze draft patterns
            # TODO: Implement more sophisticated draft pattern analysis
            # For now, just count heroes by draft position
            draft_positions = {}
            for order in draft_orders:
                for pos, hero_id in order:
                    if pos not in draft_positions:
                        draft_positions[pos] = {}
                    
                    if hero_id not in draft_positions[pos]:
                        draft_positions[pos][hero_id] = 0
                    
                    draft_positions[pos][hero_id] += 1
            
            # Convert draft positions to list
            draft_patterns = []
            for pos, heroes in draft_positions.items():
                hero_list = []
                for hero_id, count in heroes.items():
                    hero_list.append({
                        "hero_id": hero_id,
                        "hero_name": self.get_hero_name(hero_id),
                        "count": count
                    })
                hero_list.sort(key=lambda x: x["count"], reverse=True)
                
                draft_patterns.append({
                    "position": pos,
                    "heroes": hero_list[:3]  # Top 3 heroes for this position
                })
            
            report["team_draft_patterns"] = draft_patterns
        
        return report
    
    def print_team_report(self, report):
        """
        Print a formatted team report to the console
        
        Args:
            report (dict): The team report to print
        """
        if not report:
            print("No report data available")
            return
        
        print("\n" + "=" * 80)
        print(f"SCOUTING REPORT: {report['team_name']}")
        print(f"League ID: {report['league_id']} | Generated: {report['generated_at']}")
        print("=" * 80)
        
        # Print player summaries
        print("\nPLAYER SUMMARIES")
        print("-" * 80)
        
        for player in report["players"]:
            print(f"\n{player['name']} (ID: {player['id']})")
            
            # Print top overall heroes
            if "top_heroes" in player and player["top_heroes"]:
                print("\n  Top Heroes (All-time):")
                heroes_table = []
                for hero in player["top_heroes"][:5]:  # Top 5
                    heroes_table.append([
                        hero["hero_name"],
                        f"{hero['games']} games",
                        f"{hero['winrate']:.1%} winrate"
                    ])
                print(tabulate(heroes_table, tablefmt="plain"))
            
            # Print recent heroes
            if "recent_heroes" in player and player["recent_heroes"]:
                print("\n  Recent Heroes (30 days):")
                heroes_table = []
                for hero in player["recent_heroes"]:
                    heroes_table.append([
                        hero["hero_name"],
                        f"{hero['games']} games",
                        f"{hero['winrate']:.1%} winrate"
                    ])
                print(tabulate(heroes_table, tablefmt="plain"))
            
            # Print league heroes
            if "league_heroes" in player and player["league_heroes"]:
                print("\n  RD2L Heroes (Current Season):")
                heroes_table = []
                for hero in player["league_heroes"]:
                    heroes_table.append([
                        hero["hero_name"],
                        f"{hero['games']} games",
                        f"{hero['winrate']:.1%} winrate"
                    ])
                print(tabulate(heroes_table, tablefmt="plain"))
            
            print("-" * 40)
        
        # Print team picks
        if "team_picks" in report and report["team_picks"]:
            print("\nTEAM PICKS")
            print("-" * 80)
            picks_table = []
            for hero in report["team_picks"][:10]:  # Top 10
                picks_table.append([
                    hero["hero_name"],
                    f"{hero['count']} times"
                ])
            print(tabulate(picks_table, tablefmt="plain"))
        
        # Print team bans
        if "team_bans" in report and report["team_bans"]:
            print("\nTEAM BANS")
            print("-" * 80)
            bans_table = []
            for hero in report["team_bans"][:10]:  # Top 10
                bans_table.append([
                    hero["hero_name"],
                    f"{hero['count']} times"
                ])
            print(tabulate(bans_table, tablefmt="plain"))
        
        # Print draft patterns
        if "team_draft_patterns" in report and report["team_draft_patterns"]:
            print("\nDRAFT PATTERNS")
            print("-" * 80)
            for pattern in sorted(report["team_draft_patterns"], key=lambda x: x["position"]):
                pos = pattern["position"]
                phase = "First phase" if pos <= 1 else "Second phase" if pos <= 3 else "Third phase"
                print(f"\n  Position {pos} ({phase}):")
                for hero in pattern["heroes"]:
                    print(f"    {hero['hero_name']} - {hero['count']} times")
        
        print("\n" + "=" * 80)
        print("RECOMMENDED BAN PRIORITIES")
        print("-" * 80)
        
        # Calculate ban priorities based on pick frequency and impact
        ban_priorities = []
        
        # TODO: Implement more sophisticated ban priority algorithm
        # For now, just suggest the most picked heroes
        if "team_picks" in report and report["team_picks"]:
            for hero in report["team_picks"][:3]:  # Top 3 team picks
                ban_priorities.append(hero)
        
        # Add top heroes from players if not already in list
        for player in report["players"]:
            if "league_heroes" in player and player["league_heroes"]:
                for hero in player["league_heroes"][:2]:  # Top 2 heroes per player
                    # Check if already in ban priorities
                    if not any(p["hero_id"] == hero["hero_id"] for p in ban_priorities):
                        ban_priorities.append({
                            "hero_id": hero["hero_id"],
                            "hero_name": hero["hero_name"],
                            "reason": f"Top hero for {player['name']}"
                        })
        
        # Print ban priorities
        for i, hero in enumerate(ban_priorities[:5], 1):  # Top 5 priorities
            reason = hero.get("reason", "Frequently picked")
            print(f"{i}. {hero['hero_name']} - {reason}")
        
        print("\n" + "=" * 80)
    
    def export_report(self, report, file_path=None):
        """
        Export the report to a file
        
        Args:
            report (dict): The report to export
            file_path (str, optional): Path to save the report to
        """
        if not report:
            print("No report data available to export")
            return
        
        if not file_path:
            # Generate default filename
            team_name = report["team_name"].replace(" ", "_").lower()
            file_path = f"scout_{team_name}_{report['league_id']}.json"
        
        try:
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"Report exported to {file_path}")
        except Exception as e:
            print(f"Error exporting report: {e}")


def main():
    """Main function to run the scouting tool"""
    scout = TeamScout()
    
    print("\nRD2L Team Scouting Tool")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Scout a team by ID")
        print("2. Scout a team by player IDs")
        print("3. List available teams")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1":
            team_id = input("Enter team ID: ")
            report = scout.generate_team_report(team_id=team_id)
            if report:
                scout.print_team_report(report)
                export = input("\nExport report to file? (y/n): ")
                if export.lower() == 'y':
                    scout.export_report(report)
        
        elif choice == "2":
            team_name = input("Enter team name: ")
            player_input = input("Enter player IDs (comma-separated): ")
            player_ids = [int(p.strip()) for p in player_input.split(",") if p.strip()]
            
            if player_ids:
                report = scout.generate_team_report(team_name=team_name, players=player_ids)
                if report:
                    scout.print_team_report(report)
                    export = input("\nExport report to file? (y/n): ")
                    if export.lower() == 'y':
                        scout.export_report(report)
            else:
                print("No valid player IDs provided")
        
        elif choice == "3":
            teams = scout.get_league_teams()
            if teams:
                print("\nAvailable Teams:")
                for team_id, team in teams.items():
                    print(f"{team_id}: {team['name']}")
            else:
                print("No teams found or error fetching teams")
        
        elif choice == "4":
            print("\nExiting RD2L Team Scouting Tool. Goodbye!")
            break
        
        else:
            print("Invalid choice, please try again")


if __name__ == "__main__":
    main()