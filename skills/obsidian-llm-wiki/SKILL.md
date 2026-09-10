---
name: obsidian-llm-wiki
description: Reorganiza vault Obsidian no padrão LLM Knowledge Base.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Obsidian, Wiki, LLM, Knowledge Base, Reorganization]
    related_skills: [obsidian]
---

# Obsidian LLM Wiki — Reorganização de Vault

Use este skill quando o objetivo for transformar um vault Obsidian existente (projetos espalhados, transcrições, roteiros, notas soltas) no padrão de *LLM Knowledge Base* descrito em `llm-wiki.md` / `karpathytt.md`: duas camadas (`raw/` imutável e `wiki/` compilada pelo LLM), mais um `schema.md` que ensina ao agente como operar a wiki.

**Projeto associado:** BoraAutomatizar — Cerebro (vault Obsidian em `C:\Users\ddani\iCloudDrive\iCloud~md~obsidian\Cerebro`).

Diferente do skill `obsidian` genérico (que lida com leitura/busca/criação de notas no vault atual), este skill trata da **reorganização estrutural** e do **bootstrapping do esquema** que a wiki vai seguir.

## Quando usar

- Usuário pede para "reorganizar o cerebro todo no estilo wiki sem perder nada".
- Usuário quer um agente Hermes que, ao receber "indexa isso aqui", saiba onde colocar, como compilar, como atualizar índice e log.
- Existe um vault com projetos, transcrições de vídeo, roteiros, canvas soltos, índice cronológico — e a intenção é ter uma camada wiki mantida por LLM a partir de fontes raw.

## O que não é este skill

- Não substitui `obsidian` para leitura/busca/criação pontual de notas.
- Não cobre o pipeline de transcrição de vídeo — isso é coberto por `references/transcricao-videos.md` e pelo skill `cerebro-youtube` (`references/cerebro-youtube-skill.md`).
- Não cobre criação de roteiros de vídeo em si (isso é `references/transcricao-videos.md`).

## Princípios do padrão wiki (resumo operacional)

