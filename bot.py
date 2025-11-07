import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

# Load environment variables (Discord bot token)
load_dotenv()
TOKEN = os.getenv('discord_token')

# Enable full intent access for voice, message, and presence events
intents = discord.Intents.all()

# Create bot instance with slash command support
bot = commands.Bot(command_prefix='/', intents=intents)
tree = bot.tree  # Slash command interface

# ID of the private logging channel used for server activity auditing
LOG_CHANNEL_ID = 1436374842596393093

# Tracks dynamically created temporary voice channels
created_channels = []


class ChannelControls(discord.ui.View):
    """
    Interactive UI panel sent to users via DM.
    Allows the owner of a dynamically-created voice channel
    to rename, lock, or unlock it without typing commands.
    """
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.channel = channel

    @discord.ui.button(label="Rename", style=discord.ButtonStyle.primary)
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Prompt the user privately for a new channel name
        await interaction.response.send_message("Please enter the new channel name:", ephemeral=True)

        def check(message):
            return message.author == interaction.user and isinstance(message.channel, discord.DMChannel)

        msg = await bot.wait_for("message", check=check)
        await self.channel.edit(name=msg.content)
        await interaction.followup.send(f"Channel renamed to **{msg.content}**.", ephemeral=True)

    @discord.ui.button(label="Lock", style=discord.ButtonStyle.danger)
    async def lock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Prevent all users from joining the voice channel
        await self.channel.set_permissions(self.channel.guild.default_role, connect=False)
        await interaction.response.send_message("Channel locked.", ephemeral=True)

    @discord.ui.button(label="Unlock", style=discord.ButtonStyle.success)
    async def unlock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Allow users to join the voice channel again
        await self.channel.set_permissions(self.channel.guild.default_role, connect=True)
        await interaction.response.send_message("Channel unlocked.", ephemeral=True)


@bot.event
async def on_voice_state_update(member, before, after):
    """
    Handles dynamic voice channel management and voice activity logging.
    - Creates a personal voice channel when a user joins the designated channel.
    - Deletes temporary channels when empty.
    - Logs all voice join, leave, and move events.
    """

    # Dynamically create a personal channel when joining the trigger channel
    if after.channel and after.channel.name == "Create Voice Channel":
        guild = after.channel.guild
        new_channel = await guild.create_voice_channel(
            f"{member.name}'s channel",
            category=after.channel.category,
            position=after.channel.position
        )

        created_channels.append(new_channel.id)
        await member.move_to(new_channel)

        # Send voice channel controls via DM
        try:
            await member.send(
                f"Your personal voice channel **{new_channel.name}** has been created.\n"
                "Use the controls below to manage it:",
                view=ChannelControls(new_channel)
            )
        except:
            # DMs blocked — silently skip
            pass

    # Automatically delete empty temporary channels
    if before.channel and before.channel.id in created_channels:
        if not before.channel.members:
            await before.channel.delete()
            created_channels.remove(before.channel.id)

    # Voice activity logging
    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    if before.channel != after.channel and log_channel:
        if before.channel is None:
            await log_channel.send(f"🔊 **Voice Join:** {member} joined **{after.channel.name}**")
        elif after.channel is None:
            await log_channel.send(f"🚪 **Voice Leave:** {member} left **{before.channel.name}**")
        else:
            await log_channel.send(f"➡️ **Voice Move:** {member} moved from **{before.channel.name}** to **{after.channel.name}**")


@tree.command(name="rename", description="Rename your temporary voice channel.")
async def rename(interaction: discord.Interaction, new_name: str):
    """
    Slash command version of channel renaming.
    Used as an alternative to the UI controls.
    """
    if interaction.user.voice and interaction.user.voice.channel and interaction.user.voice.channel.id in created_channels:
        await interaction.user.voice.channel.edit(name=new_name)
        await interaction.response.send_message(f"Channel renamed to {new_name}.", ephemeral=True)
    else:
        await interaction.response.send_message("You must be inside your temporary voice channel.", ephemeral=True)


@tree.command(name="lock", description="Lock your temporary voice channel.")
async def lock(interaction: discord.Interaction):
    """
    Prevents all users from joining the channel except members already inside.
    """
    channel = interaction.user.voice.channel if interaction.user.voice else None

    if not channel or channel.id not in created_channels:
        return await interaction.response.send_message("You must be inside your temporary voice channel.", ephemeral=True)

    await channel.set_permissions(interaction.guild.default_role, connect=False)
    await interaction.response.send_message("Channel locked.", ephemeral=True)


@tree.command(name="unlock", description="Unlock your temporary voice channel.")
async def unlock(interaction: discord.Interaction):
    """
    Re-allows other users to join the temporary channel.
    """
    channel = interaction.user.voice.channel if interaction.user.voice else None

    if not channel or channel.id not in created_channels:
        return await interaction.response.send_message("You must be inside your temporary voice channel.", ephemeral=True)

    await channel.set_permissions(interaction.guild.default_role, connect=True)
    await interaction.response.send_message("Channel unlocked.", ephemeral=True)


@bot.event
async def on_message(message):
    """
    Logs all non-bot messages to the designated logging channel.
    """
    if not message.author.bot:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"💬 **Message Sent**\n"
                f"User: {message.author} (`{message.author.id}`)\n"
                f"Channel: {message.channel}\n"
                f"Content: {message.content}"
            )

    await bot.process_commands(message)


@bot.event
async def on_message_delete(message):
    """
    Logs deleted messages so that moderation history is preserved.
    """
    if not message.author.bot:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"🗑️ **Message Deleted**\n"
                f"User: {message.author} (`{message.author.id}`)\n"
                f"Channel: {message.channel}\n"
                f"Deleted Content: {message.content}"
            )


@bot.event
async def on_message_edit(before, after):
    """
    Logs message edits to track changed or hidden content.
    """
    if not before.author.bot and before.content != after.content:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"✏️ **Message Edited**\n"
                f"User: {before.author} (`{before.author.id}`)\n"
                f"Channel: {before.channel}\n"
                f"Before: {before.content}\n"
                f"After: {after.content}"
            )


@bot.event
async def on_ready():
    """
    Syncs slash commands and confirms the bot is running.
    """
    await bot.tree.sync()
    print(f"Bot is online: {bot.user}")


bot.run(TOKEN)
