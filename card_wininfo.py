import json
from PIL import Image
import numpy as np
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
import statistics
import sbbtracker_datasci.utils.load_data as l
from collections import defaultdict
from matplotlib.colors import LogNorm
import matplotlib 
import matplotlib.image as image

l.load_data()
mmftp = l.GLOBAL_DATA.mythic_games[l.GLOBAL_DATA.latest_patch]

health_ls = []
damage_ls = []
damage_2_ls = []
damage_3_ls = []
damage_4_ls = []
damage_5_ls = []

placements = [1,2,3,4,5,6,7,8]

color_palettes = {
    'sbb-sequential-multihue': {
        'colors': ['#f7fcf0', '#e0f3db', '#ccebc5', '#a8ddb5', '#7bccc4', '#4eb3d3', '#2b8cbe', '#0868ac', '#084081'],
        'intervals': [0, 0.10, 0.20, 0.32, 0.44, 0.59, 0.73, 0.88, 1.00]
    }
}

weirdos = 0
id_data = defaultdict( lambda : defaultdict(dict))

for _m in mmftp:

    m = l.GLOBAL_DATA.all_data[l.GLOBAL_DATA.latest_patch][_m]

    if len(m['players']) > 8:
        continue

    pid = m['player-id']

    placement = m['placement']

    for p in m['players']:
        if p['player-id'] == pid:
            healths = {int(k):v for k,v in p['healths'].items()}
            break

    last_round = None
    for c in sorted(m['combat-info'], key=lambda x : x['round']):

        if c['round'] == last_round:
            continue
        last_round = c['round']


        ids = list()
        for category, _ids in c[pid].items():
            if _ids:
                if category in ['level', 'hand']:
                    continue
                elif category == 'hero':
                    _ids = [_ids]
                elif isinstance(_ids[0], dict):
                    _ids = [_itr['id'] for _itr in _ids]

                ids.extend(_ids)
        
        ids = set(ids)

        this_round = c['round']
        next_round = this_round + 1
        try:
            won_round = (next_round not in healths and placement == 1) or (next_round in healths and (healths[this_round] - healths[next_round] < 3) )
        except KeyError:
            weirdos += 1
            continue

        for _id in ids:
            this_data = id_data[_id][this_round]
            if not len(this_data.keys()):
                this_data = {"avg_placement": placement, "n_placement": 1, "avg_brawlwin": int(won_round), "n_brawlwin": 1}
                id_data[_id][this_round] = this_data
            else:
                this_data['avg_placement'] = (this_data['avg_placement']*this_data['n_placement'] + placement)
                this_data['n_placement'] += 1
                this_data['avg_placement'] = this_data['avg_placement']/this_data['n_placement']

                this_data['avg_brawlwin'] = this_data['avg_brawlwin']*this_data['n_brawlwin'] + int(won_round)
                this_data['n_brawlwin'] += 1
                this_data['avg_brawlwin'] = this_data['avg_brawlwin']/this_data['n_brawlwin']


with open('id_data.json', 'w') as ofs:
    ofs.write(json.dumps(id_data))

print(weirdos)
