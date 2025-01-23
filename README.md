# StreamCatcher bot
## Telegram bot to record your livestreams remotely using yt-dlp

This Telegram bot allows you to authenticate, record streams using `yt-dlp`, and check the status of your recordings. Below is a guide on how to use the bot.

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Available Commands](#available-commands)
4. [Stream Recording](#stream-recording)
5. [Check Status](#check-status)
6. [Security](#security)

---

## Getting Started

1. **Set Up the Bot**  
   Ensure that the bot has been properly set up with the necessary files:
   - `auth.json` (contains the bot’s token)
   - `links.json` (contains the links to streams)
   - `password.txt` (stores a password for user authentication)
   - `whitelist.json` (contains the list of authorized users)
   
2. **Start the Bot**  
   After setting up the bot, run it by executing the script. The bot will connect to Telegram and be ready to handle commands.

---

## Authentication

Before using any commands, you need to authenticate yourself.

1. **Whitelisted Users**  
   Only users listed in `whitelist.json` are allowed to interact with the bot. If you're not whitelisted, the bot will notify you that you're not authorized.

2. **Password Authentication**  
   After starting the bot, it will ask for the password (set in `password.txt`). Enter the correct password to authenticate. If the password is incorrect, you will be prompted to try again.

---

## Available Commands

1. **/start**  
   Displays a welcome message and prompts the user to authenticate.

2. **/record**  
   Once authenticated, this command allows the user to select a stream to record. It will show a list of available links (from `links.json`) as buttons.

3. **/status**  
   Shows the status of any active recordings. If no recordings are active, the bot will inform you that there are no ongoing recordings.

---

## Stream Recording

1. **Selecting a Stream to Record**  
   When you send the `/record` command, the bot will provide a list of available streams. Select a stream by clicking one of the buttons.

2. **Recording Process**  
   After selecting a stream, the bot will use `yt-dlp` to start the recording. The file will be saved with the format: `stream_name-timestamp.ext`.

3. **Stopping the Recording**  
   Once a recording is complete, it will be automatically removed from the active recording list.

---

## Check Status

Use the `/status` command to check the status of your ongoing recordings.

- If a recording is still in progress, it will show as "Recording in progress."
- If a recording has been completed, it will show as "Recording completed."

---

## Security

1. **Password Protection**  
   The bot requires a password to authenticate users. This password is hashed and stored securely in `password.txt`. Always ensure this file is kept secure.

2. **Whitelisted Users**  
   Only users in the `whitelist.json` file are allowed to access the bot's features. This file must be updated by an administrator if new users need access.

---

## Troubleshooting

- **"I am not whitelisted!"**  
  If you are not listed in `whitelist.json`, you will not be able to use the bot. Please contact the administrator to be added.

- **"Incorrect Password"**  
  If you forget the password, you'll need the administrator to reset it in `password.txt`.

---

## License

This bot is open-source and can be freely modified. Please ensure you have permission to use it in accordance with any relevant laws.

---