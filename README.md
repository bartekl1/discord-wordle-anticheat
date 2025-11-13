# 🤖 Discord Wordle Anti-cheat Bot

Anti-cheat bot for Wordle activity in Discord.

## ℹ️ About

This bot monitors messages sent in Discord channels and deletes messages that contain Wordle answers.

Currently, bot is still under development. 
Planned features are:
- logging deleted messages (to review false positives)
- automatic punishment for completing Wordle in first attempt (e.g., temporary timeout)
- statistics for server admins (e.g., number of deleted messages, users with most deleted messages)
- Docker support for easier deployment

There is no public instance of this bot. If you want to use it, you need to host it yourself.

## 🚀 Getting Started

### Creating Discord Application and Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click on `New Application` and give it a name.
3. (Optional) Add a description and an icon for your application.
4. Navigate to the `Bot` tab on the left sidebar. Bot should be created automatically, if not, click `Add Bot` button.
5. Under `Token` section click `Reset Token` and copy the token. You will need it later. Do **not** share this token with anyone.
6. Under `Privileged Gateway Intents` section, enable `Message Content Intent`.
7. Make sure `Requires OAuth2 Code Grant` under `Authorization Flow` section is **disabled**.
8. Save changes.

### Making bot installable

#### Public bot (anyone can add it to their server)

1. Navigate to the `Bot` tab on the left sidebar.
2. Under `Authorization Flow` section, enable `Public Bot`. It should be enabled by default.
3. Navigate to the `Installation` tab on the left sidebar.
4. Under `Installation Contexts` section, enable `Guild Install` and disable `User Install`.
5. Under `Install Link` section, select `Discord Provided Link`.
6. Under `Default Install Settings` section, enable `applications.commands` and `bot` scopes. Under `Permissions` enable `View Channels`, `Send Messages`, and `Manage Messages`.
7. Save changes.

#### Private bot (only you can add it to your server)

1. Navigate to the `Installation` tab on the left sidebar.
2. Under `Install Link` section, select `None`.
3. Navigate to the `Bot` tab on the left sidebar.
4. Under `Authorization Flow` section, disable `Public Bot`.
5. Save changes.

### Inviting bot to your server

1. Open the following URL in your browser:
- for public bot: `https://discord.com/oauth2/authorize?client_id=<APP_ID>`
- for private bot: `https://discord.com/oauth2/authorize?client_id=<APP_ID>&permissions=11264&integration_type=0&scope=applications.commands+bot`

> [!NOTE]  
> Replace `<APP_ID>` with your application ID. You can find it under `OAuth2` tab in the left sidebar.

> [!NOTE]
> URL for private bot also works for public bot, so you can use it for both types of bots. The advantage of public bot URL is that it shorter and automatically adjusts permissions based on your settings in `Installation` tab.

> [!NOTE]
> URL for public bots gives bot permissions you selected under `Installation` tab. URL for private bots gives bot `View Channels`, `Send Messages`, and `Manage Messages` permissions.

> [!NOTE]
> If you want to add bot with different permissions, you can use URL generator available under the `OAuth2` tab in the left sidebar.

2. Select the server you want to add the bot to, review the permissions, and click `Authorize`.

> [!NOTE]
> You need to be an administrator of the server to add bot to it.

### Running the bot

1. Make sure you have [Python](https://www.python.org/downloads/) installed.

2. Clone this repository or download the source code.
```bash
git clone https://github.com/bartekl1/discord-wordle-anticheat.git
cd discord-wordle-anticheat
```
3. Create and activate a virtual environment (optional but recommended).
```bash
# On Linux
python3 -m venv venv
. ./venv/bin/activate
# On Windows (cmd)
py -m venv venv
.\venv\Scripts\activate.bat
# On Windows (PowerShell)
py -m venv venv
.\venv\Scripts\Activate.ps1
```
4. Install PIP dependencies.
```bash
pip install -r requirements.txt
```
5. Create `config.yaml` configuration file with the following content:
```yaml
bot_token: <BOT_TOKEN>
database_url: sqlite+aiosqlite:///./wordle_anticheat.db
```
Replace `<BOT_TOKEN>` with your bot token you copied earlier. You can change `database_url` to use a different database if needed.

6. Run the bot.
```bash
# On UNIX
python3 bot.py
# On Windows
py bot.py
```

### Hosting the bot (UNIX)

1. Follow the steps in the "Running the bot" section to set up the bot. If everything works correctly, proceed to the next step.

2. Create a systemd service file `/etc/systemd/system/discord-wordle-anticheat.service` with the following content:
```ini
[Unit]
Description=Discord Wordle Anti-Cheat Bot
After=network.target

[Service]
Type=simple
User=<USERNAME>
WorkingDirectory=<PATH>
ExecStart=<PATH>/venv/bin/python <PATH>/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```
Replace `<USERNAME>` with the user you want to run the bot as and `<PATH>` with the path to the bot directory.

3. Reload systemd, enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable discord-wordle-anticheat
sudo systemctl start discord-wordle-anticheat
```

## ⚙️ Bot usage

Use `/enable` command to enable or `/disable` command to disable anti-cheat in the server. Only users with `Administrator` permission can use these commands.

Use `/status` command to check if anti-cheat is currently enabled in the server.

If anti-cheat is enabled, the bot will automatically delete messages containing Wordle answers and send a message notifying the user about the deletion.

## 📜 License

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE).
