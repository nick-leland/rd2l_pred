# Potential Query
Here is a potential query that we can use to determine if a player has played previously in the league.  

Arguably, this could be performed in our initial data collection but I feel like that is a messy way to do it.

{
  players(steamAccountIds: [27676663, 162015739]) {
    steamAccount {id}
    matchCount
    behaviorScore
    matches(request: {leagueIds: [15578]}) {
      didRadiantWin
      
    }
  }
}
