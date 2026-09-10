#!/usr/bin/env python3
"""
Gera um roteiro de YouTube a partir de uma transcrição.

Uso:
    python roteiro.py <arquivo_transcricao.md> [output_dir]

Exemplo:
    python roteiro.py "E:/Temp/transcricoes/transcricao_sindrome_impostor.md"
"""

import os
import re
import sys
import time
from pathlib import Path

# Configuração padrão
OUTPUT_DIR = Path(os.environ.get("TRANSCRIVE_OUTPUT_DIR", "E:/Temp/transcricoes"))
VIDEO_URL = os.environ.get("TRANSCRIVE_VIDEO_URL", "")
VIDEO_TITLE = os.environ.get("TRANSCRIVE_VIDEO_TITLE", "")


def extrair_frontal(transcricao: str) -> str:
    """Tenta extrair os primeiros ~15 segundos (gancho) da transcrição."""
    lines = [l.strip() for l in transcricao.splitlines() if l.strip()]
    if not lines:
        return ""
    # Pega as primeiras 5 linhas como gancho
    hook_lines = lines[:5]
    return " ".join(hook_lines)


def extrair_problema(transcricao: str) -> str:
    """Tenta extrair a seção de problema/contexto."""
    lines = [l.strip() for l in transcricao.splitlines() if l.strip()]
    if len(lines) < 10:
        return " ".join(lines)
    # Assume que o problema vem depois do gancho, nas próximas 10 linhas
    problema_lines = lines[5:15]
    return " ".join(problema_lines)


def extrair_solucao(transcricao: str) -> str:
    """Tenta extrair a seção de solução/prática."""
    lines = [l.strip() for l in transcricao.splitlines() if l.strip()]
    if len(lines) < 20:
        return " ".join(lines[10:])
    # Solução nas próximas 15 linhas após o problema
    solucao_lines = lines[15:30]
    return " ".join(solucao_lines)


def extrair_como_funciona(transcricao: str) -> str:
    """Extrai a seção 'como funciona' / explicação central."""
    lines = [l.strip() for l in transcricao.splitlines() if l.strip()]
    if len(lines) < 40:
        return " ".join(lines[20:])
    return " ".join(lines[30:50])


def extrair_beneficio(transcricao: str) -> str:
    """Extrai seção de benefício/resultado."""
    lines = [l.strip() for l in transcricao.splitlines() if l.strip()]
    if len(lines) < 60:
        return " ".join(lines[40:])
    return " ".join(lines[50:70])


def extrair_cta(transcricao: str) -> str:
    """Extrai chamada para ação / fechamento."""
    lines = [l.strip() for l in transcricao.splitlines() if l.strip()]
    # Pega as últimas 5 linhas
    cta_lines = lines[-5:]
    return " ".join(cta_lines)


def gerar_roteiro(transcricao: str) -> str:
    """Gera o roteiro Markdown completo a partir da transcrição."""
    hoje = time.strftime("%Y-%m-%d")

    hook = extrair_frontal(transcricao)
    problema = extrair_problema(transcricao)
    solucao = extrair_solucao(transcricao)
    como_funciona = extrair_como_funciona(transcricao)
    beneficio = extrair_beneficio(transcricao)
    cta = extrair_cta(transcricao)

    roteiro = f"""---
tipo: roteiro
status: rascunho
criado: {hoje}
tags: [roteiro, youtube]
fonte: transcricao
duracao_estimada: 5min
---

# Roteiro — {VIDEO_TITLE or 'Vídeo'}

> Baseado na transcrição automática. Revisar e ajustar antes de gravar.

## 1. Gancho (0:00–0:15)

{hook}

## 2. Problema (0:15–0:30)

{problema}

## 3. Solução (0:30–1:00)

{solucao}

## 4. Como funciona (1:00–2:00)

{como_funciona}

## 5. Benefício (2:00–3:00)

{beneficio}

## 6. CTA (3:00–fim)

{cta}

---

## Notas de produção

- **Tom:** Conversa, não venda
- **Ritmo:** Depressado, pausas entre blocos
- **Visual:** Quer que a gente grave com mais uma pessoa? Se sim, ajustar os blocos de conversa
- **Revisar:** Conferir nomes, números, links antes de publicar

## Fonte

- Transcrição: {Path(transcricao).name}
- Vídeo: {VIDEO_URL or "Não especificado"}
"""
    return roteiro


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    transcricao_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT_DIR

    if not transcricao_path.exists():
        print(f"[ERRO] Arquivo não encontrado: {transcricao_path}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Lendo transcrição: {transcricao_path}")
    transcricao = transcricao_path.read_text(encoding="utf-8")

    print(f"[INFO] Transcrição tem {len(transcricao):,} caracteres")
    print(f"[INFO] Gerando roteiro...")

    roteiro = gerar_roteiro(transcricao)

    # Determina slug a partir do nome do arquivo de transcrição
    slug = transcricao_path.stem.replace("transcricao_", "").replace("_", "-").lower()

    output_file = output_dir / f"roteiro_{slug}.md"
    output_file.write_text(roteiro, encoding="utf-8")

    print(f"[OK] Roteiro salvo: {output_file}")
    print(f"[INFO] Tamanho: {len(roteiro):,} caracteres")

    return 0


if __name__ == "__main__":
    sys.exit(main())
