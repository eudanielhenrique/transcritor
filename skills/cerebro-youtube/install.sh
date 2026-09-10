#!/usr/bin/env bash
#
# Instala o skill cerebro-youtube e suas dependências.
#
# Uso:
#   ./install.sh
#
set -e

echo "=============================================="
echo "Instalando skill cerebro-youtube"
echo "=============================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_NAME="cerebro-youtube"

# ===============================================
# 1. Detectar ambiente Hermes
# ===============================================
echo "=== Passo 1: Ambiente Hermes ==="

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
SKILLS_DIR="$HERMES_HOME/skills"

if [[ -d "$SKILLS_DIR" ]]; then
    echo "[OK] Diretório de skills encontrado: $SKILLS_DIR"
else
    echo "[INFO] Criando diretório de skills: $SKILLS_DIR"
    mkdir -p "$SKILLS_DIR"
fi

SKILL_DEST="$SKILLS_DIR/$SKILL_NAME"

if [[ -d "$SKILL_DEST" ]]; then
    echo "[INFO] Skill já instalado em $SKILL_DEST"
    echo "Atualizando..."
else
    echo "[INFO] Instalando skill em $SKILL_DEST"
    mkdir -p "$SKILL_DEST"
fi

# Copiar SKILL.md
if [[ -f "$SCRIPT_DIR/SKILL.md" ]]; then
    cp "$SCRIPT_DIR/SKILL.md" "$SKILL_DEST/SKILL.md"
    echo "[OK] SKILL.md copiado para $SKILL_DEST/"
else
    echo "[ERRO] SKILL.md não encontrado em $SCRIPT_DIR"
    exit 1
fi

# ===============================================
# 2. Verificar dependências
# ===============================================
echo ""
echo "=== Passo 2: Dependências ==="

# Python
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "[AVISO] Python não encontrado. Alguns scripts podem não funcionar."
fi

# yt-dlp
if command -v yt-dlp &>/dev/null; then
    echo "[OK] yt-dlp: $(yt-dlp --version 2>&1)"
else
    echo "[AVISO] yt-dlp não encontrado. Instale com: pip install yt-dlp"
fi

# ffmpeg
if command -v ffmpeg &>/dev/null; then
    echo "[OK] ffmpeg: $(ffmpeg -version 2>&1 | head -1)"
else
    echo "[AVISO] ffmpeg não encontrado. Baixe em https://ffmpeg.org/"
fi

# ===============================================
# 3. Scripts de apoio (opcional)
# ===============================================
echo ""
echo "=== Passo 3: Scripts de apoio ==="

if [[ -f "$SCRIPT_DIR/install.sh" ]]; then
    cp "$SCRIPT_DIR/install.sh" "$SKILL_DEST/install.sh"
    chmod +x "$SKILL_DEST/install.sh" 2>/dev/null || true
    echo "[OK] install.sh copiado"
fi

echo ""
echo "=============================================="
echo "Skill '$SKILL_NAME' instalado com sucesso!"
echo "=============================================="
echo ""
echo "Localização: $SKILL_DEST/"
echo ""
echo "Para usar:"
echo "  hermes --skills cerebro-youtube"
echo ""
echo "Ou manualmente:"
echo "  $SKILL_DEST/transcreve.sh \"<URL_DO_VIDEO>\""
echo ""

