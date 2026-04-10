# SkillSwap

SkillSwap is a karma-based service marketplace where users can trade skills, post bounties, and collaborate. Instead of traditional currency, transactions are handled through a virtual "Karma" system with a built-in escrow mechanism to ensure fair exchanges. 

## ✨ Key Features

* **Karma Escrow System:** When a task is claimed, the Karma reward is locked in escrow until both the client and the worker approve the completed task.
* **Real-Time Encrypted Chat:** Secure, live messaging and file sharing within specific transaction rooms, powered by WebSockets.
* **Live Rollup Notifications:** "Facebook-style" smart notification system that prioritizes major events (like task claims) and aggregates message counts to prevent spam.
* **Dynamic Trading Floor:** A live dashboard of active bounties that updates without requiring a page refresh.
* **Review & Rating Engine:** Post-transaction feedback system that calculates average user ratings.

## 🛠️ Tech Stack

* **Backend:** Django, Python 3
* **Real-Time Engine:** Django Channels, Daphne (ASGI), WebSockets
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5.3
* **Database:** SQLite (Development)

---

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing.

### Prerequisites

You will need the following installed on your machine:
* [Python](https://www.python.org/downloads/) (v3.10 or higher recommended)
* [Git](https://git-scm.com/downloads)

### Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/YOUR-USERNAME/skillswap-marketplace.git](https://github.com/YOUR-USERNAME/skillswap-marketplace.git)
   cd skillswap-marketplace