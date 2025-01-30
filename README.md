# StreamCatcher bot

### Trigger livestream downloads on the go with a Telegram bot!

---


### How to Use:

1. **Download yt-dlp**:
   - Visit the official [[yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp)](https://github.com/yt-dlp/yt-dlp) page to download the latest **yt-dlp** executable for your platform.

2. **Download FFmpeg**:
   - Download the latest FFmpeg build from the official [[FFmpeg website](https://ffmpeg.org/download.html)](https://ffmpeg.org/download.html). Make sure to get the executable version suitable for your operating system.

3. **Place Executables in the `bin` Directory**:
   - Place both **yt-dlp.exe** and **ffmpeg.exe** into a folder named `bin` on your computer.
   - Also, place a **.bat** file inside the `bin` directory to make it easier to run the program from the command line.

   Your `bin` directory should look like this:
   ```
   bin/
   ├── yt-dlp.exe
   ├── ffmpeg.exe
   └── run_download.bat  (this is the .bat file to run yt-dlp)
   ```

4. **Set Up Telegram Bot**:
   - Create a new bot on Telegram via **BotFather**:
     1. Open Telegram and search for "BotFather."
     2. Start a conversation and use `/newbot` to create a new bot. Follow the prompts to get the **bot token**.
   - Input the **bot token** into the `auth.json` file.
   
5. **Find Your Telegram Chat ID**:
   - Start a conversation with your bot on Telegram and send any message to it.
   - Visit [[this link](https://api.telegram.org/bot%3Cyour-bot-token%3E/getUpdates)](https://api.telegram.org/bot<your-bot-token>/getUpdates) (replacing `<your-bot-token>` with your actual bot token) to retrieve your **chat ID** from the response.
   - Input your **chat ID** into the `auth.json` file.

6. **Set Up Configuration Files**:
   - **auth.json**: This file contains your bot’s **token** and **chat_id**.
   - **links.json**: This file contains the path to the **run_download.bat** file and a list of predetermined URLs you want to download.

   Your `config` directory should look like this:
   ```
   config/
   ├── auth.json         (contains bot token and chat ID)
   └── links.json        (contains file path to run_download.bat and a list of predetermined URLs to download)
   ```

### Running the Program:
1. Once everything is set up, double-click the **main.exe** file from the `root` directory, or run it from the command line.
2. Pick the link from **links.json** to record from within the Telegram chat.
3. The bot will run your custom bat file with the link as argument, i.e. `run_download.bat <link>` on your pc that runs the Telegram bot, and you can check the status of the downloads via your Telegram bot.

### Example of File Contents:
- **auth.json**:
   ```json
   {
     "BOT_TOKEN": "YOUR_BOT_TOKEN_HERE",
     "CHAT_ID": "YOUR_CHAT_ID_HERE",
    "ALLOWED_USERNAMES": ["YOUR_TELEGRAM_USERNAME(S)_HERE"]
   }
   ```

- **links.json**:
   ```json
   "TARGET_SCRIPT_PATH": "./bin/PATH_TO_YOUR_BAT_FILE",
   "LINK_MAP": {
    "livestream A": "YOUR_LIVESTREAM_URL",
    "livestream B": "YOUR_LIVESTREAM_URL",
   }
   ```

### Additional Notes:
- The **.exe** file is the main entry point for running the download process. You can run it manually, or automate it with a scheduled task if preferred.

---

Dev Notes:

IMPORTANT: `pyinstaller main.py --paths "." --noconfirm` to create the executable
