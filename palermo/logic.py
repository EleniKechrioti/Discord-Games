## logic for palermo game
from characters import characters
import random

from role import Role

basic_roles = [(role["name"], role["num_of_players"]) for role in characters if role["is_main_role"]]



def assign_roles(p, roles_config):
    players = p.copy()
    roles = []
    if len(roles_config) == 0:
        roles = basic_roles

    else:
        roles = roles_config #roles.append(roles_config)

    random_roles = []

    for role , count in roles.items(): # {'Πολίτης':1, 'Κρυφός': 1}
        while count > 0:
            random_roles.append(role)
            count -= 1

    random.shuffle(random_roles)
    
    roles_to_assign = len(random_roles)
    
    if roles_to_assign > len(players):
        raise ValueError("More roles than players")
    
    
    for i in range(roles_to_assign):
        role_lookup = {role["name"]: role for role in characters}
        data = role_lookup.get(random_roles[i])
        actual_role = Role(data["name"], data["description"], data["team"])

        player = players.pop(0)
        player.set_role(actual_role)

def run_day_phase(channel, players):
    pass

def run_night_phase(channel, players):
    pass

def is_game_over(game):
    alive_players = [p for p in game["players"] if p.is_alive]
    mafia_count = sum(1 for p in alive_players if p.role["alignment"] == "bad")
    town_count = sum(1 for p in alive_players if p.role["alignment"] == "good")

    if mafia_count == 0:
        return "good"
    elif mafia_count >= town_count:
        return "bad"
    return None



