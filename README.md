# 📊 FinSightAI - Financial Agent API

A modern API for financial analysis with intelligent agents powered by **PydanticAI** and **FastAPI**.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Development](#development)
- [Testing](#testing)

---

## 🎯 Overview

FinSightAI is an API that provides intelligent financial analysis through autonomous agents that combine real-time price data with market sentiment analysis. The platform uses modern technologies such as:

- **FastAPI** for rapid asynchronous API construction
- **PydanticAI** for AI agents with tool access
- **Uvicorn** as a high-performance ASGI server
- **Yahoo Finance API** for price data
- **NewsAPI** for financial news data

---

## ✨ Features

### 🤖 Intelligent Financial Agent
- Real-time price analysis
- Market sentiment evaluation
- Technical analysis with indicators
- Integration with multiple data sources

### 💡 Available Tools
1. **Price Analysis** (`get_price_analysis`)
   - Current and historical prices
   - Price trends and directions
   - Support and resistance levels
   - Moving averages (MA20, MA50)
   - Trading volume

2. **Sentiment Analysis** (`get_news_sentiment`)
   - Recent financial news
   - Fear & Greed Index
   - Extracted key themes
   - Identified risk factors

3. **Comprehensive Analysis** (`get_comprehensive_analysis`)
   - Combination of price and sentiment
   - Synthesized insights
   - Data-driven recommendations

### 📱 Conversation Management
- Creation of conversations with unique IDs
- Persistent message history
- Customizable user context
- Automatic timestamps

### 🔧 Health Endpoints
- General health checks
- Detailed agent status
- Availability monitoring

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│              Controllers (FastAPI Routes)                   │
│  ├─ /api/v1/agents/chat          (POST)                    │
│  ├─ /api/v1/agents/conversations (GET, POST)              │
│  ├─ /api/v1/agents/status        (GET)                    │
│  └─ /health                       (GET)                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                            │
│         AgentService - Logic Orchestration                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  AGENTS & TOOLS LAYER                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │     FinancialManagerAgent (PydanticAI)              │   │
│  │  ┌──────────────┐  ┌──────────────┐                │   │
│  │  │ PriceTool    │  │ NewsTool     │                │   │
│  │  └──────────────┘  └──────────────┘                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  DATA LAYER                                 │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │ ConversationRepo     │  │ External APIs       │        │
│  │ (In-Memory Storage)  │  │ - Yahoo Finance     │        │
│  │                      │  │ - NewsAPI           │        │
│  └──────────────────────┘  └──────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Main Components

| Component | Description |
|-----------|-----------|
| **Controllers** | FastAPI routes layer |
| **Services** | Orchestration and processing logic |
| **Agents** | PydanticAI agents with tool access |
| **Tools** | External API integrations |
| **Repositories** | Data persistence (conversations) |
| **Models** | Pydantic schemas and data structures |
| **Core** | Configuration, dependencies and exceptions |

---

## 📋 Prerequisites

- **Python 3.13+**
- **pip** (package manager)
- **API Keys** (OpenAI, NewsAPI - see [Configuration](#configuration))

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-user/finsightai-api.git
cd finsightai-api
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requeriments
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
# Edit the .env file with your API keys
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
# Application
APP_NAME=Financial Agent API
ENVIRONMENT=development
DEBUG=True

# OpenAI (required to use the agent)
OPENAI_API_KEY=sk-...

# NewsAPI (recommended for complete sentiment analysis)
NEWS_API_KEY=your-news-api-key

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Get API Keys

**OpenAI API:**
1. Visit https://platform.openai.com/api-keys
2. Create a new API key
3. Copy and add to `.env` file

**NewsAPI:**
1. Visit https://newsapi.org/
2. Register for a free account
3. Copy your API key
4. Add to `.env` file

---

## 💻 Usage

### Start the Server

```bash
# Development mode (with auto-reload)
python run.py

# Or directly with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📡 API Endpoints

### 1. Chat with Agent

**POST** `/api/v1/agents/chat`

Send a message for financial analysis.

**Request:**
```json
{
  "message": "Analyze Apple in the last 3 months",
  "agent_type": "financial_manager",
  "conversation_id": "optional-uuid",
  "context": {
    "user_timezone": "America/New_York",
    "investment_type": "long_term"
  }
}
```

**Response:**
```json
{
  "response": "## Apple Analysis...",
  "conversation_id": "uuid-12345",
  "agent_type": "financial_manager",
  "timestamp": "2024-01-21T10:30:00",
  "metadata": {
    "processing_time": 2.5,
    "tool_used": true
  }
}
```

### 2. Create New Conversation

**POST** `/api/v1/agents/conversations`

**Response:**
```json
{
  "conversation_id": "uuid-12345",
  "message": "Conversation created successfully"
}
```

### 3. Get Conversation History

**GET** `/api/v1/agents/conversations/{conversation_id}`

**Response:**
```json
{
  "conversation_id": "uuid-12345",
  "user_id": "anonymous",
  "messages": [
    {
      "role": "user",
      "content": "Analyze Apple",
      "timestamp": "2024-01-21T10:30:00"
    },
    {
      "role": "assistant",
      "content": "Analysis: ...",
      "timestamp": "2024-01-21T10:30:05"
    }
  ],
  "created_at": "2024-01-21T10:30:00",
  "updated_at": "2024-01-21T10:30:05"
}
```

### 4. Agent Status

**GET** `/api/v1/agents/status`

**Response:**
```json
[
  {
    "agent_type": "financial_manager",
    "is_available": true,
    "last_health_check": "2024-01-21T10:35:00",
    "version": "1.0.0"
  }
]
```

### 5. General Health Check

**GET** `/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "financial-agent-api"
}
```

### 6. Agent Health Check

**GET** `/health/agents`

**Response:**
```json
{
  "status": "healthy",
  "agents": {
    "financial_manager": true
  }
}
```

### 7. Application Info

**GET** `/info`

**Response:**
```json
{
  "app_name": "Financial Agent API",
  "environment": "development",
  "debug": true,
  "available_agents": ["financial_manager"]
}
```

---

## 📁 Project Structure

```
finsightai-api/
├── app/                           # Main application code
│   ├── __init__.py
│   ├── main.py                   # FastAPI configuration and lifecycle
│   ├── agents/                   # Agents layer
│   │   ├── base_agent.py         # Base interface
│   │   ├── financial_manager_agent.py  # Financial agent
│   │   ├── factory.py            # Factory pattern for agents
│   │   └── tools/                # Agent tools
│   │       ├── base_tool.py      # Tool base interface
│   │       ├── agent_tool.py     # PydanticAI integration
│   │       ├── price_tool.py     # Price analysis
│   │       ├── news_tool.py      # News analysis
│   │       └── factory.py        # Tool factory
│   ├── controllers/              # Routes and endpoints
│   │   ├── financial_manager_controller.py
│   │   └── health.py
│   ├── services/                 # Business logic
│   │   └── financial_manager_service.py
│   ├── repositories/             # Data access
│   │   └── conversation_repository.py
│   ├── models/                   # Schemas and structures
│   │   ├── financial_manager_model.py
│   │   └── schemas.py
│   └── core/                     # Configuration and utilities
│       ├── config.py             # Environment variables
│       ├── dependencies.py       # Dependency injection
│       └── exceptions.py         # Custom exceptions
├── tests/                        # Automated tests
│   └── __init__.py
├── run.py                        # Entry point
├── requeriments                  # Python dependencies
├── pytest.ini                    # Test configuration
├── .env                          # Environment variables (git ignored)
├── .env.example                  # .env template
├── .gitignore                    # Git ignored files
├── .coveragerc                   # Test coverage configuration
└── README.md                     # This file
```

---

## 🛠️ Development

### Code Patterns

#### 1. Factory Pattern
Used to create agents and tools centrally:
```python
# agents/factory.py
class AgentFactory:
    @staticmethod
    async def create_financial_manager():
        agent = FinancialManagerAgent()
        return await agent.initialize()
```

#### 2. Dependency Injection
Dependencies injected via FastAPI:
```python
# controllers/financial_manager_controller.py
@router.post("/chat")
async def chat_with_agent(
    request: ChatRequest,
    agent_service: AgentService = Depends(get_agent_service)
):
    return await agent_service.process_message(...)
```

#### 3. Async/Await
All I/O is asynchronous for better performance:
```python
async def process_message(self, message: str) -> ChatResponse:
    # Asynchronous operations
    await agent.run(message)
```

### Add a New Tool

1. **Create the tool class:**
```python
# app/agents/tools/custom_tool.py
from app.agents.tools.base_tool import BaseTool

class CustomTool(BaseTool):
    async def execute(self, **kwargs):
        # Implement logic
        pass
    
    def get_schema(self):
        # Return tool schema
        pass
```

2. **Register in the Factory:**
```python
# app/agents/tools/factory.py
def get_custom_tool(self) -> CustomTool:
    if "custom" not in self._tools:
        self._tools["custom"] = CustomTool()
    return self._tools["custom"]
```

3. **Add to the Agent:**
```python
# app/agents/financial_manager_agent.py
self.agent = Agent(
    model='openai:gpt-4',
    tools=[
        self.agent_tools.get_custom_tool,
        # ...other tools
    ]
)
```

---

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### With Code Coverage

```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html
```

### Specific Tests

```bash
# By file
pytest tests/test_agents.py

# By function
pytest tests/test_agents.py::test_agent_initialization

# With verbose mode
pytest -v
```

### Test Configuration

Defined in `pytest.ini`:
- Automatic async mode (`asyncio_mode = auto`)
- Coverage required
- HTML report
- Strict configuration validation

---

## 📊 Data Models

### Main Schemas

**ChatRequest:**
```python
{
  "message": str,              # User question
  "agent_type": "financial_manager",
  "conversation_id": str | None,
  "context": Dict[str, Any]
}
```

**ChatResponse:**
```python
{
  "response": str,             # Agent response
  "conversation_id": str,
  "agent_type": "financial_manager",
  "timestamp": datetime,
  "metadata": Dict[str, Any]
}
```

**FinancialAnalysisResponse:**
```python
{
  "presentation": str,
  "asset_symbol": str,
  "analysis_period": str,
  "price_snapshot": PriceSnapshot,
  "market_sentiment": MarketSentiment,
  "top_news_headlines": List[str],
  "key_insights": List[str],
  "analysis_timestamp": datetime,
  "data_sources": List[str]
}
```

---

## 🐛 Troubleshooting

### Erro: "OPENAI_API_KEY not found"

```bash
# Solução:
# 1. Verifique se o arquivo .env existe
# 2. Adicione OPENAI_API_KEY ao .env
# 3. Reinicie o servidor
```

### Erro: "Connection timeout com Yahoo Finance"

```bash
# Solução:
# - Verifique conexão com internet
# - Verifique se o símbolo do ativo existe (ex: AAPL, BTC-USD)
# - Tente novamente após alguns segundos
```

### Erro: "Agent not available"

```bash
# Solução:
# Verifique logs:
python run.py  # Procure por "Failed to initialize agents"
# Verifique se todas as dependências estão instaladas
```

---

## 📚 Recursos Adicionais

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Yahoo Finance API](https://finance.yahoo.com/)
- [NewsAPI Documentation](https://newsapi.org/docs)

---