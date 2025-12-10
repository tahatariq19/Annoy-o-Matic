# Annoy-o-Matic 🤖 (Async Edition ⚡)

A Discord bot that playfully annoys selected users with custom messages and emoji reactions.

**Now upgraded with Asynchronous I/O and Docker support!**

## ✨ Features

- **⚡ Async Database:** rewritten using `aiosqlite` to prevent blocking the event loop.
- **📝 Proper Logging:** Replaced `print` statements with the standard `logging` module.
- **🐳 Dockerized:** Ready to deploy with a single container command.
- **Custom Annoyance:** Reply or react to users with random or specific messages/emojis.
- **Slash Commands:** Fully supported configuration via Discord UI.

## 🚀 Quick Start

### Option A: Docker (Recommended)

1.  **Clone & Configure:**
    ```bash
    git clone <your-repo-url>
    cd Annoy-o-Matic
    # Create .env file with DISCORD_TOKEN
    ```

2.  **Run:**
    ```bash
    docker build -t annoy-o-matic .
    docker run -d --env-file .env --name annoy-bot -v $(pwd)/data:/app annoy-o-matic
    ```

### Option B: Local Python

1.  **Install:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run:**
    ```bash
    python main.py
    ```

## 🛠 Technical Upgrades (v2.0)

- **Performance:** Database operations are now non-blocking. The bot won't freeze while reading/writing settings.
- **Stability:** Added error handling and logging for easier debugging.
- **Clean Code:** Refactored for better maintainability.

---

Enjoy annoying your friends (efficiently)!
