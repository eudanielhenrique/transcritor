---
name: cerebro-youtube
description: "Transcreve e indexa vídeos do YouTube em vault Markdown (ex: Obsidian Cerebro) usando pipeline replicador-cerebro. Baixa áudio, transcreve chunk por chunk via API Flask local, gera roteiro e salva no padrão Karpathy/llm-wiki."
version: 1.0.0
tags: [transcricao, youtube, cerebro, obsidian, pipeline]
---

# Skill: cerebro-youtube

Transcreve vídeos do YouTube e indexa em um vault Markdown (ex: Obsidian Cerebro) usando o pipeline `replicador-cerebro`.

> Este skill é agnóstico a agente: pode ser usado por qualquer LLM/agente que receba a instrução e tenha acesso aos scripts. Não depende de Hermes, Claude, Codex ou similares.

## Quando usar

- Quando recebe um link de YouTube e precisa salvar a transcrição + roteiro no vault Markdown
- Para automatizar o processo de ingestão de conteúdo externo

## Pré-requisitos

Antes de usar este skill, garanta que:

1. **API Flask local** esteja rodando em `http://localhost:5000` com endpoint `POST /transcrever`
   - Verifique com: `curl http://localhost:5000/health` → deve retornar `ok`
   - Se não estiver rodando, inicie primeiro
2. **yt-dlp** instalado: `pip install yt-dlp`
3. **ffmpeg** na PATH
4. **Python 3.10+** disponível
5. **Acesso de escrita** ao vault Markdown de destino

### Variáveis de ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `CEREBRO_VAULT_PATH` | `C:\Users\ddani\iCloudDrive\iCloud~md~obsidian\Cerebro` | Caminho do vault de destino |
| `TRANSCRIVE_API_URL` | `http://localhost:5000/transcrever` | Endpoint API Flask |
| `TRANSCRIVE_CHUNK_SEC` | `30` | Duração de cada chunk em segundos |
| `TRANSCRIVE_TEMP_DIR` | `E:/Temp/videos/` | Onde baixar/converter áudio |
| `TRANSCRIVE_OUTPUT_DIR` | `E:/Temp/transcricoes/` | Onde salvar transcrições |

## Como usar

### Opção 1: Script completo (recomendado)

**Windows:**
```bat
transcreve.bat "https://www.youtube.com/watch?v=-OxFis8Ulgg"
```

**Linux/macOS:**
```bash
./transcreve.sh "https://www.youtube.com/watch?v=-OxFis8Ulgg"
```

O script faz tudo:
1. Baixa áudio do YouTube com yt-dlp
2. Converte para 16kHz mono com ffmpeg
3. Divide em chunks de 30s
4. Transcreve cada chunk via API Flask
5. Gera roteiro Markdown
6. Salva no vault (raw + wiki)

### Opção 2: Passo a passo (para controle granular)

**1. Baixar e converter áudio:**
```bash
yt-dlp --extract-audio --audio-format wav --audio-quality 0 \
  --output "E:/Temp/videos/<slug>.wav" "<URL>"

ffmpeg -y -i "E:/Temp/videos/<slug>.wav" \
  -vn -acodec pcm_s16le -ar 16000 -ac 1 \
  "E:/Temp/videos/<slug>_16k.wav"
```

**2. Transcrever:**
```bash
python transcreve.py "E:/Temp/videos/<slug>_16k.wav" "E:/Temp/transcricoes/"
```

**3. Gerar roteiro:**
```bash
python roteiro.py "E:/Temp/transcricoes/transcricao_<slug>.md"
```

**4. Salvar no vault:**
```bash
python wiki.py "E:/Temp/transcricoes/roteiro_<slug>.md" \
               "E:/Temp/transcricoes/transcricao_<slug>.md" \
               "<slug>"
```

## Estrutura de saída no vault

```
<vault>/
├── raw/sources/videos/
│   └── <slug>__raw_transcript.md     ← transcrição raw (imutável)
└── wiki/articles/
    └── <slug>.md                      ← página wiki compilada
```

