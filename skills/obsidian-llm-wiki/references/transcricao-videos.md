---
name: transcricao-videos
description: Pipeline completo para transcrever vídeos do YouTube, gerar roteiros e salvar no Cerebro (Obsidian vault) no padrão llm-wiki.
---

# Pipeline de Transcrição de Vídeos para o Cerebro

Uso quando o objetivo é baixar um ou mais vídeos do YouTube, transcrevê-los via API Flask local, gerar roteiros Markdown e salvar no vault do Cerebro (Obsidian) seguindo o padrão `obsidian-llm-wiki`.

## Pré-requisitos

- **Python 3.10+** (testado com 3.12 no Windows)
- **yt-dlp** instalado: `pip install yt-dlp`
- **API Flask local** rodando em `http://localhost:5000` com endpoint `POST /transcrever`
  - Aceita WAV/OGG/MP3 com `Content-Type: audio/wav`
  - Limite prático: ~1 MB por request (chunks maiores retornam HTTP 500)
- **ffmpeg** na PATH (para conversão de áudio para 16kHz mono)
- **Acesso ao vault** do Cerebro (iCloud Drive, caminho: `C:\Users\ddani\iCloudDrive\iCloud~md~obsidian\Cerebro`)

## Visão geral do pipeline

```
YouTube URL → yt-dlp (baixar áudio) → ffmpeg (16kHz mono WAV) → chunk 30s → API Flask → montar transcrição → gerar roteiro → salvar raw + wiki no Cerebro
```

## Passo a passo

### 1. Download do áudio

```bash
yt-dlp --extract-audio --audio-format wav --audio-quality 0 --output "E:/Temp/videos/<slug>.wav" "<YOUTUBE_URL>"
```

- O `<slug>` deve ser derivado do título do vídeo: minúsculas, sem acentos, espaços → underscores, sem caracteres especiais.
- Saída: arquivo WAV PCM (pode ser stereo, 48kHz — não importa, o próximo passo normaliza).

### 2. Conversão para 16kHz mono

```bash
ffmpeg -y -i "E:/Temp/videos/<slug>.wav" -vn -acodec pcm_s16le -ar 16000 -ac 1 "E:/Temp/videos/<slug>_16k.wav"
```

- Saída: WAV 16kHz mono, 16-bit PCM, sem metadata extra (tentar evitar metadata que gere chunks LIST/INFO no cabeçalho).
- Verificar com wave module:
  ```python
  import wave
  with wave.open("E:/Temp/videos/<slug>_16k.wav", "rb") as wf:
      print(wf.getnchannels(), wf.getsampwidth(), wf.getframerate(), wf.getnframes())
  ```

### 3. Transcrição chunk por chunk

Dividir o áudio em chunks de 30 segundos e enviar cada um para a API Flask.

**Ler o WAV com wave module (NUNCA offsets fixos):**

```python
import wave
from pathlib import Path

wav_path = Path("E:/Temp/videos/<slug>_16k.wav")
with wave.open(str(wav_path), "rb") as wf:
    nchannels = wf.getnchannels()
    sampwidth = wf.getsampwidth()
    framerate = wf.getframerate()
    nframes = wf.getnframes()
    raw_audio = wf.readframes(nframes)

# Cada frame = nchannels * sampwidth bytes
bytes_per_frame = nchannels * sampwidth  # 2 bytes para 16-bit mono
bytes_per_sec = framerate * bytes_per_frame  # 32000 bytes/s para 16kHz mono 16-bit
chunk_bytes = 30 * bytes_per_sec  # 960000 bytes por chunk de 30s
total_chunks = (len(raw_audio) + chunk_bytes - 1) // chunk_bytes
```

**Criar cada chunk WAV com wave module:**

```python
import wave as wavemod

chunk_path = Path(f"/tmp/yt_chunks/chunk_{i:04d}.wav")
with wavemod.open(str(chunk_path), "wb") as wc:
    wc.setnchannels(nchannels)
    wc.setsampwidth(sampwidth)
    wc.setframerate(framerate)
    wc.writeframes(raw_audio[start:end])
```

**Enviar para API Flask:**

```python
import requests

r = requests.post(
    "http://localhost:5000/transcrever",
    files={"audio": (chunk_path.name, open(chunk_path, "rb"), "audio/wav")},
    timeout=180,
)

if r.status_code == 200:
    data = r.json()
    texto = data.get("transcricao", "").strip() or r.text.strip()
else:
    # retry ou erro
    pass
```

**Regras de chunk:**

- **Tamanho máximo do chunk:** ~1 MB (960.000 bytes para 30s de 16kHz mono 16-bit). Chunks maiores retornam HTTP 500 na API Flask local.
- **Duração de cada chunk:** 30 segundos.
- **Retry:** 3 tentativas com backoff de 3s entre elas.
- **Limpeza:** deletar chunks antigos a cada 5 chunks processados para não encher o disco.
- **Último chunk:** pode ser silêncio e retornar HTTP 400 — isso é esperado, não é erro do pipeline.

### 4. Montar transcrição

Concatenar todas as transcrições dos chunks com `

` entre elas e salvar como Markdown com frontmatter:

```markdown
---
transcricao_de: <arquivo.wav>
data: YYYY-MM-DD
total_chunks: N
sucesso: N
falhas: N
caracteres: N
---

# Transcrição

<texto concatenado>
```

### 5. Gerar roteiro

A partir da transcrição, gerar um roteiro Markdown estruturado em 6 blocos:

