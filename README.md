# aiogram_bot_template 

## 🚀 Overview

`aiogram_bot_template ` is a robust and modern template for quickly building Telegram bots using the **Aiogram**
framework (v3). This template is designed to be:

- ⚡ **Fast**: Includes pre-configured settings for rapid development.
- 🔒 **Secure**: Adopts best practices for handling sensitive data and user interactions.
- 🌐 **Scalable**: Built with modularity to easily expand features.

---

## 🔗 Features

- **Modern Structure**: Clean project organization following best practices.
- **Environment Variables**: Configuration using `.env` for sensitive data.
- **Middleware Support**: Includes custom middleware setup for easy customization.
- **Inline and Command Handlers**: Pre-configured examples of both types of handlers.
- **Error Handling**: Centralized error management for better debugging.
- **Logging**: Configured logging for monitoring and debugging.

---

## 🔄 Quick Start

### Prerequisites

Ensure you have the following installed on your machine:

- **Python 3.10+**
- **pip**

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/createuz/aiogram_bot_template.git
   cd aiogram_bot_template
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
   Update `.env` with your bot token and other configuration values.

5. Run the bot:
   ```bash
   python app.py
   ```

---

## 🌐 Project Structure

```plaintext
📁 AiogramBotTemplate/
├─📁 alembic/
│ ├─📄 env.py
│ ├─📄 README
│ ├─📄 script.py.mako
│ └─📁 versions/
│   └─📄 2024_12_12_2119-1311dcb39dec_first_commit.py
├─📄 alembic.ini
├─📄 app.py
├─📁 core/
│ ├─📄 chunks.py
│ ├─📄 config.py
│ ├─📄 filters.py
│ ├─📄 logging.py
│ ├─📄 middleware.py
│ ├─📄 states.py
│ └─📄 __init__.py
├─📁 db/
│ ├─📄 admins.py
│ ├─📄 database.py
│ ├─📄 statistics.py
│ ├─📄 users.py
│ └─📄 __init__.py
├─📁 handlers/
│ ├─📁 users/
│ │ ├─📄 start.py
│ │ └─📄 __init__.py
│ └─📄 __init__.py
├─📁 keyboards/
│ ├─📄 callbacks.py
│ └─📄 __init__.py
├─📄 README.md
├─📄 test.py
├─📁 utils/
│ ├─📄 aiogram_services.py
│ ├─📄 sessions.py
│ ├─📄 updates.py
│ └─📄 __init__.py
└─📁 venv/
```

---

## 🔍 Key Files and Directories

### `app.py`

The entry point for the bot where the dispatcher and executor are initialized.

### `.env`

Stores sensitive configuration like the bot token. Example:

```plaintext
BOT_TOKEN=your_bot_token_here
```

---

## 🚧 Environment Variables

Ensure you set the following variables in your `.env` file:

| Variable    | Description                   |
|-------------|-------------------------------|
| `BOT_TOKEN` | Your Telegram Bot API token   |
| `LOG_LEVEL` | Logging level (default: INFO) |

---

## 🔧 Available Commands

### Pre-configured Commands

| Command  | Description                                 |
|----------|---------------------------------------------|
| `/start` | Starts the bot and shows a welcome message. |
| `/help`  | Displays the help menu.                     |

---

## 🔧 Customization

### Adding New Handlers

1. Create a new file in the `handlers/` directory.
2. Define your handler function:
   ```python
   from aiogram import Router
   from aiogram.types import Message
   from aiogram.filters import CommandStart

   router = Router()

   @router.message(CommandStart())
   async def new_handler(message: Message):
       await message.answer("This is a new handler!")
   ```
3. Register the router in `app.py` or an appropriate location.

---

## 🔧 Troubleshooting

- **Issue**: Bot does not respond to commands.
    - **Solution**: Ensure your bot token is valid and the bot is added to a chat.

- **Issue**: Module not found.
    - **Solution**: Verify that your virtual environment is activated and dependencies are installed.

---

## 🌟 Contributing

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add new feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

---

## 📢 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **Aiogram Documentation**: [https://docs.aiogram.dev/](https://docs.aiogram.dev/)
- **Telegram Bot API**: [https://core.telegram.org/bots/api](https://core.telegram.org/bots/api)

---

## 🙌 Acknowledgements

Thanks to the Aiogram community and contributors for creating a fantastic framework for Telegram bot development.

