from copy import deepcopy
from collections import defaultdict
import json
import matplotlib.pyplot as plt
import copy 

id2name = dict()
with open("CardFile.txt", 'r') as ifs:
    for e, line in enumerate(ifs):
        if e == 0:
            continue
        id2name[str(e-1)] = line.split('|')[3]

name2id = {v:k for k,v in id2name.items()}
id_data = json.load(open('id_data.json', 'r'))

ids = [201]

class Turn2Placement:
    def __init__(self):
        self.total_placement = 0
        self.total_n = 0

class Turn2Winchance:
    def __init__(self):
        self.total_wins = 0
        self.total_n = 0

turn2placement = defaultdict(Turn2Placement)
for _id, _data in deepcopy(id_data).items():
    for _round, _info in _data.items():
        turn2placement[_round].total_placement += (_info['avg_placement'] * _info['n_placement'])
        turn2placement[_round].total_n += _info['n_placement']

turn2winchance = defaultdict(Turn2Winchance)
for _id, _data in deepcopy(id_data).items():
    for _round, _info in _data.items():
        turn2winchance[_round].total_wins += (_info['avg_brawlwin'] * _info['n_brawlwin'])
        turn2winchance[_round].total_n += _info['n_brawlwin']


_turn2winchance = {k: (v.total_wins / v.total_n) for k,v in turn2winchance.items() if v.total_n > 30}
_turn2placement = {k: (v.total_placement / v.total_n) for k,v in turn2placement.items() if v.total_n > 30}

for _id in ids:
    _id = str(_id)
    data = id_data[_id]

    turns = set(range(0,19)) 
    x = sorted(turns)

    y2 = [_turn2placement[str(t)] - data[str(t)]['avg_placement'] if str(t) in data else None for t in turns]
    y1 = [data[str(t)]['avg_brawlwin'] if str(t) in data else None for t in turns]

    fig, ax = plt.subplots()
    ax.set_title(f'{id2name[_id]}')
    ax.plot(x, y2, color='red')
    ax.set_xlabel('turn')
    plt.xticks(x,x)
    ax.set_ylabel('Absolute deviation from expected placement', color='red')

    ax2=ax.twinx()
    ax2.plot(x, y1, color='blue')
    ax2.set_ylabel('Average brawl win chance', color='blue')

    ax.hlines(y=[0], xmin=1, xmax=18, colors='red', linestyles='--', lw=1, label='Average placement')
    ax2.hlines(y=[0.5], xmin=1, xmax=18, colors='blue', linestyles='--', lw=1, label='50% winrate')


    plt.savefig(f'statpics/{id2name[_id]}.png')

