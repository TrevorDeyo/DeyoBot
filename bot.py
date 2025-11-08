import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

# Load environment variables (Discord bot token and configuration values)
load_dotenv()
TOKEN = os.getenv('discord_token')

# Configure bot intents to allow voice state tracking, message events, and presence updates
intents = discord.Intents.all()

# Initialize the bot with slash command (app_commands) support
bot = commands.Bot(command_prefix='/', intents=intents)
tree = bot.tree

# Channel ID used for centralized server activity logging
LOG_CHANNEL_ID = 1436374842596393093

# Store dynamically-created temporary voice channel IDs for management and cleanup
created_channels = []


class ChannelControls(discord.ui.View):
    """
    Interactive UI panel delivered via direct message to the owner of a temporary voice channel.
    This panel provides convenient channel management actions (rename, lock, unlock) without requiring commands.
    """
    def __init__(self, channel: discord.VoiceChannel):
        super().__init__(timeout=None)
        self.channel = channel

    @discord.ui.button(label="Rename", style=discord.ButtonStyle.primary)
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Prompts the user for a new channel name and applies it.
        """
        await interaction.response.send_message("Enter a new channel name:", ephemeral=True)

        def check(msg):
            return msg.author == interaction.user and isinstance(msg.channel, discord.DMChannel)

        msg = await bot.wait_for("message", check=check)
        await self.channel.edit(name=msg.content)
        await interaction.followup.send(f"Channel renamed to **{msg.content}**.", ephemeral=True)

    @discord.ui.button(label="Lock", style=discord.ButtonStyle.danger)
    async def lock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Restricts channel access to prevent new users from joining.
        """
        await self.channel.set_permissions(self.channel.guild.default_role, connect=False)
        await interaction.response.send_message("Channel locked.", ephemeral=True)

    @discord.ui.button(label="Unlock", style=discord.ButtonStyle.success)
    async def unlock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Restores the ability for users to join the voice channel.
        """
        await self.channel.set_permissions(self.channel.guild.default_role, connect=True)
        await interaction.response.send_message("Channel unlocked.", ephemeral=True)


@bot.event
async def on_voice_state_update(member, before, after):
    """
    Core event handler for dynamic voice channel management and voice activity logging.

    Responsibilities:
    - Automatically create a private temporary voice channel when a user joins the trigger channel.
    - Clean up temporary channels when empty.
    - Log join/leave/move events to the central logging channel.
    """

    # Create a personal temporary channel when a user enters the designated trigger channel
    if after.channel and after.channel.name == "Create Voice Channel":
        guild = after.channel.guild
        new_channel = await guild.create_voice_channel(
            f"{member.name}'s channel",
            category=after.channel.category,
            position=after.channel.position
        )

        created_channels.append(new_channel.id)
        await member.move_to(new_channel)

        # Provide channel controls to the user via DM (silent fail if user has DMs disabled)
        try:
            await member.send(
                f"Your personal voice channel **{new_channel.name}** is ready.\n"
                "Use the buttons below to manage it:",
                view=ChannelControls(new_channel)
            )
        except:
            pass

    # Automatically remove a temporary channel once it is empty
    if before.channel and before.channel.id in created_channels and not before.channel.members:
        await before.channel.delete()
        created_channels.remove(before.channel.id)

    # Log voice activity transitions
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
    Allows the channel owner to rename their active temporary channel.
    """
    channel = interaction.user.voice.channel if interaction.user.voice else None
    if channel and channel.id in created_channels:
        await channel.edit(name=new_name)
        await interaction.response.send_message(f"Channel renamed to {new_name}.", ephemeral=True)
    else:
        await interaction.response.send_message("You must be in your temporary voice channel to rename it.", ephemeral=True)


@tree.command(name="lock", description="Lock your temporary voice channel.")
async def lock(interaction: discord.Interaction):
    """
    Prevents new users from joining the temporary channel.
    """
    channel = interaction.user.voice.channel if interaction.user.voice else None
    if channel and channel.id in created_channels:
        await channel.set_permissions(interaction.guild.default_role, connect=False)
        await interaction.response.send_message("Channel locked.", ephemeral=True)
    else:
        await interaction.response.send_message("You must be in your temporary voice channel to lock it.", ephemeral=True)


@tree.command(name="unlock", description="Unlock your temporary voice channel.")
async def unlock(interaction: discord.Interaction):
    """
    Re-allows new users to join the temporary channel.
    """
    channel = interaction.user.voice.channel if interaction.user.voice else None
    if channel and channel.id in created_channels:
        await channel.set_permissions(interaction.guild.default_role, connect=True)
        await interaction.response.send_message("Channel unlocked.", ephemeral=True)
    else:
        await interaction.response.send_message("You must be in your temporary voice channel to unlock it.", ephemeral=True)


@bot.event
async def on_message(message):
    """
    Logs all user-generated messages to the central logging channel for moderation visibility.
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
    Captures deleted messages to preserve moderation history and prevent evidence loss.
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
    Logs message edits to maintain transparency and detect content manipulation.
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
    Synchronizes command definitions and confirms successful bot startup.
    """
    await bot.tree.sync()
    print(f"Bot is now running as: {bot.user}")


bot.run(TOKEN)
