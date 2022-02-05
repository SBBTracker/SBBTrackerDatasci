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

games = 0
copygames = 0
noncopygames = 0
placements = 0
copyplacements = 0
noncopyplacements = 0
for _m in mmftp:

    m = l.GLOBAL_DATA.all_data[l.GLOBAL_DATA.latest_patch][_m]


    pid = m['player-id']

    is_th = False

    if len(m['combat-info']) < 14:
        continue

    for c in sorted(m['combat-info'], key=lambda x : x['round']):
        any_copycats = False

        if not c['combat']:
            continue

        if c['combat'][pid]['hero'] != 'SBB_HERO_MILITARYLEADER':
            break
        else:
            is_th = True


        if not is_th:
            break

        for char in c['combat'][pid]['characters']:
            if char['id'] == 'SBB_CHARACTER_COPYCAT':
                any_copycats = True
                break

        if any_copycats:
            break

    if is_th:
        placement = m['placement']
        games += 1
        placements += placement
        if any_copycats:
            copyplacements += placement
            copygames += 1
        else:
            noncopyplacements += placement
            noncopygames += 1
    
print('category placements totalgames avg')
print('all', placements, games, round(placements/games,2))
print('copycat', copyplacements, copygames, round(copyplacements/copygames,2))
print('no copycat', noncopyplacements, noncopygames, round(noncopyplacements/noncopygames,2))
