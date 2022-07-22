# dota2-scouting

Automating scouting for the opponent's heroes

Goal:
Get info for draft priority (picks/bans) for the opponent team. The result is a list of heroes with highest 'value'.

.

Features:

- Will accept several account ids.
Ex: if a player has alts, smurfs.
- Will adjust hero values according to player's performance on the hero.
Ex: more points for more games, more points for higher winrate.
- Will adjust hero values according to hero performance in the player's bracket.
Ex: more points for hero if the player is Divine, given 45% hero winrate on Archon vs 55% on Divine.

- Can adjust hero value according to pro meta.
Ex: more points for more pro pick/bans, to prioritize what's currently in meta.
- Can extend search history and can include non ranked games.

- Will accomodate lane or role flexibility.
Ex: some points for anti-mage mid, even if it is played there only 5% of the time (with 50% winrate).
Ex: a spammer has no problem picking it, so with enough matches the hero will have more value.
- Can adjust team flexibility from mostly strict to completely free.
Ex: with flexibility = 0.0, offrole picks are given little importance.
Ex: with flexibility = 1.0, any player can play any role.

.

Weakness:
- Having to manually set the flexibility factor
- hero_stats2.csv is meta dependent, needs to be generated again after patch


Note:
This is good at scouting 5 players on certain roles. This is not good at scouting a team's strategy. You have to do this yourself.
