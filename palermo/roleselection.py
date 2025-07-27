import discord
from discord import app_commands, Interaction, Embed, SelectOption
from discord.ui import View, Select
from discord.ext import commands, tasks
from characters import characters

class RoleCountModal(discord.ui.Modal, title="Πόσοι θα έχουν αυτόν τον ρόλο;"):
    def __init__(self, role_name, active_games):
        super().__init__()
        self.role_name = role_name
        self.active_games = active_games
        self.count_input = discord.ui.TextInput(
            label=f"Αριθμός για {role_name}",
            placeholder="Π.χ. 2",
            required=True
        )
        self.add_item(self.count_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            count = int(self.count_input.value)
            channel_id = interaction.channel.id
            game = self.active_games.get(channel_id)
            if game:
                roles_config = game.setdefault("roles_config", {})
                roles_config[self.role_name] = count
                await interaction.response.send_message(f"✅ Προστέθηκε: {self.role_name}: {count}")
        except ValueError:
            await interaction.response.send_message("❌ Πρέπει να είναι αριθμός!", ephemeral=True)


class RoleSelect(discord.ui.Select):
    def __init__(self, active_games):
        options = [discord.SelectOption(label=role["name"]) for role in characters]
        self.active_games = active_games
        super().__init__(placeholder="Επίλεξε ρόλο για προσθήκη", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_role = self.values[0]
        await interaction.response.send_modal(RoleCountModal(selected_role, self.active_games))

class RoleSetupView(discord.ui.View):
    def __init__(self, active_games):
        super().__init__(timeout=300)
        self.active_games = active_games
        self.add_item(RoleSelect(active_games))
