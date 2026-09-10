#!/usr/bin/env bash
#
# Pipeline completo: baixa vídeo do YouTube → transcreve → gera roteiro → salva no Cerebro
#
# Uso:
#   ./transcreve.sh <URL_DO_VIDEO>
#
# Exemplo:
#   ./transcreve.sh "https://www.youtube.com/watch?v=-OxFis8Ulgg"
#
set -e

# ============
# Configuração
# ============

VIDEO_URL="${1:?Uso: ./transcreve.sh <URL_DO_VIDEO>}"

# Caminhos (editar conforme o ambiente)
VAULT_PATH="${CEREBRO_VAULT_PATH:-/c/Users/ddani/iCloudDrive/iCloud~md~obsidian/Cerebro}"
TEMP_VIDEOS="${TEMP_DIR:-/c/Users/ddani/Temp/videos}"
TEMP_TRANSCRICOES="${TEMP_TRANSCRICOES_DIR:-/c/Users/ddani/Temp/transcricoes}"
API_URL="${TRANSCRIVE_API_URL:-http://localhost:5000/transcrever}"
CHUNK_SEC="${TRANSCRIVE_CHUNK_SEC:-30}"
PYTHON="${PYTHON:-/c/Users/ddani/AppData/Local/Programs/Python/Python312/python.exe}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ============
# Verificações
# ============

echo "========================================="
echo "Pipeline: YouTube → Cerebro"
echo "========================================="
echo "URL: $VIDEO_URL"
echo "Vault: $VAULT_PATH"
echo "Temp vídeos: $TEMP_VIDEOS"
echo "Temp transcrições: $TEMP_TRANSCRICOES"
echo "API: $API_URL"
echo "Chunk: ${CHUNK_SEC}s"
echo "Python: $PYTHON"
echo ""

# Verifica python
if [ ! -x "$PYTHON" ]; then
    PYTHON="python3"
    if ! command -v "$PYTHON" &>/dev/null; then
        echo "[ERRO] Python não encontrado. Instale Python 3.10+ e configure PYTHON."
        exit 1
    fi
    echo "[INFO] Usando python3 da PATH"
fi

# Verifica yt-dlp
if ! command -v yt-dlp &>/dev/null; then
    echo "[AVISO] yt-dlp não encontrado. Tentando pip install..."
    pip install yt-dlp || { echo "[ERRO] Falha ao instalar yt-dlp"; exit 1; }
fi

# Verifica ffmpeg
if ! command -v ffmpeg &>/dev/null; then
    echo "[AVISO] ffmpeg não encontrado na PATH"
fi

# Verifica API Flask
echo -n "[INFO] Verificando API Flask em $API_URL... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" != "200" ]; then
    echo "FALHA (HTTP $HTTP_CODE). Inicie a API Flask antes de rodar este script."
    exit 1
fi
echo "OK"

# Cria diretórios temporários
mkdir -p "$TEMP_VIDEOS" "$TEMP_TRANSCRICOES"

# ============
# 1. Download do vídeo
# ============

echo ""
echo "=== Passo 1: Download do áudio do YouTube ==="

VIDEO_SLUG=$(echo "$VIDEO_URL" | sed -E 's/.*(?:v=|youtu\.be/)//' | cut -d'?' -f1)
VIDEO_TITLE=$(yt-dlp --skip-download --print "%(title)s" "$VIDEO_URL" 2>/dev/null || echo "video_$VIDEO_SLUG")

