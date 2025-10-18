# 🛍️ Product-Categorization-AI

<p align="left">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green" />
  <img alt="Python" src="https://img.shields.io/badge/python-3.12%2B-blue" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-🔥-teal" />
  <img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-UI-red" />
</p>

Multi‑agent AI system for product categorization, attribute extraction, tag generation, and smart search — integrating LLMs, NLP, IR, and security.

---

## ✨ What’s Inside
- ⚙️ Backend: FastAPI API (`backend/api/main.py`) with agent endpoints and AI search
- 🧠 Agents: Category Classifier, Attribute Extractor, Tag Generator
- 🧩 Core: LLM wrapper, NLP helpers, Security utils (JWT, sanitization, CSRF)
- 🎨 Frontend: Streamlit UI (`frontend/app.py`)
- 🔎 AI Search: TF‑IDF based similar product suggestions

---

## 🚀 Quick Start
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt -r frontend/requirements.txt scikit-learn
python run_app.py
```
- 🧪 Backend: http://127.0.0.1:8000 (OpenAPI docs at `/docs`)
- 🎛️ Frontend: http://localhost:8501

Tip: If scikit‑learn install is slow on macOS/Python 3.13, use Python 3.12 for prebuilt wheels.

---

## 🔐 Optional API Security
Set an API key to protect endpoints:
```bash
export API_KEY="your-secret-key"
```
Send the header on requests:
```
X-API-Key: your-secret-key
```

---

## 🧾 Environment Variables
| Name       | Description                          | Default     |
|------------|--------------------------------------|-------------|
| `API_KEY`  | Optional API key to protect routes   | (unset)     |
| `LLM_MODEL`| LLM model name for Ollama wrapper    | `llama3.1`  |

Create a `.env` at project root if preferred.

---

## 🐳 Docker (optional)
Dockerfile not provided yet; you can still run with uvicorn/streamlit:
```bash
# Backend
cd backend
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Frontend
cd ../frontend
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

---

## 📡 API Endpoints
- ❤️ Health: `GET /api/health`
- 🔍 AI Search: `GET /api/search/suggest?q=red%20dress&top_n=5`
- 🧭 Classifier: `POST /api/classifier/process`
- 🧪 Extractor: `POST /api/extractor/process`
- 🏷️ Tagger: `POST /api/tagger/process`
- 🤖 Orchestrator (full pipeline): `POST /api/orchestrator/process`

### 🔧 Curl Examples
```bash
# Health
curl http://127.0.0.1:8000/api/health

# Search
curl "http://127.0.0.1:8000/api/search/suggest?q=red%20dress&top_n=5"

# Orchestrator (full flow)
curl -X POST http://127.0.0.1:8000/api/orchestrator/process \
  -H "Content-Type: application/json" \
  -d '{"description": "Red cotton summer dress"}'
```
If `API_KEY` is set, add `-H "X-API-Key: your-secret-key"` to requests.

---

## 📂 Data
- Default search corpus: `backend/data/cleaned_product_data.csv`
- Fallback: `backend/data/product.csv`

---

## 🧠 How It Works (High Level)
1. ✍️ Input product description
2. 🧪 NLP preprocessing + (optional) NER/summarization
3. 🧠 LLM (via Ollama wrapper) for classification/attributes/tags
4. 🔎 IR: TF‑IDF similarity for product suggestions
5. 🔐 Security: sanitization, JWT helpers, optional API key

> LLM model configurable via env `LLM_MODEL` (e.g., `llama3.1`).

---

## 🧭 Project Structure
```
backend/
  api/
    main.py        # FastAPI app + AI search
    routes.py      # Agent endpoints
  agents/
    orchestrator_agent.py
    category_classifier_agent.py
    attribute_extractor_agent.py
    tag_generator_agent.py
  core/
    llm_integration.py
    nlp_processor.py
    security.py
frontend/
  app.py           # Streamlit UI
```

---

## ✅ Responsible AI (summary)
- 🧹 Input sanitization; confidence scores on outputs
- 🧾 Transparent schemas & logging hooks (avoid PII)
- ⚙️ Configurable model and thresholds

Read more: `RESPONSIBLE_AI.md`

---

## 💼 Commercialization (summary)
- 🎯 Target: e‑commerce SMEs
- 💰 Pricing tiers: Starter / Pro / Enterprise
- ☁️ Deployment: Dockerized FastAPI + Streamlit; optional managed hosting

Details: `COMMERCIALIZATION.md`

---

## 📊 Evaluation
- 🔎 Search: precision@k, recall@k
- 🏷️ Tag relevance: human ratings
- 🧭 Classification accuracy vs labeled set

Plan & results: `EVALUATION.md`

---

## ❓ FAQ
- Q: It says `ModuleNotFoundError: sklearn`?
  - A: `pip install scikit-learn` (prefer Python 3.12 for speed.)
- Q: 401 Unauthorized?
  - A: Set `API_KEY` and send header `X-API-Key`.
- Q: Slow on Apple Silicon?
  - A: Use Python 3.12 for prebuilt wheels.

---

## 👥 Contributors
- Amaya — [github.com/amaya-6](https://github.com/amaya-6)
- Sadeepa — [github.com/SadeepaMadushani](https://github.com/SadeepaMadushani)
- Shehan — [github.com/ShehanUD](https://github.com/ShehanUD)
- Hirusha — [github.com/itzcheh1ru](https://github.com/itzcheh1ru)

### 📋 Detailed Contributions

| Member   | Branch                   | Agent                        | Core                                 | Utils             | API
|----------|--------------------------|------------------------------|--------------------------------------|-------------------|------------------
| Shehan   | IT23426344-Shehan        | orchestrator_agent.py         | llm_integration.py                   | helpers.py        | main.py
| Amaya    | IT23186156-Amaya         | category_classifier_agent.py  | nlp_processor.py                     | validators.py     | routes.py
| Sadeepa  | IT23186224-Sadeepa       | attribute_extractor_agent.py  | communication.py, information_retrieval.py | config_loader.py | schemas.py
| Hirusha  | IT23426580-Hirusha       | tag_generator_agent.py        | security.py, models/                 | remaining utils   | remaining API files

---

## 📜 License
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🧰 Troubleshooting
- ⏳ Slow install on macOS/ARM? Use Python 3.12
- 🔑 401 from API? Set `API_KEY` and send `X-API-Key`
- 📦 Missing sklearn? `pip install scikit-learn`

Happy hacking! 🚀


