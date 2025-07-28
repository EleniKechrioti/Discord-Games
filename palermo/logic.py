## logic for palermo game
from characters import characters
import random

from role import Role
import asyncio
import discord

EMOJIS = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟",
    "🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯"
]
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

async def run_day_phase(channel, players, bot):
    alive_players = [p for p in players if p.is_alive()]
    if(len(alive_players)<2):
        return
    emoji_map = {}
    vote_tracker = {}  # user_id: emoji

    # --- Create Voting Message ---
    message_lines = ["☀️ **Ψηφίστε ποιος να πεθάνει:**"]
    for idx, player in enumerate(alive_players):
        emoji = EMOJIS[idx]
        emoji_map[emoji] = player
        message_lines.append(f"{emoji} → {player.display_name}")
    msg = await channel.send("\n".join(message_lines))

    # --- Add Reactions ---
    for emoji in emoji_map:
        await msg.add_reaction(emoji)

    # --- Reset votes ---
    for p in players:
        p.reset_votes()

    # --- Reaction Handling ---
    def check_event(reaction, user):
    # Αντιστοιχία user ID -> player
        player = get_player_by_id(user.id)

        return (
            reaction.message.id == msg.id
            and not user.bot
            and reaction.emoji in emoji_map
            and player is not None
            and player.is_alive  # <--- Εδώ το φίλτρο
        )

    def get_player_by_id(user_id):
        for p in players:
            if p.discord_user.id == user_id:
                return p
        return None

    # Track time and user interactions
    last_activity = asyncio.get_event_loop().time()

    async def handle_vote(user_id, emoji, is_add):
        if user_id not in vote_tracker:
            vote_tracker[user_id] = None

        current_vote = vote_tracker[user_id]

        if is_add:
            # Remove vote from previous emoji (if any)
            if current_vote and current_vote != emoji:
                emoji_map[current_vote].votes -= 1
            vote_tracker[user_id] = emoji
            emoji_map[emoji].add_vote()
        else:
            # Remove only if the removed emoji matches current vote
            if current_vote == emoji:
                vote_tracker[user_id] = None
                emoji_map[emoji].votes -= 1
        if not player.is_alive:
            await reaction.message.remove_reaction(reaction.emoji, user)
            await channel.send(f"{user.mention}, είσαι νεκρός 💀. Δεν ψηφίζεις πλέον.")

    # Wait loop with timeout
    while True:
        try:
            done, _ = await asyncio.wait(
                [
                    asyncio.create_task(wait_for_reaction_add(bot, check_event)),
                    asyncio.create_task(wait_for_reaction_remove(bot, check_event)),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in done:
                event_type, reaction, user = await task
                await handle_vote(user.id, reaction.emoji, is_add=(event_type == "add"))
        except asyncio.TimeoutError:
            if asyncio.get_event_loop().time() - last_activity > 15:
                break  # No activity for 15s → end vote

    # --- Count Votes ---
    voted_out = determine_elimination(players)
    if voted_out:
        voted_out.kill()
        await channel.send(f"💀 Ο **{voted_out.display_name}** εκτελέστηκε από το χωριό.")
    else:
        await channel.send("😐 Κανείς δεν πήρε αρκετές ψήφους. Δεν εκτελέστηκε κανείς.")

def run_night_phase(channel, players, bot):
    pass

async def wait_for_reaction_add(bot, check_event):
    reaction, user = await bot.wait_for("reaction_add", timeout=10, check=check_event)
    return "add", reaction, user

async def wait_for_reaction_remove(bot, check_event):
    reaction, user = await bot.wait_for("reaction_remove", timeout=10, check=check_event)
    return "remove", reaction, user


def determine_elimination(players):
    alive = [p for p in players if p.is_alive()]
    max_votes = max((p.votes for p in alive), default=0)
    top_voted = [p for p in alive if p.votes == max_votes and max_votes > 0]
    if len(top_voted) == 1:
        return top_voted[0]
    return None 


def is_game_over(players):
    alive_players = [p for p in players if p.is_alive]
    mafia_count = sum(1 for p in alive_players if p.role.alignment == "Bad")
    town_count = sum(1 for p in alive_players if p.role.alignment == "Good")

    if mafia_count == 0:
        return "good"
    elif mafia_count >= town_count:
        return "bad"
    return None



