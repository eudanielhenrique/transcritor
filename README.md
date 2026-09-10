# Transcritor AI 🎬

[![Agent Index](https://img.shields.io/badge/Agent%20Index-transcritor--ai-volt?style=for-the-badge&logo=openai&logoColor=black&color=D5EF8A)](https://aiworthusing.com/agent-index/transcritor-ai)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](compose.yml)
[![Plow Network](https://img.shields.io/badge/Plow-Autonomous%20Agent-purple?style=for-the-badge)](https://plow.co)

> **Autonomous multimodal agent that transforms YouTube videos and audio recordings into ready-to-publish social carousels, video scripts, executive insights, and Obsidian LLM Wikis on demand.**

Built for the **Plow Agent Hackathon**, powered by the `plow-hermes-agent` base runtime, and deployed directly to your phone via iMessage & SMS.

---

## 🌟 What Transcritor AI Does

Founders, creators, and operators consume dozens of hours of long-form video podcasts, keynotes, and masterclasses every month. Transcribing, extracting actionable mental models, and translating someone else's personal narrative into your own brand voice is friction-heavy.

**Transcritor AI solves this in seconds directly through your chat:**

1. ⚡ **Instant Native Transcription:** Extracts complete video transcripts from YouTube in under 1 second without costly third-party speech API dependencies.
2. 🧠 **Executive Synthesis:** Distills the core narrative into an executive summary and 5 high-leverage mental models.
3. 🔄 **Niche Reframing & Ethical Repurposing:** Removes proprietary numbers, personal anecdotes, or identifying creator details, translating underlying principles into authentic first-person content customized for your exact market (e.g., Tech & AI Agents).
4. 📊 **Multi-Format Deliverable Engine:** Generates:
   * **10-Slide Social Carousels** (Instagram / LinkedIn) with hooks, breakdowns, and conversion CTAs.
   * **Structured Video Scripts** (Reels / Shorts / TikTok).
   * **Obsidian LLM Wiki Cards** (Andrew Karpathy / Cerebro knowledge standard).
   * **Executive Briefs & Newsletters**.
5. 📱 **Chat-Native (iMessage / SMS):** Text a link from your phone; receive ready-to-design copy right in your messaging app.

---

## 🚀 Installation & Quick Start

Follow these steps to deploy and run your own instance of Transcritor AI on the Plow Network.

### Prerequisites

* [Docker Desktop](https://www.docker.com/) or [OrbStack](https://orbstack.dev/) (macOS / Linux / WSL2).
* Python 3.10+ on host machine.
* A Plow Account (free via `bin/plow-agents login`).

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/eudanielhenrique/transcritor.git
cd transcritor
```

---

### Step 2: Authenticate and Mint a Plow Line

Login to Plow and mint an agent credential for your dedicated phone line:

```bash
# 1. Login with your phone number
bin/plow-agents login

# 2. View available lines
bin/plow-agents lines

# 3. Mint your agent credential (saves to ./plow-credentials)
bin/plow-agents mint
```

This creates a secured `./plow-credentials` file containing your agent token and API endpoint.

---

### Step 3: Register on Agent Index (One-Time)

Publish your agent's profile to the [Agent Index](https://aiworthusing.com/agent-index):

```bash
curl -O https://raw.githubusercontent.com/plow-pbc/agent-index-client/main/standalone/agent_index_client.py

set -a; . ./plow-credentials; set +a
python3 agent_index_client.py --register \
  --agent transcritor-ai \
  --name "Transcritor AI" \
  --blurb "Autonomous multimodal agent that transforms YouTube videos and audio into ready-to-publish social carousels, video scripts, executive insights, and Obsidian LLM Wikis on demand." \
  --repo "https://github.com/eudanielhenrique/transcritor" \
  --runtime "Plow Hermes (Docker)" \
  --install-url "https://github.com/eudanielhenrique/transcritor#installation--quick-start"
```

---

### Step 4: Launch the Container

Build and start the autonomous agent container:

```bash
docker compose up -d --build
```

Verify that the agent is running and healthy:

```bash
docker compose logs -f
```

You should see:
* `hermes-gateway`: Connected to your Plow line.
* `main-hermes`: Agent loop initialized with `runtime/SOUL.md`.
* `agent-index`: Hourly usage reporter active.

---

## 💬 Real-World Usage Example

Text your agent's phone number on iMessage or SMS:

```text
User:
Da uma olhada nesse video quero transformar ele em um carrossel:
https://www.youtube.com/watch?v=lz5VnovCpvY

Transcritor AI:
[Extracts transcript in 0.8s]
📌 Resumo Executivo: 5 modelos mentais fundamentais...
Escolha o formato desejado:
1. Roteiro Estruturado
2. Carrossel 10 Lâminas (Instagram/LinkedIn)
3. Roteiro Reels / TikTok
4. Ideias para Apresentação
5. Página Obsidian Wiki
6. Artigo Completo

User:
Vamos pensar em uma coisa: o conteúdo é da mentora, mas eu quero postar
no meu perfil sem falar dela, usando as ideias dela para o meu nicho.
Sou empreendedor na área de tecnologia e agentes de IA.

Transcritor AI:
[De-identifies & reframes concepts into 10-slide tech founder carousel]
Slide 1: "Você não precisa ter o produto perfeito pra começar a vender..."
Slide 3: "Regra #1: Processo comercial pesado não escala em tech..."
Slide 5: "Regra #2: Contratar antes de ajustar demanda é o erro mais caro..."
...
Slide 10: "Comenta 'AGENTE' que eu te mando como aplicar isso no seu negócio."
```

---

## 🛠️ Architecture

```
transcritor/
├── Dockerfile                   # Multi-stage image based on plow-hermes-agent
├── compose.yml                  # Docker Compose specification with agent volume
├── bin/
│   └── plow-agents              # Plow agent management CLI (login, mint, profile)
├── runtime/
│   └── SOUL.md                  # Persona, silent execution rules & deliverable schemas
├── image/
│   └── s6-overlay/s6-rc.d/      # S6 supervised hourly agent-index telemetry service
├── skills/                      # Hermes skills (yt-dlp, transcript extractors)
└── docs/screenshots/            # Real-world verification proofs & conversation logs
```

* **Base Runtime:** `public.ecr.aws/e1h7x4a2/plow-cloud-agents:base-cd2a898d673812621bae6764560e455807e9818e`
* **Telemetry:** Background S6 service reporting hourly token metrics to Agent Index.
* **Extraction Engine:** `youtube-transcript-api` + `yt-dlp` for lightning-fast transcript fetching.

---

## 👥 Authors & Community

* **Creator:** [Daniel Henrique](https://github.com/eudanielhenrique)
* **Agent Index Profile:** [Transcritor AI on AI Worth Using](https://aiworthusing.com/agent-index/transcritor-ai)
* **License:** Apache-2.0
