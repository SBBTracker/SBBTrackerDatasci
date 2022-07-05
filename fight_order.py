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

from collections import defaultdict
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

results_dt = defaultdict(lambda : 0)
pidlendt = defaultdict(lambda : 0)
for _m in mmftp:

    m = l.GLOBAL_DATA.all_data[l.GLOBAL_DATA.latest_patch][_m]


    pid = m['player-id']

    no = False
    for p in m['players']:
        if len(p['healths']) < 8 or any([v<=0 for k, v in p['healths'].items() if int(k) <= 9]):
            no = True
            break

    if no:
        continue

    pids = set()
    found = False
    lastround = None
    for c in sorted(m['combat-info'], key=lambda x : x['round']):
        if c['round'] == lastround:
            continue

        lastround = c['round']


        if int(c['round']) > 7:
            break

        for _pid in c:
            if _pid in ['round', 'sim-results']:
                continue
            if _pid != pid:
                if _pid in pids:
                    results_dt[c['round']] += 1
                    found = True

                    if c['round']== 3:
                        print(m['match-id'])
                    break

                pids.add(_pid)
        if found:
            break

    pidlendt[len(pids)] += 1

print(results_dt)
print(pidlendt)
