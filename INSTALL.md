# RD2L Tools Installation & Usage Guide

This document provides detailed instructions for installing and using the RD2L tools included in this repository.

## Table of Contents
- [Installation](#installation)
  - [Requirements](#requirements)
  - [Setup](#setup)
  - [Stratz API Key](#stratz-api-key)
- [Usage](#usage)
  - [Player Stats Tool](#player-stats-tool)
  - [Team Scouting Tool](#team-scouting-tool)
- [Extending the Tools](#extending-the-tools)
- [Troubleshooting](#troubleshooting)

## Installation

### Requirements

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

### Setup

1. **Get the code**

   Either clone the repository:
   ```bash
   git clone https://github.com/nick-leland/rd2l_pred.git
   cd rd2l_pred
   ```

   Or download and extract the ZIP file from GitHub.

2. **Create a virtual environment (recommended)**

   ```bash
   python -m venv venv
   ```

   Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   This installs all required packages including:
   - pandas
   - numpy
   - requests
   - python-dotenv
   - tabulate

### Stratz API Key

The tools require a Stratz API key to access Dota 2 match data:

1. **Get a Stratz API key**
   - Go to [https://stratz.com/api](https://stratz.com/api)
   - Sign in with your Steam account
   - Follow the instructions to generate an API key

2. **Create a .env file**
   
   Create a file named `.env` in the root directory of the project:
   ```
   STRATZ_API_KEY=your_stratz_api_key_here
   ```

   Replace `your_stratz_api_key_here` with your actual Stratz API key.

## Usage

### Player Stats Tool

The Player Stats tool provides detailed analysis of individual Dota 2 players, including their hero preferences, winrates, and RD2L match history.

**Run the tool:**
```bash
./player.py
```
or
```bash
python player.py
```

**Features:**
- View player's overall stats, including total games and winrate
- See top heroes by games played and winrate
- Check recent hero performance (last 30 days)
- Find RD2L-specific hero stats and experience
- Works with player IDs or Dotabuff/OpenDota URLs

**Example:**
```
Enter player ID or URL (or 'q' to quit): https://www.dotabuff.com/players/162015739
```

### Team Scouting Tool

The Team Scouting tool generates comprehensive reports on RD2L teams, helping you prepare for matches by understanding team drafting patterns and player preferences.

**Run the tool:**
```bash
./scout.py
```
or
```bash
python scout.py
```

**Features:**
- Select teams from a menu of RD2L teams
- View individual player hero preferences and winrates
- See team drafting patterns and frequently picked heroes
- Get recommended ban priorities
- Export reports to JSON files for sharing

**Options:**
1. Scout a team (select from list)
2. Scout a team by ID
3. Scout a team by player IDs
4. List available teams
5. Exit

## Extending the Tools

### Adding Custom Teams

You can add custom teams to the scouting tool by editing the team cache file:

1. Run the scout tool once to generate the initial cache
2. Edit the file at `utilities/data/rd2l_teams.json`
3. Add or modify teams following the existing format:
   ```json
   {
     "team_id": {
       "id": "team_id",
       "name": "Team Name",
       "tag": "TAG",
       "players": [123456789, 987654321]
     }
   }
   ```

### Implementing Custom Analyses

For developers who want to extend the tools:

1. The `stratz.py` file contains the core API interaction code
2. `feature_engineering.py` contains data transformation functions
3. The utilities folder contains the application layer

## Troubleshooting

### Common Issues

**"Stratz module not available" Error**
- Ensure the `.env` file is in the correct location with your API key
- Check that all dependencies are installed with `pip install -r requirements.txt`

**Import Errors**
- Make sure you're running the scripts from the project root directory
- Verify your Python version is 3.8 or higher

**API Rate Limiting**
- The Stratz API has rate limits. If you encounter errors, try again after a few minutes
- For large batch operations, add delays between requests

### Getting Help

If you encounter issues that aren't covered here:
- Check the GitHub repository issues section
- Review the source code comments for detailed implementation notes