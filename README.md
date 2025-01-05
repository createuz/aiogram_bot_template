# Aiogram Bot Template

A robust and scalable template for building Telegram bots using the [Aiogram framework](https://docs.aiogram.dev/). This template is structured for clean code organization, maintainability, and quick deployment.

---

## 📁 Project Structure

```plaintext
AiogramBotTemplate/
├─📁 alembic/             # Database migrations
│ ├─📄 env.py
│ ├─📄 README
│ ├─📄 script.py.mako
│ └─📁 versions/          # Auto-generated migration files
│   └─📄 first_commit.py
├─📄 alembic.ini          # Alembic configuration
├─📄 app.py               # Main entry point of the bot
├─📁 core/                # Core bot components
│ ├─📄 chunks.py          # Chunking large messages or data
│ ├─📄 config.py          # Bot configuration management
│ ├─📄 filters.py         # Custom filters for handlers
│ ├─📄 logging.py         # Logging configuration
│ ├─📄 middleware.py      # Middleware for request handling
│ ├─📄 states.py          # FSM (Finite State Machine) states
│ └─📄 __init__.py
├─📁 db/                  # Database interaction modules
│ ├─📄 admins.py          # Admin-related database operations
│ ├─📄 database.py        # Core database connection setup
│ ├─📄 statistics.py      # Bot statistics tracking
│ ├─📄 users.py           # User-related database operations
│ └─📄 __init__.py
├─📁 handlers/            # Update and command handlers
│ ├─📁 users/             # User-specific handlers
│ │ ├─📄 start.py         # /start command implementation
│ │ └─📄 __init__.py
│ └─📄 __init__.py
├─📁 keyboards/           # Inline and reply keyboards
│ ├─📄 callbacks.py       # Callback data handlers
│ └─📄 __init__.py
├─📄 README.md            # Project documentation
├─📄 test.py              # Testing scripts
├─📁 utils/               # Utility functions
│ ├─📄 aiogram_services.py # Aiogram-specific utilities
│ ├─📄 sessions.py        # Session management
│ ├─📄 updates.py         # Bot update-related utilities
│ └─📄 __init__.py
└─📁 venv/                # Virtual environment (optional, not recommended in production)
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **PostgreSQL**
- **Virtual Environment** (recommended)
- **Aiogram 3.x**

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/AiogramBotTemplate.git
   cd AiogramBotTemplate
   ```

2. Create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment:
   - Create a `.env` file in the root directory.
   - Add the following variables:

     ```env
     BOT_TOKEN=your_telegram_bot_token
     DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
     ```

5. Initialize the database:

   ```bash
   alembic upgrade head
   ```

6. Run the bot:

   ```bash
   python app.py
   ```

---

## 🛠 Features

- **Clean Code Structure:** Organized modules for scalability and maintainability.
- **Database Integration:** Asynchronous PostgreSQL connection using `asyncpg`.
- **State Management:** FSM support for handling complex bot flows.
- **Middleware:** Custom middleware for preprocessing updates.
- **Keyboard Management:** Flexible inline and reply keyboards.
- **Logging:** Comprehensive logging setup for debugging and monitoring.

---

## 📝 Usage

1. **Command Handlers:**
   Add your custom command handlers in `handlers/users/` or `handlers/`.

2. **Database Operations:**
   Use prebuilt modules in the `db/` folder for database queries and CRUD operations.

3. **Custom Keyboards:**
   Define your keyboards in `keyboards/` and link them to handlers.

4. **Configuration:**
   Manage bot settings in `core/config.py` or through environment variables.

---

## 📚 Documentation

- [Aiogram Documentation](https://docs.aiogram.dev/)
- [Asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/en/latest/)

---

## 🤝 Contribution

Contributions are welcome! Please follow these steps:

1. Fork this repository.
2. Create a new branch:

   ```bash
   git checkout -b feature-branch
   ```

3. Commit your changes:

   ```bash
   git commit -m "Add new feature"
   ```

4. Push to the branch:

   ```bash
   git push origin feature-branch
   ```

5. Create a pull request.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🌟 Acknowledgements

- Special thanks to the [Aiogram team](https://docs.aiogram.dev/) for their excellent framework.
- Inspired by clean and scalable bot architectures.

---

_Ready to build your bot? Let’s code!_