# Sanitiza título para nome de arquivo
VIDEO_FILE_NAME=$(echo "$VIDEO_TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g' | tr -s '_' | sed 's/^_//;s/_$//')
WAV_OUTPUT="$TEMP_VIDEOS/${VIDEO_FILE_NAME}.wav"

echo "[INFO] Título: $VIDEO_TITLE"
echo "[INFO] Slug: $VIDEO_FILE_NAME"
echo "[INFO] Áudio será salvo em: $WAV_OUTPUT"

if [ -f "$WAV_OUTPUT" ]; then
    echo "[INFO] Áudio já existe — pulando download"
else
    echo "[INFO] Baixando áudio..."
    yt-dlp \
        --extract-audio \
        --audio-format wav \
        --audio-quality 0 \
        --output "$WAV_OUTPUT" \
        "$VIDEO_URL" 2>&1 | tail -5
fi

if [ ! -f "$WAV_OUTPUT" ]; then
    echo "[ERRO] Falha ao baixar áudio. Verifique a URL e a conexão."
    exit 1
fi

WAV_SIZE=$(du -h "$WAV_OUTPUT" | cut -f1)
echo "[OK] Áudio baixado: $WAV_OUTPUT ($WAV_SIZE)"

# ============
# 2. Converte para 16kHz mono (se necessário)
# ============

echo ""
echo "=== Passo 2: Conversão para 16kHz mono ==="

WAV_16K="$TEMP_VIDEOS/${VIDEO_FILE_NAME}_16k.wav"

if [ ! -f "$WAV_16K" ]; then
    echo "[INFO] Convertendo para 16kHz mono..."
    ffmpeg -y -i "$WAV_OUTPUT" -vn -acodec pcm_s16le -ar 16000 -ac 1 "$WAV_16K" 2>&1 | tail -3
else
    echo "[INFO] Arquivo 16kHz já existe — pulando conversão"
fi

if [ ! -f "$WAV_16K" ]; then
    echo "[ERRO] Falha ao converter áudio. Verifique se ffmpeg está instalado."
    exit 1
fi

WAV_16K_SIZE=$(du -h "$WAV_16K" | cut -f1)
echo "[OK] Áudio 16kHz: $WAV_16K ($WAV_16K_SIZE)"

# ============
# 3. Transcrição chunk por chunk
# ============

echo ""
echo "=== Passo 3: Transcrição (chunk por chunk) ==="

export TRANSCRIVE_API_URL="$API_URL"
export TRANSCRIVE_CHUNK_SEC="$CHUNK_SEC"
export TRANSCRIVE_TEMP_DIR="$TEMP_VIDEOS"
export TRANSCRIVE_OUTPUT_DIR="$TEMP_TRANSCRICOES"

"$PYTHON" "$SCRIPT_DIR/transcreve.py" "$WAV_16K"

if [ ! -f "$TEMP_TRANSCRICOES/transcricao_${VIDEO_FILE_NAME}.md" ]; then
    echo "[ERRO] Transcrição não foi gerada. Verifique os logs acima."
    exit 1
fi

echo "[OK] Transcrição concluída"

# ============
# 4. Geração do roteiro
# ============

echo ""
echo "=== Passo 4: Geração do roteiro ==="

export TRANSCRIVE_VIDEO_URL="$VIDEO_URL"
export TRANSCRIVE_VIDEO_TITLE="$VIDEO_TITLE"
export TRANSCRIVE_OUTPUT_DIR="$TEMP_TRANSCRICOES"

"$PYTHON" "$SCRIPT_DIR/roteiro.py" "$TEMP_TRANSCRICOES/transcricao_${VIDEO_FILE_NAME}.md"

if [ ! -f "$TEMP_TRANSCRICOES/roteiro_${VIDEO_FILE_NAME}.md" ]; then
    echo "[AVISO] Roteiro não foi gerado — verifique a transcrição"
fi

echo "[OK] Roteiro gerado"

# ============
# 5. Salva no Cerebro
# ============

echo ""
echo "=== Passo 5: Salvando no Cerebro ==="

export CEREBRO_VAULT_PATH="$VAULT_PATH"
export CEREBRO_ARTICLE_SLUG="$VIDEO_FILE_NAME"
export TRANSCRIVE_VIDEO_URL="$VIDEO_URL"

"$PYTHON" "$SCRIPT_DIR/wiki.py" \
    "$TEMP_TRANSCRICOES/roteiro_${VIDEO_FILE_NAME}.md" \
    "$TEMP_TRANSCRICOES/transcricao_${VIDEO_FILE_NAME}.md" \
    "$VIDEO_FILE_NAME"

echo ""
echo "========================================="
echo "Pipeline concluído com sucesso!"
echo "========================================="
echo ""
echo "Arquivos no Cerebro:"
echo "  Raw:  $VAULT_PATH/raw/sources/videos/${VIDEO_FILE_NAME}__raw_transcript.md"
echo "  Wiki: $VAULT_PATH/wiki/articles/${VIDEO_FILE_NAME}.md"
echo ""
echo "Arquivos intermediários (E:/Temp):"
echo "  Áudio:     $WAV_16K"
echo "  Transcrição: $TEMP_TRANSCRICOES/transcricao_${VIDEO_FILE_NAME}.md"
echo "  Roteiro:   $TEMP_TRANSCRICOES/roteiro_${VIDEO_FILE_NAME}.md"
