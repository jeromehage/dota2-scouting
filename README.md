# dota2-scouting

Automating scouting for the opponent's heroes

Goal:
Get info for draft priority (picks/bans) for the opponent team. The result is a list of heroes with highest 'value'.

Features:

- Accepts several account ids for alts, smurfs.
- Adjust value to player's performance on the hero (games, winrate).
- Adjust value according to hero performance in the player's bracket (from medal, automated).
- Adjust value according to pro meta (pick+ban rates).
- Can extend search history and include non-ranked games.
- Accomodate lane or role flexibility for team:
Ex: with flexibility = 0.0, offrole picks are given little importance.
Ex: with flexibility = 1.0, any player can play any role.

Weakness:
- Having to manually set the flexibility factor
- hero_stats2.csv is meta dependent, needs to be generated again after patch

Note:
This is good at scouting 5 players on certain roles. This is not good at scouting a team's strategy. You have to do this yourself.
