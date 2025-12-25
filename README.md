# PDF RAG Agent - Git Submodule Copilot Skill

A GitHub Copilot Agent Skill for searching PDF documentation (datasheets, technical manuals, FPGA specs) using semantic search. Designed to be used as a **git submodule** in any repository.

## 🎯 What This Is

A **self-contained Agent Skill** that enables GitHub Copilot to search your indexed PDF documentation and provide accurate answers with source citations.

**Key Features:**
- ✅ Use as git submodule (no copying needed)
- ✅ Repo-specific knowledge base
- ✅ Local embeddings via Ollama (no API keys)
- ✅ Auto-activates when you ask hardware/datasheet questions

## 🚀 Quick Start

### 1. Add as Submodule to Your Repo

```bash
cd your-repo

# Add this skill as a submodule
git submodule add https://github.com/yourusername/vscode-agent-rag .github/skills/pdf-rag-knowledge

# Initialize the submodule
git submodule update --init --recursive
```

### 2. Prerequisites

```bash
# Install Python dependencies
pip install requests PyPDF2

# Install Ollama and model
ollama pull mxbai-embed-large
```

### 3. Enable in VS Code Insiders

Add to your repo's `.vscode/settings.json`:
```json
{
  "chat.useAgentSkills": true
}
```

### 4. Index Your PDFs

```bash
cd .github/skills/pdf-rag-knowledge
python3 rag_search.py --index /path/to/your/datasheets/*.pdf
```

### 5. Use with Copilot

Open Copilot Chat and ask questions:
- "What are the GPIO specifications in the datasheet?"
- "How do I configure I2C?"
- "What's the power consumption?"

The skill **automatically activates** for hardware/datasheet questions!

## 📁 Repository Structure

This repo contains the skill files:
```
.
├── SKILL.md           # Skill definition for Copilot
├── rag_search.py      # Self-contained search engine
├── search_rag.sh      # Bash helper script
└── README.md          # This file
```

When added as submodule, files go to: `.github/skills/pdf-rag-knowledge/`

Each repo maintains its own `vector_store.json` (gitignored).

## 🔧 Usage

### Direct Search (Command Line)

```bash
cd .github/skills/pdf-rag-knowledge

# Search
./search_rag.sh "GPIO pins"
python3 rag_search.py --search "power consumption"

# Check status
python3 rag_search.py --stats

# Index PDFs
python3 rag_search.py --index /path/to/pdfs/*.pdf

# Clear database
python3 rag_search.py --clear
```

### With GitHub Copilot (Recommended)

Just ask natural questions in Copilot Chat. The skill activates automatically when you ask about:
- Hardware specifications
- Pin configurations
- Register details
- Timing diagrams
- Power requirements
- Communication protocols
- Any technical info from datasheets

## 📦 Using in Multiple Repos

Add this skill to any repository as a submodule:

```bash
cd /path/to/repo-A
git submodule add <this-repo-url> .github/skills/pdf-rag-knowledge
cd .github/skills/pdf-rag-knowledge
python3 rag_search.py --index /path/to/repo-A-pdfs/*.pdf

cd /path/to/repo-B
git submodule add <this-repo-url> .github/skills/pdf-rag-knowledge
cd .github/skills/pdf-rag-knowledge
python3 rag_search.py --index /path/to/repo-B-pdfs/*.pdf
```

Each repo gets its own `vector_store.json` with repo-specific documentation!

## 🔍 How It Works

1. **Indexing**: PDFs chunked into 2000-char segments with 400-char overlap
2. **Embeddings**: Generated via Ollama (local, free, private)
3. **Search**: Semantic similarity using cosine distance
4. **Integration**: Auto-loads when Copilot detects relevant questions

## 🔄 Updating the Skill

In repos using this as a submodule:

```bash
cd .github/skills/pdf-rag-knowledge
git pull origin main
```

## ⚙️ Configuration

Optional environment variables:
```bash
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=mxbai-embed-large
export CHUNK_SIZE=2000
export CHUNK_OVERLAP=400
```

## 🐛 Troubleshooting

```bash
# Check status
python3 rag_search.py --stats

# Test search
./search_rag.sh "test query"

# Verify Ollama
curl http://localhost:11434/api/tags
```

## 📚 Documentation

See [SKILL.md](SKILL.md) for detailed documentation.

## 📄 License

MIT License
