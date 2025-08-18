# InsAct-mockup

Fast full-stack mockup of **Problem → Pathway → Solution** narrative platform.

---

## 📂 Structure
- `backend/` → FastAPI backend serving pre-seeded JSON stories.
- `frontend/` → React frontend displaying story cards and details.
- `data.json` → Seeded sample data to simulate real scraping + analysis.

---

## 🚀 Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # (on Windows: venv\Scripts\activate)
pip install -r requirements.txt
uvicorn main:app --reload
