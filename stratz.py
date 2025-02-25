import requests
import pandas as pd
import time
import sys
import os
from os import path
import io
from dotenv import load_dotenv
import json

def stratz_request(players, leagues=None):
    """
    Make a GraphQL request to the Stratz API to get player data.
    
    Args:
        players (list): List of player IDs (Steam account IDs)
        leagues (list, optional): List of league IDs to filter matches
        
    Returns:
        dict: JSON response from the Stratz API
    """
    url = "https://api.stratz.com/graphql"
    api_key = os.getenv('STRATZ_API_KEY')
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Debug leagues parameter
    if leagues:
        print(f"Querying for matches across {len(leagues)} league IDs")
        print(f"League IDs: {leagues}")
    
    # Build query for multiple players with optional league filter
    player_queries = []
    
    for idx, player_id in enumerate(players):
        player_alias = f"p{idx}"
        query_parts = [
            f"{player_alias}: player(steamAccountId: {player_id}) {{",
            "  steamAccount { id name }",
            "  matchCount",
            "  winCount",
            "  behaviorScore",
            "  performance {",
            "    imp rank kills killsAverage deaths deathsAverage assists assistsAverage",
            "    cs csAverage gpm gpmAverage xpm xpmAverage",
            "  }",
            "  heroesPerformance {",
            "    heroId kDA avgKills avgDeaths avgAssists imp best lastPlayedDateTime",
            "  }"
        ]
        
        # Add league matches if leagues are specified
        if leagues:
            # Use separate take parameters to ensure we get all matches
            query_parts.append(f"  matches(request: {{leagueIds: {str(leagues)}, take: 100}}) {{")
            query_parts.append("    id didRadiantWin startDateTime")
            query_parts.append("  }")
        
        query_parts.append("}")
        player_queries.append("\n".join(query_parts))
    
    # Combine all player queries
    query = "{\n" + "\n".join(player_queries) + "\n}"
    
    response = requests.post(url, json={"query": query}, headers=headers)
    
    if response.status_code != 200:
        print(f"Error: Status code {response.status_code}")
        print(f"Response text: {response.text[:500]}...")
        return {"error": f"API request failed with status {response.status_code}"}
    
    try:
        return response.json()
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return {"error": str(e)}


def process_player_data(stratz_data):
    """
    Process the Stratz API response into features for machine learning.
    
    Args:
        stratz_data (dict): Response from stratz_request()
        
    Returns:
        pd.DataFrame: Processed player data with features
    """
    if "error" in stratz_data:
        print(f"Error in input data: {stratz_data['error']}")
        return pd.DataFrame()
    
    if "data" not in stratz_data:
        print("No data in response")
        return pd.DataFrame()
    
    players_data = []
    
    for player_key, player_data in stratz_data["data"].items():
        player_features = {
            'player_id': player_data["steamAccount"]["id"],
            'player_name': player_data["steamAccount"]["name"],
            'match_count': player_data.get("matchCount", 0),
            'win_count': player_data.get("winCount", 0),
            'win_rate': player_data.get("winCount", 0) / player_data.get("matchCount", 1) if player_data.get("matchCount", 0) > 0 else 0,
            'behavior_score': player_data.get("behaviorScore", 0),
            'has_rd2l_experience': 0  # Default to no
        }
        
        # Check if player has RD2L matches
        if "matches" in player_data and player_data["matches"]:
            player_features['has_rd2l_experience'] = 1
            player_features['rd2l_match_count'] = len(player_data["matches"])
            
            # Process match dates to find first and most recent RD2L match
            if player_data["matches"] and len(player_data["matches"]) > 0:
                match_dates = []
                for match in player_data["matches"]:
                    if "startDateTime" in match:
                        try:
                            # Convert Unix timestamp to datetime
                            match_dates.append(match["startDateTime"])
                        except:
                            pass
                
                if match_dates:
                    player_features['first_rd2l_match'] = min(match_dates)
                    player_features['last_rd2l_match'] = max(match_dates)
        
        # Add performance metrics
        if "performance" in player_data and player_data["performance"]:
            perf = player_data["performance"]
            player_features.update({
                'imp': perf.get("imp", 0),
                'rank': perf.get("rank", 0),
                'avg_kills': perf.get("killsAverage", 0),
                'avg_deaths': perf.get("deathsAverage", 0),
                'avg_assists': perf.get("assistsAverage", 0),
                'avg_cs': perf.get("csAverage", 0),
                'avg_gpm': perf.get("gpmAverage", 0),
                'avg_xpm': perf.get("xpmAverage", 0)
            })
        
        # Add hero performance metrics
        if "heroesPerformance" in player_data and player_data["heroesPerformance"]:
            hero_perf = player_data["heroesPerformance"]
            
            # Count heroes played and get average metrics across heroes
            player_features['heroes_played'] = len(hero_perf)
            
            if hero_perf:
                avg_hero_kda = sum(h.get("kDA", 0) for h in hero_perf) / len(hero_perf)
                player_features['avg_hero_kda'] = avg_hero_kda
                
                # Get best heroes by KDA
                sorted_heroes = sorted(hero_perf, key=lambda h: h.get("kDA", 0), reverse=True)
                top_heroes = sorted_heroes[:min(5, len(sorted_heroes))]
                player_features['top_heroes'] = [h.get("heroId", 0) for h in top_heroes]
        
        players_data.append(player_features)
    
    return pd.DataFrame(players_data)

