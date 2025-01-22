# RD2L Prediction Project

The goal of this project is to utilize data science techniques on information gathered on players in the league to predict different aspects within the league. Initially this began with the goal of optimizing team composition but for the time being it has been scaled back for use as a predictive cost model.

## What is RD2L?

RD2L, initially standing for "Reddit Dota 2 League" (now R\* Dota 2 League as the Reddit association has dropped) is a self hosted amateur level competitive league. Dota for the unfamiliar is a Moba (Multiplayer Online Battle Arena) game for the computer. Players are grouped into teams of 5 where they then draft heroes to play in the individual match and then compete to destroy the other team's base.

Within the RD2L league specifically, entrants are grouped into two categories, players and captains. Due to the amateur nature of the league and the goal to appeal to as many players as possible, there is a wide skill range of players who enter to compete. This is where things tend to get very interesting. Captains are given a currency that is based on their MMR or Matchmaking Rating within Dota. This number has no ceiling but typically caps out around 7000 (for non-professional players). The captains utilize this currency to bid on players in an event that is called the draft. Players provide their MMR, comfort on playing each of the 5 roles within Dota (Carry, Mid, Offlane, Soft Support, and Hard Support) and most importantly, a link to their dotabuff account. Dotabuff is one of the large services provided to the community that acts as a game database, carrying loads of statistics on individual players. All of this is tied to their steam_id, an account specific number attached to their steam account (the service utilized to play Dota 2). These outside services are the primary way that we will be gathering information.

## Outside Services and Data Collection

Currently there are 4 ways to gather information that we would be able to use when training a model.

### Spreadsheet

The information provided by the google sheets spreadsheet that the organization runs is unfortunately bare minimum at best. Ultimately we will utilize previous season spreadsheets as the baseline information giving us the following: MMR, Player_id, Role comfort and cost. Player_id is originally given as a dotabuff url but with some quick python string parsing we can extract the information. "https://www.dotabuff.com/players/{player_id}" can be modified with a simple function mapped onto a Pandas DataFrame:
