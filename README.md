# 🧠 Oynx AI Brain — Autonomous Local AI Assistant Agent

> **A fully autonomous AI assistant agent running 100% locally with LM Studio**  
> Voice-enabled, memory-equipped, book-aware, security-hardened — your personal AI brain.

---

## 🧠 AI Agent Architecture

```mermaid
graph TB
    subgraph INTERFACE["🎤 Interface Layer"]
        I1[Voice Input\nSpeech Recognition]
        I2[Text Input\nChat Interface]
        I3[Admin Console\nDashboard]
    end

    subgraph BRAIN["🧠 Oynx AI Core Agents"]
        A1[Chatbot Agent\nConversation Engine]
        A2[Memory Agent\nContext Retention]
        A3[Search Agent\nInformation Retrieval]
        A4[Security Agent\nAuthentication & Guard]
    end

    subgraph TOOLS["🔧 Tool Agents"]
        T1[Book Downloader\nAgent]
        T2[Book Analysis\nAgent]
        T3[Google Fetch\nAgent]
        T4[Speech Agent\nTTS/STT]
    end

    subgraph LLM["⚡ Local LLM Engine"]
        L1[LM Studio\nLocal Inference]
        L2[DeepSeek R1\nDistill Qwen 7B]
        L3[Context Window\nManagement]
    end

    subgraph STORAGE["💾 Storage Layer"]
        S1[Memory Store\nConversation History]
        S2[Book Library\nKnowledge Base]
        S3[Search Cache\nQuery Results]
        S4[Security Logs\nAudit Trail]
    end

    I1 --> A1
    I2 --> A1
    I3 --> A4
    A1 --> A2
    A1 --> A3
    A1 --> T1
    A1 --> T2
    A1 --> T3
    A1 --> T4
    A2 --> S1
    A3 --> S3
    T1 --> S2
    T2 --> S2
    T4 --> I1
    A4 --> S4
    A1 --> L1
    L1 --> L2
    L2 --> L3

    style A1 fill:#4CAF50,stroke:#333,color:#fff
    style A2 fill:#2196F3,stroke:#333,color:#fff
    style A3 fill:#FF9800,stroke:#333,color:#fff
    style A4 fill:#f44336,stroke:#333,color:#fff
    style T4 fill:#9C27B0,stroke:#333,color:#fff
```

## 🤖 AI Agent Components

| Agent | Module | Function |
|-------|--------|----------|
| **Chatbot Agent** | `chatbot.py` | Core conversation engine — processes queries, routes to tools, maintains context |
| **Memory Agent** | `memory.py` | Maintains conversation history and user preferences across sessions |
| **Search Agent** | `search.py` | Retrieves information from local knowledge base and cached queries |
| **Security Agent** | `security.py`, `Admin.py` | Admin authentication, access control, audit logging |
| **Book Downloader Agent** | `book_downloader.py` | Downloads and catalogs books for knowledge expansion |
| **Book Analysis Agent** | `book_analysis.py` | Analyzes book content, extracts insights, builds knowledge |
| **Google Fetch Agent** | `fetch_google.py` | Retrieves information via Google Custom Search API |
| **Speech Agent** | `speech.py` | Text-to-Speech and Speech-to-Text for voice interaction |

## 🛠 Tech Stack

| Component | Technology | Agent Role |
|-----------|-----------|------------|
| **LLM Backend** | LM Studio (Local) | Local inference engine |
| **AI Model** | DeepSeek R1 Distill Qwen 7B | Core reasoning agent |
| **Voice** | Google Cloud TTS | Speech synthesis agent |
| **Fuzzy Matching** | RapidFuzz | Intent recognition agent |
| **Security** | Custom auth system | Access control agent |
| **Platform** | Windows 11 + RTX 3060 6GB | Local inference hardware |

## 🔄 Before vs After

```mermaid
graph LR
    subgraph BEFORE["❌ Before"]
        BM[Separate tools\nNo unified assistant\nCloud-dependent AI\nPrivacy concerns]
    end

    subgraph AFTER["✅ After (Oynx AI Agent)"]
        AM[Single AI brain\nVoice + Text interface\n100% local & private\nMemory & knowledge\nTool integration]
    end

    BM -->|Oynx AI Agent| AM
```

## ⚡ Quick Start

```bash
# Start the Oynx AI Assistant
python chatbot.py

# Access admin dashboard
python Admin.py
```

## 📁 Repository Contents

| File | Description |
|------|-------------|
| `chatbot.py` | Core AI conversation agent |
| `Admin.py` | Admin authentication & dashboard |
| `memory.py` | Persistent memory & context agent |
| `search.py` | Knowledge retrieval agent |
| `speech.py` | Voice I/O agent |
| `security.py` | Access control agent |
| `book_downloader.py` | Book acquisition agent |
| `book_analysis.py` | Book insight extraction agent |
| `fetch_google.py` | Web intelligence agent |
| `config.py` | Configuration agent |

---

Built by **[Shazaly Musa](https://github.com/SparkSpheartech)** — Founder, SparkSphear Tech  
*AI Agents for Personal & Enterprise Local AI Assistants*