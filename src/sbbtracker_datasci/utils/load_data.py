from collections import defaultdict
import json
from dataclasses import dataclass
import gzip
import boto3
import os
import logging
import datetime
import tarfile
from sbbtracker_datasci import TEMPLATEID_SUBDIR, MATCH_DATA_DIR
from sbbbattlesim.characters import registry as character_registry
from sbbbattlesim.treasures import registry as treasure_registry
from sbbbattlesim.spells import registry as spell_registry

logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    filename: str
    token: str
    datestr: str


class GlobalData:

    def __init__(self):
        self.all_data = defaultdict(lambda : defaultdict(set))
        self.mythic_games = defaultdict(set)
        self.nonmythic_games = defaultdict(set)
        self.games_by_placement = defaultdict(lambda : defaultdict(set))
        self.games_by_starting_hero = defaultdict(lambda : defaultdict(set))

        self.count_broken_files = 0
        self.latest_patch = '67.4'


    def add_file(self, fileinfo, data):
        patch = '67.4'  # TODO add logic to separate games into patches

        # Throw out shitty data
        if not len(data['players']) == 8:
            self.count_broken_files += 1
            return

        # Get some straightforward data
        playerid = data['player-id']

        # player info is a list, find the data pertaining to the actual player
        player_info = None
        for p in data['players']:
            if p['player-id'] == playerid:
                player_info = p
        if player_info is None:
            raise ValueError(f'Did not find player id {playerid} in file {fileinfo.filename}')

        # Easier than complicated object shenanigans
        game_hash_id = hash(f'{fileinfo.token}/{os.path.split(fileinfo.filename)[-1]}/{data["time"]}')

        # split data in fun ways
        self.all_data[patch][game_hash_id] = data
        if data['possibly-mythic']:
            self.mythic_games[patch].add(game_hash_id)
        else:
            self.nonmythic_games[patch].add(game_hash_id)

        self.games_by_placement[patch][data['placement']].add(game_hash_id)
        self.games_by_starting_hero[patch][player_info['heroes'][0]].add(game_hash_id)


GLOBAL_DATA = GlobalData()


def walk_data_dir():
    """
    Go through the downloaded data and return relevant data, split into its useful components
    """

    for root_dir, _, files in os.walk(MATCH_DATA_DIR):
        for f in files:
            full_path = os.path.join(root_dir, f)

            path, filename = os.path.split(full_path)
            path, token = os.path.split(path)
            path, datestr = os.path.split(path)

            yield FileInfo(filename=full_path, token=token, datestr=datestr)
            

def load_data():
    # TODO: Add the ability to filter on patches & such

    templateids = json.load(open(os.path.join(TEMPLATEID_SUBDIR, 'template-id-v4.0.4.json') ))
    templateids["8"] = {"Name": "Pig", "Id": "SBB_CHARACTER_PIG"}

    for fi in walk_data_dir():
        data = json.load(open(fi.filename))

        for player_info in data['players']:
            playerid = player_info['player-id']
            heroes = player_info['heroes']

            new_heroes = list()
            for hero in heroes:
                hero_id = templateids[hero]['Id']
                if not hero_id.startswith('SBB_HERO'):
                    raise ValueError(f'Wrong template-ids file used with this data file, id {hero} maps to name {hero_id} which is not a hero')

                new_heroes.append(hero_id)
                player_info['heroes'] = new_heroes


        new_combat_info = list()
        for combat in data['combat-info']:
            new_combat = dict()
            for player, board in combat.items():
                if player == 'round':
                    continue

                # Update character template ids to the SBB ids
                for char in board['characters']:
                    try:
                        char_id = templateids[char['id']]['Id']
                        char['golden'] = False
                    except KeyError:
                        char['id'] = str(int(char['id']) - 1)

                        char['golden'] = True
                        try:
                            char_id = templateids[char['id']]['Id']
                        except:
                            logger.debug(f'Character {char} is proving difficult to import from file {fi}')
                            raise


                    if not char_id.startswith('SBB_CHARACTER'):
                        raise ValueError(f'Wrong template-ids file used with this data, id {char["id"]} maps to name {char_id} which is not a character')
                    char['id'] = char_id
                
                # Update treasure template ids to the SBB Ids
                new_treasures = list()
                for treasure in board['treasures']:
                    treasure_id = templateids[treasure]['Id']
                    if not treasure_id.startswith('SBB_TREASURE'):
                        raise ValueError(f'Wrong template-ids file used with this data, id {treasure} maps to name {treasure_id} which is not a treasure')
                    new_treasures.append(treasure_id)
                board['treasures'] = new_treasures

                # Update spell tempalte ids to the SBB Ids
                new_spells = list()
                for spell in board['spells']:
                    spell_id = templateids[spell]['Id']
                    if not spell_id.startswith('SBB_SPELL'):
                        raise ValueError(f'Wrong template-ids file used with this data, id {spell} maps to name {spell_id} which is not a spell')
                    new_spells.append(spell_id)
                board['spells'] = new_spells

                # Update hero template ids to the SBB ids
                hero_id = templateids[board['hero']]['Id']
                if not hero_id.startswith('SBB_HERO'):
                    raise ValueError(f'Wrong template-ids file used with this data file, id {hero} maps to name {hero_id} which is not a hero')
                board['hero'] = hero_id

                new_combat[player] = board

            new_combat_info.append({'combat': new_combat, 'round': combat['round']})
        
        data['combat-info'] = new_combat_info
        GLOBAL_DATA.add_file(fi, data)
        
