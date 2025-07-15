# 🔊 Auto Voice Channel Creator Discord Bot

A Discord bot that automatically creates, manages, and cleans up temporary voice channels. Users can also rename, lock, and unlock their personal voice channels using slash-style commands.

## 📌 Features

- ✅ Auto-creates a personal voice channel when a user joins a special channel
- 🕒 Cooldown prevents users from spamming channel creation (default: 5 seconds)
- 🧹 Deletes the voice channel automatically when it's empty
- ✏️ Users can rename their voice channels
- 🔒 Voice channels can be locked or unlocked by their creator

## ⚙️ Setup Instructions

**1. Install Python packages**

Run the following command:

pip install -U discord.py python-dotenv

**2. Create a `.env` file**

In the same directory as your script, add the following:

env_token=YOUR_DISCORD_BOT_TOKEN

Replace `YOUR_DISCORD_BOT_TOKEN` with your actual bot token from the [Discord Developer Portal](https://discord.com/developers/applications).

**3. Run the bot**

Make sure your script is saved (e.g., `bot.py`), then run:

python bot.py

## 🧪 Available Commands

- `/rename <new_name>` — Rename your temporary voice channel
- `/lock` — Lock your voice channel to prevent others from joining
- `/unlock` — Unlock your voice channel to allow others to join

> Commands only work in channels created by the bot.

## 📋 Behavior

- When a user joins a voice channel named `Create Voice Channel`, a new channel is created for them.
- They are moved into the new channel automatically.
- A 5-second cooldown prevents repeat creations.
- The channel is deleted automatically when no one is left in it.
- Users can control access and customize their channel via commands.

## 🛡️ Bot Permissions

Make sure the bot has the following permissions in your server:

- Manage Channels
- Move Members
- Connect
- Speak
- View Channel
