from typing import Tuple, Optional, Sequence, Any
import json
import re
import random

# Extract JSON from Smogon action request
request_regex = re.compile(r"\|request\|(.+?)$")
# Extract player id for a game
player_regex = re.compile(r"\|player\|(.+?)\|(.+?)\|")
# Extract opponent's pokemon
poke_regex = lambda pid: "\\|poke\\|%s\\|(.+?)\\|" % pid

class BattleHandler(object):

    def __init__(self, roomid: str, username: str):
        self.roomid = roomid
        self.username = username
        self.pid = None # Player id in game
        self.opponent_pid = None # Opponent player id in game


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
            for m in matches:
                pokemon = m.group(1)
                print('\x1b[6;30;42m' + pokemon + '\x1b[0m')

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
        pass