Além de atualizar:
- `wiki/index.md` → seção "Artigos"
- `wiki/overview.md` → seção "Artigos compilados"
- `wiki/log.md` → entrada de ingest

## Decisão: roteiro vs. só base de conhecimento

Nem todo vídeo precisa de roteiro estruturado ou conteúdo para rede social.

### Padrão (sem aviso do usuário)

O skill salva **apenas a base de conhecimento**:
- Transcreve e salva em `raw/sources/videos/<titulo-slug>__raw_transcript.md` (imutável)
- Cria página wiki `wiki/articles/<titulo-slug>.md` com título oficial + síntese leve + link para o raw
- Atualiza `wiki/index.md`, `wiki/overview.md`, `wiki/log.md`
- **Não** gera roteiro em 6 blocos, nem variações para redes sociais

### Quando gerar roteiro / conteúdo para rede social

Só se o usuário avisar explicitamente ("quero roteiro", "preciso de conteúdo pra rede social", "gere threaded", "ok para postar", etc.).

Nesse caso:
- Gera roteiro em 6 blocos (Gancho/Problema/Solução/Como funciona/Benefício/CTA) ou outro formato pedido
- Gera variações para rede social se pedido (ex: thread LinkedIn, post Instagram)
- Ainda salva o raw e a página wiki básica — o roteiro fica à parte ou integrado conforme pedido

### Antes de começar

Se tiver dúvida sobre o objetivo do vídeo, **pergunte antes de transcrever ou gerar qualquer saída**: "Esse vídeo é só pra base de conhecimento, ou quer roteiro/conteúdo pra rede social?"

Isso evita gerar roteiro desnecessário e gastar tempo com saída que não será usada.

## Nomeação de arquivos: usar o título do vídeo

**Regra geral:** nomeia arquivos e páginas wiki usando o **título oficial do vídeo**, nunca o ID do YouTube.

- Obtenha o título com: `yt-dlp --skip-download --print "%(title)s" "<URL>"`
- H1 da página wiki = título oficial do vídeo
- Slug do arquivo = título limpo (minúsculas, hífens, sem acento, sem parênteses), ex: `hermes-agent-nao-e-um-agente-de-ia-e-um-sistema`
- Arquivo raw: `<slug>__raw_transcript.md`
- Arquivo wiki: `<slug>.md`
- O ID do YouTube fica apenas no campo `Fonte:` da wiki (com o link completo)

**Por que essa regra:** o ID do YouTube é inútil na navegação e confunde a base de conhecimento. O título é o que o usuário lembra e o que faz sentido ler no índice.

## Limitações

- API Flask usa Google Web Speech (gratuito). Cada chunk é enviado individualmente.
- Chunks > 1min podem falhar. Padrão é 30s.
- Último chunk pode ser silêncio → HTTP 400. Isso é normal.
- iCloud pode travar arquivos. Feche o Obsidian antes de rodar se mover arquivos falhar.

## Repositório

Código fonte: `https://github.com/eudanielhenrique/replicador-cerebro`

## Troubleshooting

**API Flask não responde:**
```bash
curl http://localhost:5000/health
# Se não responder, inicie a API antes
```

**yt-dlp não encontrado:**
```bash
pip install yt-dlp
```

**Arquivo WAV corrompido após download:**
- Verifique se o áudio foi baixado completamente
- Tente baixar novamente com `--audio-quality 0`

**Chunk final falha com HTTP 400:**
- Normal: pode ser silêncio no final do vídeo
- 35/36 chunks OK é aceitável — não precisa retranscrever

**iCloud travar arquivos ao mover:**
- Feche o Obsidian
- Ou use Python pathlib/shutil para mover (evita shell)

**iCloud travar arquivos ao mover:**
- Feche o Obsidian
- Ou use Python pathlib/shutil para mover (evita shell)

