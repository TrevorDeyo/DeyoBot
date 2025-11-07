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

created_channels = []

@bot.event
# function that watches for users moving/joining voice channels
async def on_voice_state_update(member, before, after):

    # Check if user joined the voice channel titled "Create Voice Channel"
    if after.channel and after.channel.name == "Create Voice Channel":

        # Create a new voice channel named after the user
        guild = after.channel.guild
        new_channel = await guild.create_voice_channel(
            f"{member.name}'s channel",
            category=after.channel.category,
            position=after.channel.position
        )

        created_channels.append(new_channel.id)

        # Move the user into the channel
        await member.move_to(new_channel)


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
    if interaction.user.voice and interaction.user.voice.channel:
        if interaction.user.voice.channel.id in created_channels:
            channel = interaction.user.voice.channel
            perms = channel.overwrites_for(interaction.guild.default_role)
            perms.connect = False
            await channel.set_permissions(interaction.guild.default_role, overwrite=perms)
            await interaction.response.send_message("Channel locked.", ephemeral=True)
        else:
            await interaction.response.send_message("You can only lock temporary channels.", ephemeral=True)
    else:
        await interaction.response.send_message("You must be in your temporary channel.", ephemeral=True)


@tree.command(name="unlock", description="Unlock your temporary voice channel.")
async def unlock(interaction: discord.Interaction):
    if interaction.user.voice and interaction.user.voice.channel:
        if interaction.user.voice.channel.id in created_channels:
            channel = interaction.user.voice.channel
            perms = channel.overwrites_for(interaction.guild.default_role)
            perms.connect = True
            await channel.set_permissions(interaction.guild.default_role, overwrite=perms)
            await interaction.response.send_message("Channel unlocked.", ephemeral=True)
        else:
            await interaction.response.send_message("You can only unlock temporary channels.", ephemeral=True)
    else:
        await interaction.response.send_message("You must be in your temporary channel.", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")

bot.run(TOKEN) # type: ignore