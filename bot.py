import discord
import asyncio
from discord.ext import commands
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('env_token')

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='/', intents=intents)

created_channels = []
user_cooldown = {}

@bot.event
# function that watches for users moving/joining voice channels
async def on_voice_state_update(member, before, after):

    # Check if user joined the voice channel titled "Create Voice Channel"
    if after.channel and after.channel.name == "Create Voice Channel":

        # Check if user has exceeded the cooldown
        now = datetime.now()
        cooldown = 5
        if member.id not in user_cooldown or now - user_cooldown[member.id] > timedelta(seconds=cooldown):

            # Create a new voice channel named after the user
            guild = after.channel.guild
            new_channel = await guild.create_voice_channel(f"{member.name}'s channel",
                category=after.channel.category, position=after.channel.position)
            
            # append created channel id to created channels list
            created_channels.append(new_channel.id)

            # Move the user to the new channel
            await member.move_to(new_channel)

            # Update the cooldown for the user
            user_cooldown[member.id] = now

            # wait for 15 seconds
            await asyncio.sleep(15)

            # Remove the cooldown entry for the member
            del user_cooldown[member.id]
        else:
            # Tell the user they need to wait before creating another channel
            await member.send(f"You must wait {cooldown} seconds before creating another channel.")

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

@bot.command()
async def rename(ctx, new_name: str):

    # Check if user is in a voice channel
    if ctx.author.voice and ctx.author.voice.channel:
        
        # Check if voice channel is in the list of created channels
        if ctx.author.voice.channel.id in created_channels:
    
            # Rename the voice channel
            await ctx.author.voice.channel.edit(name=new_name)
            await ctx.send(f"Voice channel renamed to {new_name}.")
        else:
            await ctx.send("You can only rename created voice channels.")
    else:
        await ctx.send("You need to be in a created voice channel to use this command.")



@bot.command()
async def lock(ctx):

    # Check if user is in a voice channel
    if ctx.author.voice and ctx.author.voice.channel:

        # Check if voice channel is in the list of created channels
        if ctx.author.voice.channel.id in created_channels:

            # Set the permissions for the voice channel to prevent users from joining
            channel = ctx.author.voice.channel
            permissions = channel.overwrites_for(ctx.guild.default_role)
            permissions.connect = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=permissions)
            await ctx.send("Voice channel locked.")
        else:
            await ctx.send("You can only lock created voice channels.")
    else:
        await ctx.send("You need to be in a voice channel to use this command.")

@bot.command()
async def unlock(ctx):
    # Check if user is in a voice channel
    if ctx.author.voice and ctx.author.voice.channel:
        # Check if voice channel is in the list of created channels
        if ctx.author.voice.channel.id in created_channels:
            # Set the permissions for the voice channel to allow users to join
            channel = ctx.author.voice.channel
            permissions = channel.overwrites_for(ctx.guild.default_role)
            permissions.connect = True
            await channel.set_permissions(ctx.guild.default_role, overwrite=permissions)
            await ctx.send("Voice channel unlocked.")       
        else:
            await ctx.send("You can only unlock created voice channels.")
    else:
        await ctx.send("You need to be in a voice channel to use this command.")

bot.run(TOKEN) # type: ignore