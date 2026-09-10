#!/usr/bin/env python3
"""
Salva transcrição raw + roteiro compilado no Cerebro (Obsidian vault),
no padrão Karpathy / llm-wiki.

Uso:
    python wiki.py <roteiro.md> <transcricao.md> <slug>

Exemplo:
    python wiki.py "E:/Temp/transcricoes/roteiro_sindrome-impostor.md"
                   "E:/Temp/transcricoes/transcricao_sindrome-impostor.md"
                   "sindrome-impostor"
"""

import os
import re
import sys
import time
from datetime import date
from pathlib import Path

# Configuração — editar conforme o ambiente
VAULT_PATH = Path(os.environ.get(
    "CEREBRO_VAULT_PATH",
    r"C:\Users\ddani\iCloudDrive\iCloud~md~obsidian\Cerebro"
))
HOJE = date.today().isoformat()


def sanitize_slug(slug: str) -> str:
    """Normaliza slug para nome de arquivo seguro."""
    slug = slug.strip().lower()
    slug = re.sub(r"[^a-z0-9_-]", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug


def slug_to_title(slug: str) -> str:
    """Converte slug kebab-case para título legível."""
    return slug.replace("-", " ").replace("_", " ").title()


def salvar_raw_transcricao(transcricao_path: Path, slug: str) -> Path:
    """Salva a transcrição raw no diretório raw/sources/videos/ do Cerebro."""
    raw_dir = VAULT_PATH / "raw" / "sources" / "videos"
    raw_dir.mkdir(parents=True, exist_ok=True)

    raw_name = f"{slug}__raw_transcript.md"
    raw_path = raw_dir / raw_name

    conteudo = f"""---
tipo: raw
fonte: transcricao
slug: {slug}
video_url: {os.environ.get("TRANSCRIVE_VIDEO_URL", "")}
data_ingest: {HOJE}
total_caracteres: {transcricao_path.stat().st_size}
---

# Transcrição Raw — {slug_to_title(slug)}

> Fonte imutável. Não editar. Ver página compilada: [[wiki/articles/{slug}.md|{slug_to_title(slug)}]]

{transcricao_path.read_text(encoding="utf-8")}
"""
    raw_path.write_text(conteudo, encoding="utf-8")
    print(f"[OK] Raw salvo: {raw_path}")
    print(f"[INFO] Tamanho: {raw_path.stat().st_size:,} bytes")
    return raw_path


def salvar_wiki_artigo(roteiro_path: Path, slug: str) -> Path:
    """Salva a página wiki compilada em wiki/articles/ do Cerebro."""
    articles_dir = VAULT_PATH / "wiki" / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)

    artigo_path = articles_dir / f"{slug}.md"

    roteiro = roteiro_path.read_text(encoding="utf-8")

    # Extrai metadados do roteiro se houver frontmatter
    meta = {}
    title = slug_to_title(slug)
    if roteiro.startswith("---"):
        match = re.match(r"^---\s*\n(.*?)\n---", roteiro, re.DOTALL)
        if match:
            frontmatter_text = match.group(1)
            for line in frontmatter_text.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    meta[key.strip()] = val.strip().strip("[]").strip('"')
            title = meta.get("titulo", meta.get("title", title))

    conteudo = f"""---
tipo: wiki
categoria: artigo
tags: [artigo, {slug}]
status: compilado
criado: {HOJE}
titulo: {title}
slug: {slug}
raw_source: raw/sources/videos/{slug}__raw_transcript.md
roteiro_fonte: {roteiro_path.name}
---

# {title}

> Artigo compilado a partir de roteiro + transcrição. Fonte raw: [[{slug}__raw_transcript|{slug}]]

## Sumário

{toc_placeholder}

## Conteúdo

{roteiro}
"""
    artigo_path.write_text(conteudo, encoding="utf-8")
    print(f"[OK] Wiki artigo salvo: {artigo_path}")
    print(f"[INFO] Tamanho: {artigo_path.stat().st_size:,} bytes")
    return artigo_path


def atualizar_index():
    """Adiciona entrada de artigo em wiki/index.md se ainda não existir."""
    index_path = VAULT_PATH / "wiki" / "index.md"

    if not index_path.exists():
        print(f"[INFO] index.md não existe — pulando atualização")
        return

    conteudo = index_path.read_text(encoding="utf-8")

    # Determina slug e título
    slug = os.environ.get("CEREBRO_ARTICLE_SLUG", "")
    if not slug:
        print(f"[INFO] CEREBRO_ARTICLE_SLUG não definido — pulando index update")
        return

    title = slug_to_title(slug)

    artigo_markdown = f"- [[wiki/articles/{slug}.md|{title}]] _(compilado {HOJE})_"

    if artigo_markdown in conteudo:
        print(f"[INFO] Entrada já existe em index.md — não duplicando")
        return

    # Tenta inserir em uma seção existente ou criar no final
    if re.search(r"^##\s+Artigos\s*$", conteudo, re.MULTILINE):
        conteudo = re.sub(
            r"(##\s+Artigos\s*\n)",
            r"\1" + artigo_markdown + "\n",
            conteudo,
            count=1,
            flags=re.MULTILINE
        )
        print(f"[OK] index.md: entrada adicionada na seção Artigos")
    elif re.search(r"^##\s+Artigos", conteudo, re.MULTILINE):
        # Seção com conteúdo, insere logo após o header
        conteudo = re.sub(
            r"(##\s+Artigos\b.*?\n)",
            r"\1" + artigo_markdown + "\n",
            conteudo,
            count=1,
            flags=re.MULTILINE
        )
        print(f"[OK] index.md: entrada adicionada na seção Artigos")
    else:
        # Cria seção no final do arquivo
        conteudo = conteudo.rstrip() + f"\n\n## Artigos\n\n{artigo_markdown}\n"
        print(f"[OK] index.md: seção Artigos criada e entrada adicionada")

    index_path.write_text(conteudo, encoding="utf-8")


