## logic for palermo game
from characters import characters
import random

basic_roles = [role["name"] for role in characters if role["is_main_role"]]




def assign_roles(player_names, roles_config):
    roles = []
    if len(roles_config) == 0:
        roles = basic_roles
    else:
        roles = roles.append(roles_config)
    

    random.shuffle(roles)
    return dict(zip(player_names, roles))


player_names = ["Player1", "Player2", "Player3, Player4", "Player5"]
roles_config = []
assigned_roles = assign_roles(player_names, roles_config)
print("Assigned Roles:", assigned_roles)
