# DeyoBot

DeyoBot is a Discord moderation and utility bot designed to automatically manage temporary voice channels, log user message activity, and provide convenient user controls via an interactive UI panel. The bot is easy to configure and maintain, making it suitable both for community servers and professional development demonstration.

## Features

### Dynamic Voice Channels
- Users who join the **Create Voice Channel** trigger channel automatically receive their own temporary voice channel.
- Channels are deleted automatically once empty.
- Users receive a **private control panel** (Rename / Lock / Unlock buttons).

### Moderation Logging
All logged to a private `#logs` channel:
- Messages sent
- Messages deleted
- Message edits (before and after)
- Voice channel joins, leaves, and moves

### Slash Commands
For direct and private channel management:
```
/rename <new_name>
/lock
/unlock
```

### Interactive Controls (No Commands Needed)
Users receive DM controls to:
- Rename their voice channel
- Lock it from being joined
- Unlock it for public joining

## Installation & Setup

### Prerequisites
- Python 3.10 or newer
- Discord Bot Token
- A server where you have permission to add bots

### 1. Clone the Repository
```
git clone <your repo link>
cd DeyoBot
```

### 2. Create and Activate a Virtual Environment
```
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate    # Windows
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create `.env` in the project root:
```
discord_token=YOUR_DISCORD_BOT_TOKEN_HERE
```

### 5. Run the Bot
```
python bot.py
```

## Configuration

### Logging Channel
Find your private logs channel ID:
- Enable Developer Mode in Discord
- Right-click `#logs` → Copy Channel ID
Update in `bot.py`:
```
LOG_CHANNEL_ID = <your id>
```

### Trigger Channel Name
The channel that triggers creation must be named exactly:
```
Create Voice Channel
```

## Project Structure
```
.
├── bot.py          # Main bot logic
├── .env            # Environment variables (not version controlled)
├── requirements.txt
├── README.md
```

## License
This project is free to use and modify for personal or professional purposes.

---