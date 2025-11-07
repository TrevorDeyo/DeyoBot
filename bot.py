import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('discord_token')

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='/', intents=intents)
tree = bot.tree # this is the slash command handler

class ChannelControls(discord.ui.View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.channel = channel

    @discord.ui.button(label="Rename", style=discord.ButtonStyle.primary)
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Send the new channel name:", ephemeral=True)

        def check(message):
            return message.author == interaction.user and isinstance(message.channel, discord.DMChannel)

        msg = await bot.wait_for("message", check=check)
        await self.channel.edit(name=msg.content)
        await interaction.followup.send(f"✅ Renamed to **{msg.content}**", ephemeral=True)

    @discord.ui.button(label="Lock", style=discord.ButtonStyle.danger)
    async def lock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.channel.set_permissions(
            self.channel.guild.default_role,
            connect=False
        )
        await interaction.response.send_message("🔒 Channel locked.", ephemeral=True)

    @discord.ui.button(label="Unlock", style=discord.ButtonStyle.success)
    async def unlock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.channel.set_permissions(
            self.channel.guild.default_role,
            connect=True
        )
        await interaction.response.send_message("🔓 Channel unlocked.", ephemeral=True)


created_channels = []

@bot.event
# function that watches for users moving/joining voice channels
async def on_voice_state_update(member, before, after):

    # Check if user joined the voice channel titled "Create Voice Channel"
    if after.channel and after.channel.name == "Create Voice Channel":
        guild = after.channel.guild
        new_channel = await guild.create_voice_channel(
            f"{member.name}'s channel",
            category=after.channel.category,
            position=after.channel.position
        )

        created_channels.append(new_channel.id)
        await member.move_to(new_channel)

        # Send control panel to the user
        try:
            await member.send(
                f"🎛 **Your Voice Channel Controls**\nYou can manage **{new_channel.name}** using the buttons below:",
                view=ChannelControls(new_channel)
            )
        except:
            print("⚠️ Could not DM user (their DMs are closed).")

    # Check if user left a voice channel
    if before.channel:

        # Check if channel is in the list of created channels
        if before.channel.id in created_channels:

            # Check if channel is empty
            if not before.channel.members:

                # Delete the channel
                await before.channel.delete()

                # Remove the channel's ID from the list of created channels
                created_channels.remove(before.channel.id)

@tree.command(name="rename", description="Rename your temporary voice channel.")
async def rename(interaction: discord.Interaction, new_name: str):
    if interaction.user.voice and interaction.user.voice.channel:
        if interaction.user.voice.channel.id in created_channels:
            await interaction.user.voice.channel.edit(name=new_name)
            await interaction.response.send_message(f"Renamed to {new_name}.", ephemeral=True)
        else:
            await interaction.response.send_message("You can only rename temporary channels.", ephemeral=True)
    else:
        await interaction.response.send_message("You must be in your temporary channel.", ephemeral=True)


@tree.command(name="lock", description="Lock your temporary voice channel.")
async def lock(interaction: discord.Interaction):
    channel = interaction.user.voice.channel if interaction.user.voice else None

    if channel is None or channel.id not in created_channels:
        return await interaction.response.send_message(
            "You must be in your temporary voice channel to lock it.",
            ephemeral=True
        )

    # Deny connect for @everyone
    await channel.set_permissions(
        interaction.guild.default_role,
        connect=False
    )

    await interaction.response.send_message("🔒 Channel locked.", ephemeral=True)


@tree.command(name="unlock", description="Unlock your temporary voice channel.")
async def unlock(interaction: discord.Interaction):
    channel = interaction.user.voice.channel if interaction.user.voice else None

    if channel is None or channel.id not in created_channels:
        return await interaction.response.send_message(
            "You must be in your temporary voice channel to unlock it.",
            ephemeral=True
        )

    # Allow connect for @everyone
    await channel.set_permissions(
        interaction.guild.default_role,
        connect=True
    )

    await interaction.response.send_message("🔓 Channel unlocked.", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")

bot.run(TOKEN) # type: ignore