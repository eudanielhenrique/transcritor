---
name: schema-exemplo
description: Esquema mínimo de schema.md para um vault reorganizado no padrão LLM Knowledge Base.
---

# Exemplo de schema.md

Este é um esquema mínimo do `schema.md` para um vault reorganizado no padrão LLM Knowledge Base.

## Visão geral das camadas

- **raw/** — fontes imutáveis (projetos, vídeos, documentos). Não editar diretamente; o LLM referencia mas não modifica.
- **wiki/** — conhecimento compilado pelo LLM. Markdown em estrutura de diretórios, com backlinks, sumários, categorização de conceitos. Humano intervém apenas em curadoria e perguntas boas.
- **schema.md** — este arquivo. Define como a wiki funciona.

## Frontmatter padrão

### Todos os tipos

```yaml
---
tags: [wiki, <tipo>, ...outras tags]
criado: YYYY-MM-DD
updated: YYYY-MM-DD
source: compiled
tipo: <entity|concept|project-view|log|index>
---
```

### Entity

```yaml
---
tags: [wiki, entity, produto|cliente|agente|empresa, ...]
criado: YYYY-MM-DD
updated: YYYY-MM-DD
source: compiled
tipo: entity
---

# Nome da Entidade

> Descrição breve da entidade.

## Fontes

- raw/projects/<projeto>/arquivo.md

## Relações

- [[wiki/entities/outra-entidade.md]]

## Status

- status: novo
```

### Concept

```yaml
---
tags: [wiki, concept, ...]
criado: YYYY-MM-DD
updated: YYYY-MM-DD
source: compiled
tipo: concept
---

# Nome do Conceito

> Definição do conceito.

## Fontes

- raw/projects/<projeto>/arquivo.md

## Exemplos

- _A ser adicionado pelo LLM._

## Status

- status: novo
```

### Project-view

```yaml
---
tags: [wiki, project-view, <slug>]
criado: YYYY-MM-DD
updated: YYYY-MM-DD
source: compiled
raw_sources:
  - raw/projects/<slug>/arquivo1.md
  - raw/projects/<slug>/arquivo2.md
tipo: project-view
---

# Projeto — Visão Geral Compilada

> Esta página é uma compilação automática dos arquivos raw do projeto. Para editar, modifique os arquivos em raw/projects/<slug>/.

## Visão Geral

## Arquitetura e Stack

## Funcionalidades

## Roadmap

## Decisões e Armadilhas

## Status

Veja também [[wiki/index.md]] para o índice geral.
```

### Log

```yaml
---
tags: [wiki, log]
criado: YYYY-MM-DD
updated: YYYY-MM-DD
source: compiled
tipo: log
---

# Log do Cerebro

> Registro cronológico de tudo que acontece no Cerebro. Cada entrada começa com prefixo parseável.

## [YYYY-MM-DD] descrição

- item 1
- item 2
```

### Index

```yaml
---
tags: [wiki, index]
criado: YYYY-MM-DD
updated: YYYY-MM-DD
source: compiled
tipo: index
---

# Índice do Cerebro

> Catálogo de tudo no Cerebro. Atualizado automaticamente a cada ingest, query ou lint.

## Visão Geral

- [[wiki/overview.md|Visão Geral]]

## Entidades

- [[wiki/entities/entidade1.md|Entidade 1]]
- [[wiki/entities/entidade2.md|Entidade 2]]

## Conceitos

- [[wiki/concepts/conceito1.md|Conceito 1]]
- [[wiki/concepts/conceito2.md|Conceito 2]]

## Projetos

- [[wiki/projects/projeto1.md|Projeto 1]]
- [[wiki/projects/projeto2.md|Projeto 2]]

## Log

- [[wiki/log.md|Log de atividades]]
```

## Regras de ingest

Quando o LLM recebe novo conteúdo para indexar:

1. **Salvar fonte raw:** Colocar o arquivo original em `raw/projects/<projeto>/` (ou `raw/videos/campanhas/` para vídeos, ou `raw/notes/` para documentos soltos).
2. **Compilar wiki:** Criar ou atualizar páginas em `wiki/` com base na fonte raw.
3. **Atualizar index.md:** Adicionar entradas para novas entidades, conceitos ou projetos.
4. **Atualizar log.md:** Adicionar entrada com data, o que foi indexado e de onde veio.

## Regras de lint

Periodicamente, o LLM deve rodar lint para:

- Encontrar dados inconsistentes entre entidades e fontes raw.
- Identificar páginas órfãs (wiki sem links entrantes).
- Sugerir novas páginas ou conexões.
- Verificar se há fontes raw sem compilação correspondente em wiki/.

## Limitações

- Escala: funciona bem até ~100 fontes / ~400K palavras. Acima disso, precisa de busca/chunking.
- Controle: LLM escreve quase tudo — frontmatter e log ajudam mas não eliminam risco de alucinação. Human in the loop periódico recomendado.
- Imagens: LLM não lê markdown com imagens inline em passada única — ler texto primeiro, visualizar imagens separadamente.
