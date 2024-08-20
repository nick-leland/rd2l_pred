# Potential Query

Here is a potential query that we can use to determine if a player has played previously in the league.  
Arguably, this could be performed in our initial data collection but I feel like that is a messy way to do it.

This can be shortened, right now I am using all of the queries within the selected areas for a lot of these, which can probably be shortened.  
GraphQL website: https://api.stratz.com/graphiql/ 

Look into this article for adding the Stratz API key to a hugging face environment: https://discuss.huggingface.co/t/how-would-i-hide-my-files/13035 

{
  players(steamAccountIds: [27676663, 162015739]) {
    steamAccount {id}
    matchCount
    winCount
    behaviorScore
    activity {
      activity
    }
    performance {
      imp
      rank
      kills
      killsAverage
      deaths
      deathsAverage
      assists
      assistsAverage
      cs
      csAverage
      gpm
      gpmAverage
      xpm
      xpmAverage
    }
    heroesPerformance {
      kDA
      avgKills
      avgDeaths
      avgAssists
      imp
      best
      lastPlayedDateTime
    }
    ranks {
      seasonRankId
      asOfDateTime
      isCore
      rank
    }
    matches(request: {leagueIds: [15578]}) {
      didRadiantWin
      
    }
  }
}
