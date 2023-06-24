import subprocess
import os

from dotenv import load_dotenv
load_dotenv()

# Define the SSH parameters
ssh_host = os.getenv('ssh_host')
ssh_user = os.getenv('ssh_user')
ssh_pass = os.getenv('ssh_pw')

# 1. SCP the folder
scp_cmd = f'scp -r C:/Users/tdeyo/Desktop/Code/DeyoBot {ssh_user}@{ssh_host}:/home/deyo'
subprocess.run(scp_cmd, shell=True, input=f"{ssh_pass}\n", text=True)

# 2. SSH to the server and resume screen session
ssh_cmd = f'ssh {ssh_user}@{ssh_host} "screen -r"'
subprocess.run(ssh_cmd, shell=True, input=f"{ssh_pass}\n", text=True)

# 3. Stop the bot
ssh_cmd = 'echo "\003" > /dev/tty'
subprocess.run(ssh_cmd, shell=True, input=f"{ssh_pass}\n", text=True)

# 4. Start the bot
ssh_cmd = 'python3 /home/deyo/DeyoBot/bot.py'
subprocess.run(ssh_cmd, shell=True, input=f"{ssh_pass}\n", text=True)

# 5. Detach from the screen session
ssh_cmd = 'echo "\001d" > /dev/tty'
subprocess.run(ssh_cmd, shell=True, input=f"{ssh_pass}\n", text=True)

# 6. Close the connection
ssh_cmd = 'exit'
subprocess.run(ssh_cmd, shell=True, input=f"{ssh_pass}\n", text=True)