def atualizar_overview():
    """Adiciona menção ao artigo compilado em wiki/overview.md."""
    overview_path = VAULT_PATH / "wiki" / "overview.md"

    if not overview_path.exists():
        print(f"[INFO] overview.md não existe — pulando")
        return

    conteudo = overview_path.read_text(encoding="utf-8")
    slug = os.environ.get("CEREBRO_ARTICLE_SLUG", "")
    title = slug_to_title(slug)

    if not slug:
        print(f"[INFO] CEREBRO_ARTICLE_SLUG não definido — pulando overview update")
        return

    referencia = (
        f"\n- [[wiki/articles/{slug}.md|{title}]] — compilado {HOJE}. "
        f"Fonte raw: `raw/sources/videos/{slug}__raw_transcript.md`."
    )

    if "Artigos compilados" not in conteudo:
        conteudo = conteudo.rstrip() + f"\n\n## Artigos compilados\n\n{referencia}\n"
        print(f"[OK] overview.md: seção Artigos compilados criada")
    elif referencia.strip() not in conteudo:
        # Adiciona no início da seção ou cria se não existir
        if re.search(r"^##\s+Artigos compilados\s*\n", conteudo, re.MULTILINE):
            conteudo = re.sub(
                r"(##\s+Artigos compilados\s*\n)",
                r"\1" + referencia + "\n",
                conteudo,
                count=1,
                flags=re.MULTILINE
            )
        else:
            conteudo = conteudo.rstrip() + f"\n\n## Artigos compilados\n\n{referencia}\n"
        print(f"[OK] overview.md: entrada adicionada")
    else:
        print(f"[INFO] overview.md: entrada já existe — não duplicando")

    overview_path.write_text(conteudo, encoding="utf-8")


def atualizar_log(slug: str):
    """Registra a ingestão no wiki/log.md."""
    log_path = VAULT_PATH / "wiki" / "log.md"

    log_dir = log_path.parent
    log_dir.mkdir(parents=True, exist_ok=True)

    if log_path.exists():
        conteudo = log_path.read_text(encoding="utf-8")
    else:
        conteudo = "# Log de Ingestão do Cerebro\n\n"

    entrada = (
        f"\n## [{HOJE}] ingest | Artigo — {slug_to_title(slug)}\n\n"
        f"- slug: `{slug}`\n"
        f"- raw: `raw/sources/videos/{slug}__raw_transcript.md`\n"
        f"- wiki: `wiki/articles/{slug}.md`\n"
        f"- status: compilado\n"
    )

    if f"[{HOJE}] ingest" in conteudo and slug in conteudo:
        print(f"[INFO] Log já contém entrada para hoje e slug {slug} — não duplicando")
        return

    # Insere no início (logo após o título) ou no final
    if conteudo.count("\n## [") == 0:
        conteudo = conteudo.rstrip() + entrada + "\n"
    else:
        # Insere logo após o header principal
        conteudo = re.sub(
            r"^(# Log de Ingestão do Cerebro\s*\n\n)",
            r"\1" + entrada,
            conteudo,
            count=1,
            flags=re.MULTILINE
        )

    log_path.write_text(conteudo, encoding="utf-8")
    print(f"[OK] log.md atualizado")


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    roteiro_path = Path(sys.argv[1])
    transcricao_path = Path(sys.argv[2])
    slug = sanitize_slug(sys.argv[3])

    os.environ["CEREBRO_ARTICLE_SLUG"] = slug

    if not roteiro_path.exists():
        print(f"[ERRO] Roteiro não encontrado: {roteiro_path}")
        sys.exit(1)
    if not transcricao_path.exists():
        print(f"[ERRO] Transcrição não encontrada: {transcricao_path}")
        sys.exit(1)

    print(f"=== Salvando no Cerebro: {slug_to_title(slug)} ===")
    print(f"  Roteiro: {roteiro_path}")
    print(f"  Transcrição: {transcricao_path}")
    print(f"  Slug: {slug}")
    print()

    salvar_raw_transcricao(transcricao_path, slug)
    salvar_wiki_artigo(roteiro_path, slug)
    atualizar_index()
    atualizar_overview()
    atualizar_log(slug)

    print()
    print(f"=== Concluído ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
