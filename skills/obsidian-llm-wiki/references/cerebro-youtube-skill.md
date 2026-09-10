# Skill: cerebro-youtube

> **Refundido para `obsidian-llm-wiki`**. Este skill é um subconjunto do pipeline descrito em `references/transcricao-videos.md`. Para transcrever e indexar vídeos no Cerebro, use o skill `obsidian-llm-wiki` e seguir o pipeline descrito lá. Não criar skill separado para cada pipeline de transcrição — usar o skill de classe existente.

## Quando usar (se este skill estiver ativo)

Use apenas se o vault não estiver sob o padrão `obsidian-llm-wiki` e for necessário um skill específico para transcrição de vídeo. Caso contrário, usar `obsidian-llm-wiki` com `references/transcricao-videos.md`.

## Pipeline rápido

Assumindo que `obsidian-llm-wiki` está disponível:

```bash
# Baixar + transcrever + roteiro + salvar no Cerebro (tudo em um comando)
python transcreve3.py "E:/Temp/videos/<slug>_16k.wav" "E:/Temp/transcricoes/"
python roteiro.py      "E:/Temp/transcricoes/transcricao_<slug>.md"
python wiki.py         "E:/Temp/transcricoes/roteiro_<slug>.md" \
                      "E:/Temp/transcricoes/transcricao_<slug>.md" "<slug>"
```

Ou usar o script completo:
```bash
# Linux/macOS
./transcreve.sh "https://www.youtube.com/watch?v=<ID>"

# Windows
transcreve.bat "https://www.youtube.com/watch?v=<ID>"
```

## Qual versão do script usar

- **`transcreve3.py`** — versão CORRETA e robusta. Usa `wave` module para ler/escrever WAVs, não offsets fixos. Use esta.
- **`transcreve.py`** — version depreciada. Usa offsets fixos de 44 bytes; falha com WAVs que têm chunks LIST/INFO entre fmt e data (gera chunks de 26 bytes = silêncio puro).
- **`transcreve2.py`** — alternativa, lê manualmente mas com bug de sample_rate (lê offset errado do fmt chunk). Não usar.

Regra: sempre que criar ou modificar um script de chunk transcription, testar com o wave module primeiro. Nunca assumir que o cabeçalho WAV tem exatamente 44 bytes antes do data.
