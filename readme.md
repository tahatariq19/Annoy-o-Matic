# Annoy-o-Matic 🤖

A Discord bot that playfully annoys selected users with custom messages and emoji reactions.

## ✨ Features

- **Custom Annoyance:** Reply or react to users with random or specific messages/emojis.
- **Slash Commands:** Add/remove targets, set messages/reactions, configure annoyance methods and modes.
- **Per-user Settings:** Each target can have their own annoyance configuration.
- **Flexible Message Input:** Set specific messages using semicolons or quoted strings (commas allowed inside quotes).
- **Persistent Storage:** All settings are saved in a local SQLite database.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- A Discord Bot Token ([Discord Developer Portal](https://discord.com/developers/applications))
- Enable **MESSAGE CONTENT INTENT** and **SERVER MEMBERS INTENT** for your bot

### Installation

1. **Clone & Setup:**

    ```bash
    git clone <your-repo-url>
    cd annoybot
    python -m venv .venv
    # Activate venv:
    # Windows:
    .venv\Scripts\activate
    # macOS/Linux:
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2. **Configure:**
    - Create a `.env` file with your `DISCORD_TOKEN` (see `.env.example` if present).

### Running

```bash
python main.py
```

## 🛠 Usage

- Use `/settarget` to add a user to the annoyance list.
- Use `/setannoyancemessage` to set custom messages (semicolon-separated or quoted for messages with commas).
- Use `/setannoyancereaction` to set custom emoji reactions (comma-separated).
- Use `/setannoyancemethods` and `/setmessagemode` to configure how users are annoyed.
- Use `/removetarget` to stop annoying a user.
- Use `/listtargets` to view all annoyance targets and their settings.

## ⚠️ Notes

- The bot stores data in a local SQLite database (`annoy_o_matic.db`).
- Do **not** commit your `.db` or `.env` files to git.
- For production or multi-server use, consider a centralized database and process manager.

---

Enjoy annoying your friends (with consent)!
