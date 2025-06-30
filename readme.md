# Annoy-o-Matic 🤖

A simple Discord bot that delivers custom, repetitive replies to specified users for lighthearted, disruptive fun.

## ✨ Features

* **Customizable Replies:** Configured through environment variables for personalized responses.
* **Targeted Annoyance:** Responds specifically to predefined user IDs.

## 🚀 Getting Started

Follow these steps to get your bot running.

### Prerequisites

* Python 3.8+
* Git
* A Discord Bot Application (from [Discord Developer Portal](https://discord.com/developers/applications) - remember to enable **MESSAGE CONTENT INTENT** in your bot's settings).

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/tahatariq19/Annoy-o-Matic.git
    cd Annoy-o-Matic
    ```

2.  **Set Up Virtual Environment:**
    ```bash
    python -m venv .venv
    # On Windows:
    .venv\Scripts\activate
    # On macOS/Linux:
    source .venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1.  **Create `.env` file:**
    Copy the example environment file:
    ```bash
    cp .env.example .env
    ```

2.  **Edit `.env`:**
    Open `.env` and fill in your values.

    ```
    # .env file
    DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
    USER_ID_1=YOUR_DISCORD_USER_ID_1
    USER_ID_2=YOUR_DISCORD_USER_ID_2
    USER_ID_3=YOUR_DISCORD_USER_ID_3
    USER_ID_4=YOUR_DISCORD_USER_ID_4
    ```
    *(Replace `YOUR_DISCORD_BOT_TOKEN` with your bot's token and `YOUR_DISCORD_USER_ID_X` with actual Discord numeric user IDs.)*

    **Note:** You can adjust the number of `USER_ID_X` variables (e.g., `USER_ID_5`, `USER_ID_6`, etc.) in your `.env` file to match your desired number of targets.

3.  **Customize Reply Messages:**
    Remember to modify the corresponding reply messages (what the bot says) for each `USER_ID` directly within the `main.py` file to suit your preferences.

### Running the Bot

```bash
# Ensure your virtual environment is activated
python main.py
