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
from sbbbattlesim.treasures import registry as treasure_registry
from sbbbattlesim.characters import registry as character_registry
from sbbbattlesim.spells import registry as spell_registry

l.load_data()
mmftp = l.GLOBAL_DATA.mythic_games[l.GLOBAL_DATA.latest_patch]

treasures_by_turn = defaultdict(Counter)

placements = [1,2]

color_palettes = {
    'sbb-sequential-multihue': {
        'colors': ['#f7fcf0', '#e0f3db', '#ccebc5', '#a8ddb5', '#7bccc4', '#4eb3d3', '#2b8cbe', '#0868ac', '#084081'],
        'intervals': [0, 0.10, 0.20, 0.32, 0.44, 0.59, 0.73, 0.88, 1.00]
    }
}

missing_units = set()
missing_spells = set()

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
    for c in sorted(m['combat-info'], key=lambda x : x['round']):
        all_treasures = set()
        if not c['combat']:
            continue

        ci = c['combat'][pid]
        r = c['round']
        if r > 20:
            continue
        treasures = ci['treasures']
        for t in treasures:
            if t != 'SBB_TREASURE_RUSTYDAGGERS': #t in all_treasures:
                continue
            else:
                all_treasures.add(t)
                sbbst = treasure_registry[t]
                if t == 'SBB_TREASURE_EYESOFARES':
                    sbbst._level = 3
                treasures_by_turn[r][sbbst._level] += 1

        for _c in ci['characters']:
            sssss = character_registry[_c['id']]
            if sssss._level == 0:
                missing_units.add(_c['id'])

        for _s in ci['spells']:
            sssss = spell_registry[_s]
            try:
                if sssss._level == 0:
                    missing_spells.add(_s)
            except AttributeError:
                missing_spells.add(_s)

print(missing_units, missing_spells)

ylabel = 'lol'

maxlen = 20
maxval = 7
minval = 0
ymin = 0

heatmap = list()
heatmap_not_normalized = list()
for _ in range(0, 8):
    ls = list()
    ls_not_normalized = list()
    for _ in range(0, 20):
        ls.append(0)
        ls_not_normalized.append(0)
    heatmap.append(ls)
    heatmap_not_normalized.append(ls_not_normalized)

for e, turn in enumerate(sorted(treasures_by_turn)):

    tbtt = treasures_by_turn[turn]
    for lvl in tbtt:
        heatmap[lvl-ymin][e] = tbtt[lvl] / sum(tbtt.values())
        heatmap_not_normalized[lvl-ymin][e] = tbtt[lvl]

npdata = np.array(heatmap)
npdata_not_normalized = np.array(heatmap_not_normalized)
   
placements = [str(i) for i in placements]

fig = plt.figure(1)
sns.heatmap(npdata, norm=LogNorm(), cmap=cmap)
figwidth = fig.get_figwidth()
figheight = fig.get_figheight()
plt.ylim(0, maxval+1-ymin)
plt.xlim(1)
numticks = int((maxval-ymin+1)/8)
ticks = list(range(ymin, maxval+1, numticks))
locations = list(range(0, maxval-ymin+1, numticks))
plt.yticks(locations, ticks, rotation=0)
plt.ylabel(ylabel)
plt.xlabel('Turn Number')
plt.title(f'{ylabel} vs Turn, Normalized by Turn\nPlacements: {", ".join(placements)}')
fig.figimage(rsizeArr, figwidth, figheight, zorder=100)
plt.savefig(f'/Users/ilyasaricanli/pngs/treasures-by-level-and-turn-normalized_{"-".join(placements)}.png')

fig = plt.figure(0)
sns.heatmap(npdata_not_normalized, norm=LogNorm(), cmap=cmap)
plt.ylim(0, maxval+1-ymin)
plt.xlim(1)
plt.yticks(locations, ticks, rotation=0)

plt.xlabel('Turn Number')
plt.ylabel(ylabel)
fig.figimage(rsizeArr, figwidth, figheight, zorder=100)
plt.title(f'{ylabel} vs Turn Number, raw\nPlacements: {", ".join(placements)}')
plt.savefig(f'/Users/ilyasaricanli/pngs/treasures-by-level-and-turn-raw_{"-".join(placements)}.png')