- **raw/** — fonte imutável. Projeto, vídeo, artigo, nota técnica entram aqui e nunca são editados pelo LLM durante o ciclo de wiki. O LLM lê, referencia, compila — mas a fonte de verdade fica intacta.
- **wiki/** — saída compilada pelo LLM: markdown em estrutura de diretórios, com backlinks, sumários, categorização de conceitos, links entre entidades. O humano intervém apenas em curadoria e nas perguntas boas; raramente toca no markdown compilado.
- **schema.md** — o documento que ensina ao agente Hermes (e a qualquer LLM futuro) como a wiki funciona: estrutura de pastas, convenções de frontmatter, tipos de página, fluxo de ingest/query/lint, como atualizar índice e log. Sem ele, o agente não sabe o esquema.
- **.obsidian/** e convenções visuais (ex: `99 - Convenções Visuais.md`) são mantidos; não são afetados pela reorganização.

## Fluxo de reorganização (passo a passo)

### 0. Confirmar escopo e backups

- Entenda o que o usuário quer preservar.
- Se o vault é iCloud-sync ou outra sync, lembre-se dos travamentos de arquivo (ver *Pitfalls*).
- Opcional: snapshot do vault antes de mexer (copy recursiva externa).

### 1. Mapear o vault atual

Etapa obrigatória antes de mexer qualquer coisa.

- Listar todos os arquivos e diretórios no root do vault (use `search_files` com `target: "files"`, `pattern: "*"`, ou `find` em terminal).
- Ler o índice existente se houver um (ex: `00 - Índice.md`) e anotar projetos ativos e organização atual.
- Ler os frontmatters (tags, status, tipo) dos principais projetos para preservar metadados e servir de base para entidades wiki.
- Identificar arquivos soltos (canvas `.canvas`, markdown fora de pasta, etc.).
- Identificar onde estão as transcrições/roteiros de vídeo (ex: pasta `Campanhas/` dentro de um projeto).

### 2. Decidir estrutura de slugs e agrupamentos

Para cada projeto existente, escolher um *slug* (nome lower-case com hífens, sem acentos, único). Exemplo: `BoraAutomatizar` → `boraautomatizar`, `MaoNaObra` → `maonao-obra` (evitar espaços em slugs).

Decidir também:

- Vídeos/transcrições: vão para `raw/projects/<projeto>/videos/campanhas/` (se são parte do projeto) ou `raw/videos/campanhas/` (se forem independentes e agrupados globalmente).
- Arquivos soltos: vão para `raw/notes/`.
- Assets (imagens, etc.): vão para `raw/assets/`.

Anote essa decisão num documento temporário ou direto no `schema.md` final.

### 3. Criar estrutura de diretórios (se não existir)

Diretórios esperados no vault após reorganização:

```
<vault>/
├── .obsidian/          (mantido — não tocar)
├── 00 - Índice.md      (ou similar — mantido ou transformado em overview)
├── 99 - Convenções Visuais.md  (mantido)
├── schema.md           (NOVO — ver seção schema)
├── raw/
│   ├── projects/
│   │   ├── <slug-proj-1>/
│   │   ├── <slug-proj-2>/
│   │   └── ...
│   ├── videos/         (opcional, se não usar dentro de projects)
│   │   └── campanhas/
│   ├── notes/
│   └── assets/
└── wiki/
    ├── index.md
    ├── log.md
    ├── overview.md
    ├── entities/
    ├── concepts/
    ├── comparisons/
    └── projects/
```

Crie os diretórios com `mkdir -p` ou `pathlib.Path.mkdir(parents=True, exist_ok=True)` via Python.

### 4. Migrar projetos para raw/projects/

Para cada projeto do vault atual:

1. Se o projeto ainda está no root, mova a pasta inteira para `raw/projects/<slug>/`.
2. Se `raw/projects/<slug>/` já existe, verifique se é duplicata e resolva (normalmente a origem tem os arquivos originais e o destino pode estar vazio ou com versão compilada; decida com base no que o usuário quer preservar). O ideal é mover a origem e remover a duplicata no root **após** confirmar que a migração foi completa.
3. Use `shutil.move` via Python (pathlib) em vez de `mv` shell quando estiver em ambiente Windows com iCloud — ver *Pitfalls*.

Pendências toleráveis durante a migração:

- Se iCloud travar um arquivo, tente de novo após um momento ou usar Python. Em caso de falha persistente, registre o arquivo problemático e avance; o usuário pode resolver manualmente depois.

### 5. Migrar arquivos soltos

- Canvas e markdown soltos que não fazem parte de um projeto devem ir para `raw/notes/` (ou `raw/projects/<slug>/` se houver um projeto específico).
- Mantenha nomes descritivos.

### 6. Migrar vídeos/transcrições

Se o vault atual tem uma pasta como `BoraAutomatizar/Campanhas/` com roteiros/transcrições:

- Mova para `raw/projects/boraautomatizar/videos/campanhas/` (ou caminho equivalente decidido no passo 2).
- Ajuste os caminhos nas páginas wiki que referenciam esses arquivos.

### 7. Criar schema.md

O `schema.md` é o coração do padrão. Ele deve conter:

- Visão geral das três camadas (raw, wiki, schema) e quem faz o quê (LLM escreve wiki, humano curadoria e faz perguntas boas).
- Frontmatter padrão para cada tipo de página (ver `references/schema-exemplo.md`).
- Regras de como o LLM deve compilar uma visão de projeto: ler os arquivos raw, extrair funcionalidades, arquitetura, roadmap, decisões, e montar um markdown estruturado em `wiki/projects/<slug>.md`.
- Regras de ingest: onde cada tipo de fonte nova vai (ex: novo projeto → `raw/projects/<slug>/`, nova transcrição de vídeo → `raw/projects/<projeto>/videos/campanhas/<arquivo>.md`), como atualizar `index.md` e `log.md`, como manter as entidades e conceitos consistentes.
- Regras de query: como perguntar ao LLM sobre a wiki (ex: "o que a gente sabe sobre <produto>?"), o que esperar como resposta (síntese com fontes listadas).
- Regras de lint: o que verificar periodicamente (contradições entre entidades, páginas órfãs sem backlinks, gaps entre raw e wiki).

Ver `references/schema-exemplo.md` para um esquema mínimo explícito.

### 8. Bootstrapping da wiki inicial

Após a migração das fontes raw, compilar as primeiras páginas wiki usando o que existe. A ordem sugerida:

1. Criar `wiki/overview.md` — visão geral do vault, projetos ativos, como usar.
2. Criar `wiki/index.md` — catálogo de entidades, conceitos, projetos e campanhas de vídeo.
3. Criar `wiki/log.md` — registro inicial da criação da wiki e migração.
4. Criar `wiki/entities/<slug>.md` para cada entidade identificada (produto, cliente, agente, empresa).
5. Criar `wiki/concepts/<slug>.md` para cada conceito identificado.
6. Criar `wiki/projects/<slug>.md` com visão compilada de cada projeto.

Durante esse passo, o LLM (ou você, se estiver fazendo manualmente agora) deve:

- Ler os arquivos raw relevantes para cada página wiki.
- Extrair o essencial (visão geral, funcionalidades, arquitetura, decisões) para a página compilada.
- Listar as fontes raw no campo `raw_sources` ou seção `Fontes`.
- Usar wikilinks (`[[...]]`) entre páginas wiki quando fizer sentido.

### 9. Validar e limpar

- Verificar se todos os projetos foram migrados (listar `raw/projects/` e comparar com lista original).
- Verificar arquivos soltos remanescentes no root (devem estar em `raw/notes/` ou roteiros relevantes).
- Verificar se `wiki/index.md` e `wiki/overview.md` estão consistentes com o que foi migrado.
- Remover duplicatas no root se houve (com cuidado em ambientes iCloud).

### 10. Criar skill Hermes para ingest futura

Após a reorganização, criar um skill Hermes específico do vault (ex: `bora-wiki` em `~/AppData/Local/hermes/skills/bora-wiki/` ou similares) que:

- Carregue o `schema.md` (ou tenha uma cópia interna) para saber o esquema.
- Saiba para cada tipo de fonte nova onde depositar o raw e como compilar/atualizar a wiki.
- Atualize `wiki/index.md` e `wiki/log.md` a cada ingest.

Ver o skill já criado na sessão para referência de configuração.

## Frontmatter padrão (referência rápida)

### Todos os tipos

```yaml
---
tags: ["wiki", "<tipo>", ...outras tags]
criado: YYYY-MM-DD
updated: YYYY-MM-DD
source: compiled
tipo: <entity|concept|project-view|log|index>
---
```

### Entity

```yaml
---
tags: ["wiki", "entity", "produto"|"cliente"|"agente"|"empresa", ...outras tags]
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
tags: ["wiki", "concept", ...outras tags]
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
tags: ["wiki", "project-view", "<slug>"]
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
tags: ["wiki", "log"]
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
tags: ["wiki", "index"]
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

## Pitfalls

- **iCloud no Windows trava arquivos durante move/rename.** `mv` via shell pode falhar com "Device or resource busy" ou "Acesso negado". Trabalhe com Python `pathlib` + `shutil.move()` e, se necessário, feche o Obsidian antes de migrar. Se um arquivo persistir travado, avance e deixe um registro para o usuário resolver manualmente — não fique em loop tentando rename.
- **Não confundir o vault do Obsidian com o repo da API de transcrição.** O vault é o repositório de conhecimento (Markdown, canvas, etc.); a API de transcrição (Flask/gunicorn, `main.py`, `requirements.txt`) é um sistema separado. Migrações de conhecimento não devem mexer no repo da API.
- **Preservar todo conteúdo existente.** A reorganização não deve apagar nada — só mover e criar as camadas wiki. Se houver dúvida se um arquivo será apagado, verifique com o usuário antes.
- **Índice existente não deve ser apagado cegamente.** O `00 - Índice.md` (ou similar) pode ser transformado em `overview.md` ou mantido como distrito. Se for transformado, crie o `overview.md` primeiro e só então remova/renomeie o antigo.
- **Frontmatter existente deve ser respeitado e reutilizado.** Quando migrar arquivos, mantenha seus frontmatters originais; não os altere durante a migração. As novas páginas wiki têm o próprio frontmatter com `source: compiled` e `tipo:`.
- **Evitar loops de escrita/parche desnecessários.** Para criar páginas wiki que ainda não existem, use `write_file` direto com o conteúdo completo. Reserve `patch` para edições pontuais em páginas que já existem e que você já leu.
- **Não presumir que a estrutura do vault é a padrão antes de mapear.** Sempre faça o passo 1 (mapear) antes de decidir a estrutura de slugs e agrupamentos.

## Referências

- `references/schema-exemplo.md` — esquema mínimo do `schema.md` com frontmatters e regras.
- `references/fluxo-reorganizacao.md` — versão textual do fluxo passo a passo (espelha esta seção).
- `references/transcricao-videos.md` — pipeline completo para transcrever vídeos do YouTube, gerar roteiros e salvar no Cerebro.
- `references/cerebro-youtube-skill.md` — skill dedicado ao pipeline de transcrição de vídeo (consolidado sob este skill).
- Skill `obsidian` (`note-taking/obsidian`) — para leitura/busca/criação de notas no vault durante e após a reorganização.