def extract_players_from_csv(csv_file):
    """
    Extract player IDs from an RD2L draft sheet CSV.
    
    Args:
        csv_file (str): Path to the CSV file
        
    Returns:
        list: List of player IDs
    """
    try:
        df = pd.read_csv(csv_file)
        
        # Check if this is a player file or captains file
        if 'Dotabuff Link:' in df.columns:
            # Players file
            dotabuff_col = 'Dotabuff Link:'
        elif 'Dotabuff:' in df.columns:
            # Captains file
            dotabuff_col = 'Dotabuff:'
        else:
            print(f"Could not find Dotabuff column in {csv_file}")
            return []
        
        # Extract player IDs from Dotabuff links
        player_ids = []
        for link in df[dotabuff_col]:
            if isinstance(link, str) and 'dotabuff.com/players/' in link:
                try:
                    # Extract player ID from the link
                    player_id = int(link.split('players/')[1].split('/')[0].split(',')[0])
                    player_ids.append(player_id)
                except:
                    pass
        
        return player_ids
    except Exception as e:
        print(f"Error reading CSV file {csv_file}: {e}")
        return []


def batch_process(player_ids, leagues=None, batch_size=10):
    """
    Process players in batches to avoid API rate limits.
    
    Args:
        player_ids (list): List of player IDs
        leagues (list, optional): List of league IDs
        batch_size (int): Number of players to process in each batch
        
    Returns:
        pd.DataFrame: Processed player data
    """
    all_data = []
    
    # Process in batches
    for i in range(0, len(player_ids), batch_size):
        batch = player_ids[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1} of {(len(player_ids) + batch_size - 1) // batch_size} ({len(batch)} players)")
        
        try:
            # Get data from Stratz API
            api_response = stratz_request(batch, leagues)
            
            # Process the data
            df_batch = process_player_data(api_response)
            
            if not df_batch.empty:
                all_data.append(df_batch)
                
            # Sleep to avoid rate limits
            time.sleep(1)
                
        except Exception as e:
            print(f"Error processing batch: {e}")
    
    # Combine all batches
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()


def enrich_player_data(input_csv, output_csv=None, rd2l_leagues=[15578], batch_size=10):
    """
    Enrich player data from a CSV file with Stratz data and save to a new CSV.
    
    Args:
        input_csv (str): Path to the input CSV file with player dotabuff links
        output_csv (str, optional): Path to save the output CSV. If None, will use input_csv + "_enriched.csv"
        rd2l_leagues (list): List of RD2L league IDs to check for player participation
        batch_size (int): Number of players to process in each batch
        
    Returns:
        pd.DataFrame: Enriched player data
    """
    # Set default output file if not provided
    if output_csv is None:
        output_csv = os.path.splitext(input_csv)[0] + "_enriched.csv"
    
    # Load the original CSV
    original_df = pd.read_csv(input_csv)
    
    # Extract player IDs
    player_ids = extract_players_from_csv(input_csv)
    print(f"Extracted {len(player_ids)} player IDs from {input_csv}")
    
    if not player_ids:
        print("No player IDs found in the CSV file")
        return pd.DataFrame()
    
    # Get Stratz data for players
    stratz_df = batch_process(player_ids, rd2l_leagues, batch_size)
    
    if stratz_df.empty:
        print("Failed to get Stratz data for players")
        return pd.DataFrame()
    
    # Now we need to merge the original DataFrame with the Stratz data
    # First, find the Dotabuff column
    dotabuff_col = None
    for col in original_df.columns:
        if 'dotabuff' in col.lower():
            dotabuff_col = col
            break
    
    if not dotabuff_col:
        print("Couldn't find a Dotabuff column in the original CSV")
        return stratz_df
    
    # Create a column with the player ID from the Dotabuff link
    original_df['player_id'] = None
    for idx, link in enumerate(original_df[dotabuff_col]):
        if isinstance(link, str) and 'dotabuff.com/players/' in link:
            try:
                player_id = int(link.split('players/')[1].split('/')[0].split(',')[0])
                original_df.at[idx, 'player_id'] = player_id
            except:
                pass
    
    # Now merge the DataFrames
    original_df['player_id'] = original_df['player_id'].astype('float')
    merged_df = pd.merge(original_df, stratz_df, on='player_id', how='left')
    
    # Save to CSV
    merged_df.to_csv(output_csv, index=False)
    print(f"Enriched data saved to {output_csv}")
    
    return merged_df


if __name__ == "__main__":
    load_dotenv()
    
    # RD2L league IDs
    rd2l_leagues = [15578]  
    
    # Demo on sample players
    players = [27676663, 80266369]
    
    # Test with sample players
    print("\n--- Test with sample players ---")
    results = stratz_request(players, rd2l_leagues)
    player_df = process_player_data(results)
    print(player_df[['player_name', 'match_count', 'win_rate', 'has_rd2l_experience']])
    
    # Test CSV extraction and processing
    input_file = 'input/S33 Draft Sheet - Draft Sheet.csv'
    
    print("\n--- Test CSV Processing ---")
    # Process just 5 players for testing
    extracted_ids = extract_players_from_csv(input_file)[:5]
    if extracted_ids:
        sample_df = batch_process(extracted_ids, rd2l_leagues, batch_size=2)
        print(sample_df[['player_name', 'match_count', 'win_rate', 'has_rd2l_experience']])
    
    # Uncomment to process a full file
    # print("\n--- Full CSV Enrichment ---")
    # enriched_data = enrich_player_data(input_file, rd2l_leagues=rd2l_leagues)
    # print(f"Processed {len(enriched_data)} players")
