# SerenitySpace 🧘‍♀️

SerenitySpace is a mental wellness web platform focused on reducing stress and depression through AI-driven support, curated motivational content, and a supportive community.

---

## 🚀 Features

- **AI Chatbot Assistant (“Esmo”)** — Provides emotional and mental wellness support via natural conversation using NLP.
- **Curated Inspirational Content** — Daily quotes, Reels, and TED Talk videos to uplift your mood.
- **Community Hub** — Join the Discord server to connect with like-minded individuals.
- **Help & Contact** — Reach out to the team for support or collaboration inquiries.

---

## 📁 Project Structure
SerenitySpace/
├── frontend/ # React/Vite client UI
├── backend/ # Express.js / FastAPI / other API service
├── public/ # Static assets, images, resume, etc.
├── README.md # Project overview (this file)
├── LICENSE # MIT License
├── .github/ # Community files (ISSUE_TEMPLATE, CONTRIBUTING.md, CODE_OF_CONDUCT.md)
└── SECURITY.md # Security policy

---

## 🛠 Requirements

Ensure you have the following installed:

- **Node.js** (v14 or higher)
- **npm** or **yarn**
- (Optional) **Docker** and **Docker Compose** if using containerized setup

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/apoorva-18/SerenitySpace.git
cd SerenitySpace
2. Install dependencies
bash
Copy
Edit
# For frontend
cd frontend
npm install

# For backend
cd ../backend
npm install
3. Start in development mode
bash
Copy
Edit
# In one terminal: start backend (port 5000)
cd backend
npm run dev

# In another terminal: start frontend (port 5173)
cd frontend
npm run dev

