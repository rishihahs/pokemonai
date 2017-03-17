from typing import Tuple, Optional, Sequence, Any
import pkgutil
import json
import re
import random

# Load pokedex
pokedex = json.loads(pkgutil.get_data('pokemonai', 'data/pokedex.json'))

# Extract JSON from Smogon action request
request_regex = re.compile(r"\|request\|(.+?)$")
# Extract player id for a game
player_regex = re.compile(r"\|player\|(.+?)\|(.+?)\|")
# Extract opponent's pokemon
poke_regex = lambda pid: "\\|poke\\|%s\\|(.+?)\\|" % pid
# Extract active pokemon
switch_regex = lambda pid: "\\|switch\\|%s.+?\\|(.+?)\\|" % pid

class BattleHandler(object):

    def __init__(self, roomid: str, username: str):
        self.roomid = roomid
        self.username = username
        self.pid = None # Player id in game
        self.opponent_pid = None # Opponent player id in game
        self.battledata = BattleData()


    def parse(self, message: str) -> Tuple[Optional[str], bool]:
        done = False
        response = None

        # Extract player ids
        if '|player|' in message:
            m = player_regex.search(message)
            pid = m.group(1)
            uname = m.group(2)
            if uname == self.username:
                self.pid = pid
            else:
                self.opponent_pid = pid

        # Extract opponent's pokemon from team preview
        if '|poke|' in message:
            assert(self.opponent_pid) # We should already know their pid
            matches = re.finditer(poke_regex(self.opponent_pid), message)
            self.battledata.record_opponent_team([m.group(1) for m in matches])
            print(self.battledata.opponent_team)

        # Extract active pokemon
        if '|switch|' in message:
            m = re.search(switch_regex(self.opponent_pid), message)
            self.battledata.record_opponent_active(m.group(1))

        # Smogon is requesting an action or switch
        if '|request|' in message:
            # Data provided with request (i.e. team info)
            request_data = json.loads(request_regex.search(message).group(1))

            if request_data.get('teamPreview'):
                choice = self.team_preview(request_data["side"]["pokemon"])
                return ('/team %s' % ''.join(map(str, choice)), done)
            elif 'ZMove' in message:
                return ('/choose move 1 zmove', done)
            else:
                return ('/choose move 1', done)

        if '|win|' in message or '|lose|' in message:
            done = True

        return (response, done)


    """
    Given a list of pokemon (team)
    returns the order in which team should play
    """
    def team_preview(self, pokemon: Sequence[Any]) -> Sequence[int]:
        # For now random
        choices = list(range(1, len(pokemon)))
        random.shuffle(choices)
        return choices


class BattleData(object):

    def __init__(self):
        self.player_team = [] # Our team
        self.player_active = None # Our active pokemon in battle
        self.opponent_team = []
        self.opponent_active = None

    """
    Given a Smogon pokemon description,
    sets that opponent's active pokemon
    """
    def record_opponent_active(self, pokemon: str) -> None:
        attrs = pokemon.split(',')
        pokeid = attrs[0].lower().replace('-', '')
        self.opponent_active = any(p for p in self.opponent_team if p['id'] == pokeid)

    """
    Given a list of Smogon pokemon descriptions (i.e. from team preview)
    cross references with pokedex to record opponent's team
    """
    def record_opponent_team(self, pokemon: Sequence[str]) -> None:
        normalized = [] # Normalized names to index into pokedex
        genders = []
        for p in pokemon:
            attrs = p.split(',')
            normalized.append(attrs[0].lower().replace('-', ''))
            genders.append(attrs[1] if 1 < len(attrs) else None) # Gender or None if no gender

        # Set opponent's team
        self.opponent_team = []
        for idx, name in enumerate(normalized):
            poke = pokedex[name]
            self.opponent_team.append({
                'baseStats': poke['baseStats'],
                'weightkg': poke['weightkg'],
                'types': poke['types'],
                'species': poke['species'],
                'gender': genders[idx],
                'id': name
            })


