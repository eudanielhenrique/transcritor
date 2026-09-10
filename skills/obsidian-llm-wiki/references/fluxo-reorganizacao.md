---
name: fluxo-reorganizacao
description: Fluxo passo a passo para reorganizar um vault Obsidian no padrão LLM Knowledge Base.
---

# Fluxo de Reorganização de Vault Obsidian para LLM Wiki

## Passo 1: Mapear o vault atual

- Listar todos os arquivos e diretórios no root do vault.
- Ler o índice existente (ex: `00 - Índice.md`) e anotar projetos ativos e organização atual.
- Ler os frontmatters dos principais projetos para preservar metadados.
- Identificar arquivos soltos (canvas, markdown fora de pasta).
- Identificar onde estão as transcrições/roteiros de vídeo.

## Passo 2: Decidir estrutura de slugs e agrupamentos

- Para cada projeto, escolher um slug (lower-case, hífens, sem acentos, único).
- Decidir onde vídeos/transcrições vão (dentro do projeto ou agrupados globalmente).
- Decidir onde arquivos soltos vão (`raw/notes/`).
- Decidir onde assets vão (`raw/assets/`).

## Passo 3: Criar estrutura de diretórios

Criar diretórios:

```
<vault>/
├── raw/
│   ├── projects/
│   ├── videos/
│   ├── notes/
│   └── assets/
└── wiki/
    ├── entities/
    ├── concepts/
    ├── comparisons/
    ├── projects/
    ├── overview.md
    ├── index.md
    └── log.md
```

## Passo 4: Migrar projetos para raw/projects/

- Mover pasta inteira de cada projeto para `raw/projects/<slug>/`.
- Usar Python `shutil.move` em vez de `mv` shell em Windows com iCloud.
- Se `raw/projects/<slug>/` já existe, verificar duplicata e resolver.

## Passo 5: Migrar arquivos soltos

- Canvas e markdown soltos vão para `raw/notes/`.

## Passo 6: Migrar vídeos/transcrições

- Mover pasta de campanhas para `raw/projects/<projeto>/videos/campanhas/` ou `raw/videos/campanhas/`.

## Passo 7: Criar schema.md

- Visão geral das três camadas.
- Frontmatter padrão para cada tipo de página.
- Regras de ingest, query e lint.

Ver `references/schema-exemplo.md`.

## Passo 8: Bootstrapping da wiki inicial

1. Criar `wiki/overview.md`.
2. Criar `wiki/index.md`.
3. Criar `wiki/log.md`.
4. Criar `wiki/entities/<slug>.md` para cada entidade.
5. Criar `wiki/concepts/<slug>.md` para cada conceito.
6. Criar `wiki/projects/<slug>.md` com visão compilada.

## Passo 9: Validar e limpar

- Verificar migração de todos os projetos.
- Verificar arquivos soltos remanescentes.
- Verificar consistência das páginas wiki.
- Remover duplicatas no root se houve.

## Passo 10: Criar skill Hermes para ingest futura

- Criar skill que carregue o `schema.md` e saiba como operar a wiki.
- Atualizar `wiki/index.md` e `wiki/log.md` a cada ingest.
