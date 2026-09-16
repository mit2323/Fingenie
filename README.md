[![CI](https://github.com/mit2323/Fingenie/actions/workflows/ci.yml/badge.svg)](https://github.com/mit2323/Fingenie/actions/workflows/ci.yml)
# FinGenie — AI-Powered Personal Finance \& Investment Copilot

FinGenie is a full-stack AI-powered personal finance and investment copilot for portfolio management, market-data analysis, portfolio analytics, risk analysis, and financial knowledge retrieval.

## Features

* User authentication with JWT
* Portfolio and holdings management
* Real-time market data using yFinance
* Portfolio value and profit/loss analysis
* Sector allocation and diversification analysis
* Portfolio risk analysis
* Conversational AI financial copilot
* Context-aware conversation history
* LangGraph-based AI workflow
* Tool-based query routing
* RAG-based financial knowledge retrieval
* PDF document ingestion
* Sentence Transformer embeddings
* ChromaDB vector search
* CrossEncoder reranking
* Source-cited RAG responses

## Architecture

React Frontend
      |
      v
   FastAPI
      |
      +-------------------+
      |                   |
      v                   v
 PostgreSQL          LangGraph
                          |
             +------------+------------+
             |            |            |
             v            v            v
        Portfolio      Market        RAG
          Tools         Tools        Tool
                                      |
                                      v
                                  ChromaDB
                                      |
                                      v
                                CrossEncoder
                                      |
                                      v
                                    Gemini

## AI Workflow

User Question
     |
     v
LangGraph Agent
     |
     v
Select appropriate tool
     |
     +--> Portfolio Analytics
     |
     +--> Market Data
     |
     +--> Risk Analysis
     |
     +--> Financial Knowledge / RAG
     |
     v
Verified Backend Result
     |
     v
Gemini Response Generation
     |
     v
Final Answer


## RAG Pipeline

PDF
 |
 v
Text Extraction
 |
 v
Chunking
 |
 v
Sentence Transformer Embeddings
 |
 v
ChromaDB Vector Search
 |
 v
Candidate Chunks
 |
 v
CrossEncoder Reranking
 |
 v
Relevant Context
 |
 v
Gemini
 |
 v
Grounded Answer + Sources


### Backend

* Python
* FastAPI
* Uvicorn
* SQLAlchemy
* PostgreSQL
* Alembic

### AI / ML

* Google Gemini API
* LangGraph
* Retrieval-Augmented Generation (RAG)
* Sentence Transformers
* CrossEncoder
* ChromaDB

### Market Data

* yFinance

### Frontend

* React
* Vite
* TypeScript
* Tailwind CSS
* Recharts
* Axios

### Security

* JWT authentication
* User-scoped resource access
* Environment-based secrets

## Backend Structure

backend/
├── app/
│   ├── api/
│   │   └── v1/
│   ├── ai/
│   │   ├── graph/
│   │   ├── rag/
│   │   └── tools/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   ├── core/
│   └── database/
├── alembic/
├── data/
│   └── chroma/
├── tests/
├── requirements.txt
└── README.md

## Database

PostgreSQL stores structured application data:

User
 |
 +--> Portfolio
 |       |
 |       +--> Holdings
 |
 +--> Conversations
         |
         +--> Messages

SQLAlchemy is used for database access and Alembic manages schema migrations.

## Setup

1 Clone the repository

bash
git clone <YOUR\_GITHUB\_REPOSITORY\_URL>
cd Fingenie


2 Create and activate virtual environment

Windows:

```powershell
python -m venv venv
venv\\Scripts\\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

3 Install dependencies

```bash
pip install -r requirements.txt
```

4 Configure environment variables

Create a `.env` file in the backend directory:

env
DATABASE\_URL=your\_postgresql\_connection\_string
GEMINI\_API\_KEY=your\_gemini\_api\_key
GEMINI\_MODEL=your\_supported\_gemini\_model
JWT\_SECRET=your\_jwt\_secret


Never commit `.env` or API keys to GitHub.

5 Run database migrations

```bash
alembic upgrade head
```

6 Start the backend

bash
uvicorn app.main:app --reload

API:
text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Frontend

From the frontend directory:

```bash
npm install
npm run dev
```

Configure the backend URL:

```env
VITE\_API\_URL=http://127.0.0.1:8000/api/v1
```

## API Modules

The backend provides APIs for:

```text
/api/v1/auth
/api/v1/portfolios
/api/v1/holdings
/api/v1/stocks
/api/v1/market
/api/v1/analytics
/api/v1/portfolio-summary
/api/v1/chat
/api/v1/conversations
/api/v1/knowledge
```

## Example AI Query

```json
{
  "message": "How diversified is my portfolio?",
  "portfolio\_id": 3
}
```

The AI agent determines the appropriate backend capability and returns a response using verified application data.

For financial knowledge questions, the RAG pipeline can return document sources such as:

```json
{
  "message": "The fee is ₹50,000.",
  "intent": "search\_financial\_knowledge",
  "sources": \[
    {
      "source": "sebi\_investor\_guidelines.pdf",
      "chunk\_index": 4
    }
  ]
}
```

## Testing RAG Retrieval

The retrieval pipeline can be tested with:

```bash
python test\_retrieval.py
```

Example questions:

```text
What is the fee for applying for informal guidance?
How long can the Department take to dispose of an application?
Who can apply for informal guidance?
What are the two forms of informal guidance?
How long can confidential treatment be requested?
```

## Security

FinGenie uses:

* JWT authentication for protected APIs
* User-scoped portfolio access
* Conversation ownership validation
* Environment variables for secrets
* Backend validation of portfolio access
* Controlled error responses

The AI model is not trusted to decide which user's portfolio can be accessed. Authenticated user context is enforced by the backend.

## Project Workflow

```text
Login
  |
  v
Create Portfolio
  |
  v
Add Holdings
  |
  v
Market Data
  |
  v
Portfolio Analytics
  |
  v
Risk Analysis
  |
  v
AI Copilot
  |
  +--> Portfolio Questions
  |
  +--> Market Questions
  |
  +--> Risk Questions
  |
  +--> Financial Knowledge Questions
           |
           v
          RAG
```

## Future Improvements

* Streaming AI responses
* Additional financial data providers
* More advanced portfolio risk metrics
* Historical portfolio performance
* Improved document management
* Automated testing and CI/CD
* Production cloud deployment
* Production-grade vector storage

## Disclaimer

FinGenie is an educational and decision-support application and is not a substitute for professional financial advice.

Market information may depend on third-party data providers. Users should independently verify important financial information before making investment decisions.


