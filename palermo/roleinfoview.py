import discord
from discord import app_commands
from discord.ui import View, Select
from discord import Interaction, Embed, SelectOption
from characters import characters


class RoleDropdown(Select):
    def __init__(self):
        # Φτιάχνουμε options από τη λίστα χαρακτήρων
        options = [
            SelectOption(
                label=char["name"],
                description=char["description"][:95] + ("..." if len(char["description"]) > 100 else ""),
                value=char["name"]
            )
            for char in characters
        ]

        super().__init__(
            placeholder="Διάλεξε ρόλο για να δεις την περιγραφή του",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: Interaction):
        selected_role = self.values[0]
        role_data = next((c for c in characters if c["name"] == selected_role), None)

        if not role_data:
            await interaction.response.send_message("❌ Δεν βρέθηκε ο ρόλος.", ephemeral=True)
            return

        team = "🟢 Καλοί" if role_data["team"] == "Good" else "🔴 Κακοί"

        embed = Embed(
            title=f"{role_data['name']} ({team})",
            description=role_data["description"],
            color=discord.Color.green() if role_data["team"] == "Good" else discord.Color.red()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


class RoleInfoView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleDropdown())
