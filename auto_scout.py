### input

# team flexibility [0.0 - 1.0]
# how comfortable is a team with switching roles, lanes, or playing heroes offrole
flex = 0.10

# accounts for each player
team = {1: [120430219],
        2: [127714243],
        3: [170319481],
        4: [159179884],
        5: [64711066]}

# match history search parameters
params = {'lobby_type': 7, 'date': 365} # ranked, last year

# see https://docs.opendota.com/#tag/players%2Fpaths%2F~1players~1%7Baccount_id%7D~1heroes%2Fget
# omit lobby_type to include all games
# add 'significant': 0 to include turbo games

# adjust points for pro meta (pick/ban)
meta = True





### code

import requests, json, time
import pandas as pd
import numpy as np

# get player hero history
def get_player_heroes(account_id, **parameters):
    params = ''
    if parameters:
        params = '?' + '&'.join('{}={}'.format(k, v) for k, v in parameters.items())
    url = 'https://api.opendota.com/api/players/{}/heroes{}'
    data = requests.get(url.format(account_id, params)).json()
    return data

# get player medal from profile
def get_player_medal(account_id):
    url = 'https://api.opendota.com/api/players/{}'
    data = requests.get(url.format(account_id, params)).json()
    return data['rank_tier'] // 10, data['profile']['personaname']

# default flexibility
weights = {1: [0.85, 0.05, 0.10, 0.00, 0.00],
           2: [0.20, 0.60, 0.20, 0.00, 0.00],
           3: [0.10, 0.10, 0.70, 0.10, 0.00],
           4: [0.00, 0.10, 0.00, 0.50, 0.40],
           5: [0.00, 0.00, 0.00, 0.40, 0.60]}

weightsf = {k: {i + 1: 0.2 * flex + w * (1 - flex) for i, w in enumerate(v)}
            for k, v in weights.items()}

# player names
names = {i: 'pos_{}'.format(i) for i in team}

# player medals
medal = {}
for k, accs in team.items():
    m = []
    for a in accs:
        rank_tier, name = get_player_medal(a)
        m += [rank_tier]
        names[k] = name
        # delay for opendota APIs
        time.sleep(2)
    medal[k] = max(m)

# hero roles stats from stratz
stats = pd.read_csv('hero_stats2.csv', sep = ';', index_col = 0)

# also get older data
weight = 0.25
params2 = params.copy()
params2['date'] *= 3
wcols = ['games', 'win', 'with_games', 'with_win', 'against_games', 'against_win']

## main
outputs = []
for role, account_ids in team.items():
    if account_ids:
        d = []
        for a in account_ids:
            df = pd.DataFrame(get_player_heroes(a, **params))
            # delay for opendota APIs
            time.sleep(2.1)

            # also get older data
            df2 = pd.DataFrame(get_player_heroes(a, **params2))
            time.sleep(2.2)

            # combine
            df[wcols] = df[wcols] + weight * df2[wcols]
            d += [df]

        # combine accounts
        d = [pd.DataFrame(a) for a in d]
        g1 = pd.concat(d).groupby('hero_id')['last_played'].apply(max)
        g2 = pd.concat(d).groupby('hero_id')[d[0].columns[2:]].apply(sum)
        df = pd.merge(g1, g2, on = 'hero_id').sort_values('games', ascending = False).reset_index()

        # add stats columns
        df['hero_id'] = df['hero_id'].astype('int64')
        m = pd.merge(df, stats, how = 'left', left_on = ['hero_id'], right_on = ['id'])

        # value: give points for heroes played on this role (considering flexibility)
        for k in range(1, 6):
            m['pts_{}'.format(k)] = weightsf[role][k] * m['pos{}_pick'.format(k)] * m['pos{}_win'.format(k)]
        m['value'] = m[['pts_{}'.format(k) for k in range(1, 6)]].sum(axis = 1)

        # adjust value for winrate on the player's medal and meta
        m['value'] = 2 * m['value'] * m['{}_win'.format(medal[role])] / m['{}_pick'.format(medal[role])]
        if meta:
            m['value'] = m['value'] * (m['pro_pick'] + m['pro_ban'])
        else:
            m['value'] = m['value'] * 1000

        # points:
        # adjust with number of player games
        m['pts'] = 10 + m['value'] * (5 + m['games'])
        # percentage of games on each hero
        m['gr'] = 100 * m['games'] / m['games'].sum()
        m['pts'] *= m['gr'] / m['gr'].mean()
        # winrate
        m['wr'] = m['win'] / m['games']
        m['pts'] *= 1 + 0.6 * np.tanh((m['wr'] - 0.5) * 10)
        m.sort_values('pts', ascending = False, inplace = True)
        #print(m[['localized_name', 'value', 'games', 'gr', 'wr', 'pts']])

        # drop less important heroes
        m = m.reset_index().fillna(0)
        top = m['pts'].cumsum() < m['pts'].sum() * 0.95 # keep top 95%
        m = m[top | (m.index < 20)] # keep at least 20 heroes
        m['points'] = (1000 * m['pts'] / sum(m['pts']))

        # formating
        m['last_played_days'] = ((time.time() - m['last_played']) / (24 * 3600)).astype(int)
        m['value'] = m['value'].astype(int)
        m['points'] = m['points'].fillna(0).astype(int)

        # player scout sheets
        output = m[['localized_name', 'games', 'win', 'last_played_days', 'value', 'points']].copy()
        output.rename(columns = {'localized_name': 'hero'}, inplace = True)
        #output.to_csv('pos{}.csv'.format(role), sep = ';')
        outputs += [output]

# overall scouting report
report = pd.DataFrame()
for i, o in enumerate(outputs):
    report[names[i + 1]] = o['hero']
    report['{}_points'.format(i + 1)] = o['points']
report.to_csv('scouting.csv', sep = ';')
