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

im = Image.open('icon.png')
rsize= im.resize((np.array(im.size)/10).astype(int))
rsizeArr = np.asarray(rsize)
def NonLinCdict(steps, hexcol_array):
    cdict = {'red': (), 'green': (), 'blue': ()}
    for s, hexcol in zip(steps, hexcol_array):
        rgb =matplotlib.colors.hex2color(hexcol)
        cdict['red'] = cdict['red'] + ((s, rgb[0], rgb[0]),)
        cdict['green'] = cdict['green'] + ((s, rgb[1], rgb[1]),)
        cdict['blue'] = cdict['blue'] + ((s, rgb[2], rgb[2]),)
    return cdict

cpallete = color_palettes['sbb-sequential-multihue']
colors = NonLinCdict(cpallete['intervals'], cpallete['colors']) 
cmap = matplotlib.colors.LinearSegmentedColormap('sbbtracker-sequential-cmap', colors)

for _m in mmftp:

    m = l.GLOBAL_DATA.all_data[l.GLOBAL_DATA.latest_patch][_m]


    if m['placement'] not in placements:
        continue

    pid = m['player-id']
    for p in m['players']:
        if p['player-id'] != pid:
            continue

        healths = []
        damages = []
        damage_rate = []
        damage_3 = []
        damage_4 = []
        damage_5 = []
        last_hp = None
        for _turn, hp in sorted(p['healths'].items(), key=lambda x: int(x[0])):
            if _turn == 1 and health <= 0:
                break
            if last_hp is not None and last_hp - hp > 27:
                break
            if last_hp is not None and last_hp <= 0:
                break
            healths.append(float(hp))
            last_hp = hp

        health_ls.append(healths)
        if len(healths) > 1:
            damages = [healths[idx-1] - healths[idx] for idx in range(1, len(healths))]
            damage_ls.append(damages)
        if len(damages) > 1:
            damage_rate = [damages[idx-1] - damages[idx] for idx in range(1, len(damages))]
            damage_2_ls.append(damage_rate)
        if len(damage_rate) > 1:
            damage_3 = [damage_rate[idx-1] - damage_rate[idx] for idx in range(1, len(damage_rate))]
            damage_3_ls.append(damage_3)
        if len(damage_3) > 1:
            damage_4 = [damage_3[idx-1] - damage_3[idx] for idx in range(1, len(damage_3))]
            damage_4_ls.append(damage_4)
        if len(damage_4) > 1:
            damage_5 = [damage_4[idx-1] - damage_4[idx] for idx in range(1, len(damage_4))]
            damage_5_ls.append(damage_5)

i = 0

for mode in [1,2,3]: 
    minval = None
    ymin = None
    yfilter = None
    if mode == 1:
        ls_to_inspect = health_ls
        ylabel = 'Health'
        ymin = 0
    if mode == 2:
        ls_to_inspect = damage_ls
        ylabel = 'Damage Received'
        ymin = 0
        yfilter = 2
    if mode == 3:
        ls_to_inspect = damage_2_ls
        ylabel = 'Delta Damage Received'
    if mode == 4:
        ls_to_inspect = damage_3_ls
        ylabel = '2nd Order Delta of Damage'
    if mode == 5:
        ls_to_inspect = damage_4_ls
        ylabel = 'Snap of Damage'
    
    maxlen = max([len(i) for i in ls_to_inspect])
    maxval = int(max([max(i) for i in ls_to_inspect]))
    minval = minval if minval is not None else int(min([min(i) for i in ls_to_inspect]))
    ymin = ymin if ymin is not None else minval
    yfilter = yfilter if yfilter is not None else ymin
    for ls in ls_to_inspect:
        ls.extend(['abc']*(maxlen-len(ls)))
        for _ in range(mode):
            ls.insert(0, 'abc')
                
    ls_by_turn = list(zip(*ls_to_inspect))
    counter_by_turn = [Counter([int(i) for i in ls if i != 'abc' and i>yfilter ]) for ls in ls_by_turn]
    counter_by_turn = counter_by_turn[:20]
    
    heatmap = list()
    heatmap_not_normalized = list()
    for _ in range(minval, maxval+1):
        ls = list()
        ls_not_normalized = list()
        for _ in range(0, 20):
            ls.append(0)
            ls_not_normalized.append(0)
        heatmap.append(ls)
        heatmap_not_normalized.append(ls_not_normalized)
    
    for e, c in enumerate(counter_by_turn):
        turn = e+1
        for key in c:
            heatmap[key-ymin][e] = c[key] / sum(c.values())
            heatmap_not_normalized[key-ymin][e] = c[key]
    
    npdata = np.array(heatmap)
    npdata_not_normalized = np.array(heatmap_not_normalized)
   
    placements = [str(i) for i in placements]

    fig = plt.figure(i)
    i += 1
    sns.heatmap(npdata, norm=LogNorm(), cmap=cmap)
    figwidth = fig.get_figwidth()
    figheight = fig.get_figheight()
    plt.ylim(0, maxval+1-ymin)
    plt.xlim(1)
    numticks = int((maxval-ymin+1)/25)
    ticks = list(range(ymin, maxval+1, numticks))
    locations = list(range(0, maxval-ymin+1, numticks))
    plt.yticks(locations, ticks, rotation=0)
    plt.ylabel(ylabel)
    plt.xlabel('Turn Number')
    plt.title(f'{ylabel} vs Turn, Normalized by Turn\nPlacements: {", ".join(placements)}')
    fig.figimage(rsizeArr, figwidth, figheight, zorder=100)
    plt.savefig(f'heatmap_normalized_by_turn{mode}_placements-{"-".join(placements)}.png')
    
    fig = plt.figure(i)
    i += 1
    sns.heatmap(npdata_not_normalized, norm=LogNorm(), cmap=cmap)
    plt.ylim(0, maxval+1-ymin)
    plt.xlim(1)
    plt.yticks(locations, ticks, rotation=0)

    plt.xlabel('Turn Number')
    plt.ylabel(ylabel)
    fig.figimage(rsizeArr, figwidth, figheight, zorder=100)
    plt.title(f'{ylabel} vs Turn Number, raw\nPlacements: {", ".join(placements)}')
    plt.savefig(f'heatmap_raw{mode}_placements-{"-".join(placements)}.png')
