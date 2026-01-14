# VSCode Agent RAG - PDF RAG Copilot Skill

A GitHub Copilot Agent Skill for using Retrieval-Augmented Generation (RAG) to increase accuracy of AI responses based on information from manuals, datasheets, etc.  
Uses a locally stored vector store based on hashlib to store the embeddings, and provides a cli tool for generating embeddings from PDF files using Ollama.

## Installation

### 1. Prerequisites
Install [Ollama](https://ollama.com/).  
Install Python dependencies
```bash
pip install requests PyPDF2
```
Install Ollama model (default is mxbai-embed-large)
```bash
ollama pull mxbai-embed-large
```


### 2. Add as Submodule to Your Repo

```bash
cd your-repo

git submodule add https://github.com/yourusername/vscode-agent-rag .github/skills/pdf-rag-knowledge
git submodule update --init --recursive
```


### 3. Enable in VS Code Insiders

Add to your repo's `.vscode/settings.json` (or set it globally):
```json
{
  "chat.useAgentSkills": true
}
```

## Usage

### 4. Adding PDFs
```bash
cd .github/skills/pdf-rag-knowledge
python3 rag_search.py --index /path/to/your/datasheets/*.pdf
```

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

### With GitHub Copilot

Just ask natural questions in Copilot Chat. The skill activates automatically when you ask about:
- Hardware specifications
- Pin configurations
- Register details
- Timing diagrams
- Power requirements
- Communication protocols
- Any technical info from datasheets

## 🔍 How It Works

1. **Indexing**: PDFs chunked into 2000-char segments with 400-char overlap
2. **Embeddings**: Generated via Ollama (local, free, private)
3. **Search**: Semantic similarity using cosine distance
4. **Integration**: Auto-loads when Copilot detects relevant questions

## Configuration

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

See [SKILL.md](SKILL.md) for detailed documentation.
