# TG-save-local

# Telegram File Downloader Bot

This is a simple Telegram bot written in Python using the Pyrogram library. The bot allows you to download files from Telegram and save them to your local machine. It can be useful for quickly saving files sent to you in Telegram chats.

## Environment Setup

Before running the Telegram File Downloader Bot, you need to set up your environment variables. Make sure you have the following information ready:

- `API_ID`: Your Telegram API ID. You can obtain it by creating a new application on the [Telegram website](https://my.telegram.org/apps).
- `API_HASH`: Your Telegram API hash. This is also provided when you create a new application on the Telegram website.
- `SESSION_STRING`: The Pyrogram session string. You can generate it by running the `python3 session_generate.py`.
- `BOT_TOKEN`: The Telegram Bot token. You can create a new bot and obtain the token by talking to the [BotFather](https://core.telegram.org/bots#botfather).
- `OWNER_ID`: Telegram User ID that allowed to use the bot. All User ID more than one seperate by space, example `123 456 789`

Once you have the required information, create a `.env` file in the project directory and populate it with the environment variables:

```
API_ID="<your_api_id>"
API_HASH="<your_api_hash>"
SESSION_STRING="<your_session_string>"
BOT_TOKEN="<your_bot_token>"
OWNER_ID="<user_id_allowed>"
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/jusidama18/TG-save-local.git
   ```

2. Change to the project directory:

   ```bash
   cd TG-save-local
   ```

3. Create a virtual environment (optional but recommended):

   ```bash
   python3 -m venv env
   source env/bin/activate  # for Linux/Mac
   env\Scripts\activate  # for Windows
   ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Deployment Steps with Docker

1. Make sure you have Docker installed on your system.

2. Build and start the bot using Docker Compose:

   ```bash
   docker-compose up -d
   ```

   This command will build the Docker image and start the bot in detached mode.

   If you make any changes to the code, you can rebuild the image with the `--build` flag:

   ```bash
   docker-compose up -d --build
   ```

3. The bot will now be running inside the Docker container.

    You can also deploy the bot to a cloud platform like AWS, Google Cloud, or Heroku by adapting the Dockerfile and deployment configuration to the platform's specifications.

    Please note that when deploying the bot to a public environment, make sure to secure sensitive information like API credentials and session strings. Consider using environment variables or a secure secret management system.

## Usage

Run the bot using the following command:

```bash
python -m src
```

The bot will start running, and you can now use it to download files. Add the bot to a Telegram group or start a chat with it, and send a file to the bot. The bot will save the file to the local directory.

You can also deploy the bot to a server or cloud platform for continuous operation.

## Contributing

If you want to contribute to this project, you can fork the repository, make your changes, and submit a pull request. Any contributions are welcome!

## License

This project is licensed under the [GPL-3.0 license](LICENSE).

## Disclaimer

This project is intended for educational purposes only. The authors are not responsible for any misuse of the code or any actions taken with the downloaded files. Be aware of the legal implications and respect the rights of others when downloading files.