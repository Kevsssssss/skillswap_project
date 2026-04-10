# SkillSwap 🔄

SkillSwap is a karma-based service marketplace where users can trade skills, post bounties, and collaborate. Instead of traditional currency, transactions are handled through a virtual **Karma** system with a built-in escrow mechanism to ensure fair exchanges.

---

## ✨ Key Features

- **Karma Escrow System** — When a task is claimed, the Karma reward is locked in escrow until both the client and the worker approve the completed work.
- **Real-Time Chat** — Live messaging and file sharing within transaction rooms, powered by WebSockets and Redis.
- **Live Notifications** — Smart notification system that aggregates message counts and delivers real-time toasts with sound alerts.
- **Dynamic Trading Floor** — A live dashboard of active bounties that updates without requiring a page refresh.
- **Review & Rating Engine** — Post-transaction feedback system that calculates average user ratings.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django, Python 3 |
| Real-Time | Django Channels, Daphne (ASGI), WebSockets |
| Cache / Message Broker | Redis (via Docker) |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5.3 |
| Database | SQLite (Development) |

---

## 🚀 Getting Started

### Prerequisites

- [Python](https://www.python.org/downloads/) 3.10 or higher
- [Git](https://git-scm.com/downloads)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — required to run the Redis server for WebSockets

### Installation

1. **Clone the repository**

    ```bash
    git clone https://github.com/YOUR-USERNAME/skillswap-marketplace.git
    cd skillswap-marketplace
    ```

2. **Create and activate a virtual environment**

    ```bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate

    # macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

    > If you don't have a `requirements.txt` yet, run `pip install django channels channels-redis daphne` then generate one with `pip freeze > requirements.txt`.

4. **Start the Redis server via Docker**

    Django Channels requires Redis to handle real-time WebSocket messaging. Make sure Docker Desktop is running, then execute:

    ```bash
    docker run -p 6379:6379 -d redis:7
    ```

    > The `-d` flag runs Redis in the background. It will stay active until you stop it in Docker Desktop.

5. **Apply database migrations**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6. **Create a superuser** *(optional but recommended)*

    ```bash
    python manage.py createsuperuser
    ```

7. **Run the development server**

    ```bash
    python manage.py runserver 0.0.0.0:8000
    ```

8. **Open the app**

    Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## 💡 Usage Notes

- **Testing real-time features** — Open two different browsers (e.g. Chrome + Firefox) or use an Incognito window to log in as two different users simultaneously and test chat and notifications end-to-end.
- **Audio notifications** — Browsers require a user interaction before playing audio. Click anywhere on the page at least once after loading for notification chimes to activate.
- **Admin panel** — Access Django's admin at [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) to inspect users, transactions, and notifications directly.
- **Redis must be running** — If WebSockets or notifications aren't working, check that your Docker Redis container is active before starting the Django server.

---

## 📁 Project Structure

```
skillswap_project/
├── marketplace/          # Core app — models, views, signals, consumers
│   ├── models.py         # Service, Transaction, Notification, Message, etc.
│   ├── views.py          # All request handlers
│   ├── signals.py        # WebSocket broadcast triggers
│   ├── consumers.py      # Django Channels WebSocket consumers
│   └── urls.py           # App-level URL routes
├── accounts/             # Auth — registration, login, profile
├── templates/            # All HTML templates
├── static/               # CSS, JS, audio assets
├── manage.py
└── requirements.txt
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to open a pull request or file an issue.

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).