1. **Gancho** (0:00–0:15) — primeiras linhas da transcrição
2. **Problema** (0:15–0:30) — contexto/problema identificado
3. **Solução** (0:30–1:00) — proposta/solução
4. **Como funciona** (1:00–2:00) — explicação central
5. **Benefício** (2:00–3:00) — resultados esperados
6. **CTA** (3:00–fim) — chamada para ação / fechamento

Plus notas de produção: tom, ritmo, visual, revisar nomes/números/links.

### 6. Salvar no Cerebro

Seguindo o padrão `obsidian-llm-wiki`:

**Raw (imutável):**

```
raw/sources/videos/<slug>__raw_transcript.md
```

Frontmatter:
```yaml
---
tipo: raw
fonte: transcricao
slug: <slug>
video_url: <URL>
data_ingest: YYYY-MM-DD
total_caracteres: N
---
```

**Wiki compilada:**

```
wiki/articles/<slug>.md
```

Frontmatter:
```yaml
---
tipo: wiki
categoria: artigo
tags: [artigo, <slug>]
status: compilado
criado: YYYY-MM-DD
titulo: <Título legível>
slug: <slug>
raw_source: raw/sources/videos/<slug>__raw_transcript.md
roteiro_fonte: <arquivo_roteiro.md>
---
```

**Atualizar índices:**

- `wiki/index.md`: adicionar entrada em seção `## Artigos` (ou criar a seção se não existir)
- `wiki/overview.md`: adicionar entrada em seção `## Artigos compilados` (ou criar)
- `wiki/log.md`: adicionar entrada `## [YYYY-MM-DD] ingest | Artigo — <titulo>` com slug, raw, wiki, status

## Pitfalls

- **NUNCA usar offsets fixos para ler WAV.** O cabeçalho WAV pode ter chunks extras (LIST, INFO, ISFT) entre `fmt ` e `data`. Sempre usar `wave` module ou varrer os chunks. Offsets fixos de 44 bytes falham silenciosamente e geram chunks de 26 bytes (silêncio puro).
- **Sample rate corrompida:** se ler o cabeçalho WAV manualmente e encontrar sample_rate = 1048576001 Hz (ou qualquer valor impossível), o parser de chunks está errado — descarta e usa wave module.
- **API Flask retorna HTTP 500 para chunks > ~1 MB.** Mantenha chunks de no máximo 30s (960KB para 16kHz mono 16-bit).
- **iCloud lock:** ao salvar no vault, o iCloud pode travar arquivos. Se o Obsidian estiver aberto, feche antes de salvar. Use Python pathlib/shutil em vez de shell mv/rm.
- **Último chunk silencioso:** o final do vídeo pode ser silêncio e a API retorna HTTP 400. Isso é normal — registro no log como "falha esperada" não como erro do pipeline.
- **Slug duplication:** ao derivar slug do título, sanitizar completamente: minúsculas, sem acentos, sem caracteres especiais, sem espaços duplicados. Exemplo: "Como criar conteúdo mesmo se achando um merda (Sindrome do Impostor)" → `sindrome-do-impostor-como-parar-de-se-sabotar`.
- **Diferenciar repo da API de transcrição do vault do Cerebro.** O repo `transcreveAPI` (em `E:\dev\transcreveAPI`) é o sistema de transcrição; o vault Cerebro (em `C:\Users\ddani\iCloudDrive\iCloud~md~obsidian\Cerebro`) é o repositório de conhecimento. Não confundir os dois ao criar scripts de replicação.

## Replicação em outra máquina

Para replicar o pipeline em outra máquina:

1. Clonar o repo `replicador-cerebro` (ou copiar os scripts: `transcreve*.py`, `roteiro.py`, `wiki.py`)
2. Instalar deps: `pip install -r requirements.txt`
3. Garantir que `yt-dlp`, `ffmpeg` e a API Flask estejam disponíveis
4. Editar as variáveis de ambiente ou os valores default nos scripts:
   - `CEREBRO_VAULT_PATH` → caminho do vault na nova máquina
   - `TRANSCRIVE_OUTPUT_DIR` → diretório de saída das transcrições
   - `TRANSCRIVE_TEMP_DIR` → diretório temporário para chunks
   - `TRANSCRIVE_API_URL` → URL da API Flask
5. Rodar: `python transcreve3.py "<arquivo.wav>" "<output_dir>"`

Os scripts têm valores default que funcionam na máquina de origem; para outra máquina, sobrescrever via variáveis de ambiente.

## Scripts do pipeline

- **`transcreve3.py`** — transcrição Robusta (usa wave module, chunks de 30s, retry, limpeza)
- **`transcreve2.py`** — versão alternativa (ler manualmente, menos confiável)
- **`transcreve.py`** — versão original (depreciada — offsets fixos falham com WAVs com metadata)
- **`roteiro.py`** — gera roteiro Markdown a partir da transcrição
- **`wiki.py`** — salva raw + wiki no Cerebro, atualiza índices
- **`transcreve.sh`** — script Shell completo: download → transcrição → roteiro → wiki
- **`transcreve.bat`** — script Windows completo (equivalente ao .sh)

## Limitações conhecidas

- A API Flask local usa SpeechRecognition com Google Web Speech (gratuito, sem API key). Cada chunk é enviado individualmente; se a API ficar sem quota ou mudar, o pipeline quebra.
- Vídeos com áudio muito baixo ou silêncio nos primeiros segundos podem gerar transcrição com erros de reconhecimento.
- Idioma do vídeo deve ser português brasileiro para melhor reconhecimento (a API não tem detecção automática de idioma).
