#!/usr/bin/env python3
"""
Transcreve um arquivo de áudio WAV usando a API Flask local.
Divide o áudio em chunks e transcreve cada um separadamente.

Uso:
    python transcreve.py <caminho_do_arquivo_wav> [output_dir]

Exemplo:
    python transcreve.py "E:/Temp/videos/transcrever_youtube_16k.wav"
"""

import json
import os
import shutil
import sys
import time
from pathlib import Path

import requests

# Configuração padrão — pode ser sobrescrita por variáveis de ambiente
API_URL = os.environ.get("TRANSCRIVE_API_URL", "http://localhost:5000/transcrever")
CHUNK_SEC = int(os.environ.get("TRANSCRIVE_CHUNK_SEC", "30"))
TEMP_DIR = Path(os.environ.get("TRANSCRIVE_TEMP_DIR", "E:/Temp/videos"))
OUTPUT_DIR = Path(os.environ.get("TRANSCRIVE_OUTPUT_DIR", "E:/Temp/transcricoes"))

# Cabeçalho padrão do arquivo WAV
WAVE_HEADER_SIZE = 44


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    wav_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT_DIR

    if not wav_path.exists():
        print(f"[ERRO] Arquivo não encontrado: {wav_path}")
        sys.exit(1)

    # Garante diretórios
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Lê metadados do WAV — varre os chunks para achar o "data"
    print(f"[INFO] Lendo metadados: {wav_path}")
    with open(wav_path, "rb") as f:
        if f.read(4) != b"RIFF":
            print("[ERRO] Arquivo WAV inválido (sem RIFF)")
            sys.exit(1)
        # pula 4 bytes do tamanho do arquivo RIFF
        f.seek(4, 1)
        if f.read(4) != b"WAVE":
            print("[ERRO] Arquivo WAV inválido (sem WAVE)")
            sys.exit(1)

        num_channels = None
        sample_rate = None
        bits_per_sample = None
        data_size = None
        data_offset = None

        while True:
            chunk_id = f.read(4)
            if len(chunk_id) < 4:
                break
            chunk_size = int.from_bytes(f.read(4), "little")
            if chunk_id == b"fmt ":
                fmt_data = f.read(chunk_size)
                num_channels = int.from_bytes(fmt_data[0:2], "little")
                sample_rate = int.from_bytes(fmt_data[2:6], "little")
                bits_per_sample = int.from_bytes(fmt_data[14:16], "little")
                print(f"[INFO] Canal: {num_channels}, Taxa: {sample_rate}Hz, Bits: {bits_per_sample}")
            elif chunk_id == b"data":
                data_size = chunk_size
                data_offset = f.tell()
                break  # achou os dados, sai do loop
            else:
                f.seek(chunk_size, 1)  # pula chunks desconhecidos (LIST, INFO, etc.)

    if num_channels is None or sample_rate is None or data_size is None:
        print("[ERRO] Não conseguiu ler metadados do WAV")
        sys.exit(1)

    print(f"[INFO] Tamanho dos dados: {data_size:,} bytes (offset: {data_offset})")

    bytes_per_sample = num_channels * bits_per_sample // 8
    bytes_per_sec = sample_rate * bytes_per_sample
    chunk_bytes = CHUNK_SEC * bytes_per_sample
    total_chunks = (data_size + chunk_bytes - 1) // chunk_bytes

    print(f"[INFO] Duração estimada: {data_size / bytes_per_sec:.1f}s ({data_size / bytes_per_sec / 60:.1f}min)")
    print(f"[INFO] Divisão em {total_chunks} chunks de ~{CHUNK_SEC}s ({chunk_bytes:,} bytes cada)")

    # Lê todo o áudio a partir do offset correto
    print(f"[INFO] Lendo áudio completo ({data_size / 1024 / 1024:.1f}MB)...")
    with open(wav_path, "rb") as f:
        f.seek(data_offset)
        raw_audio = f.read(data_size)

    # Cria chunks temporários
    chunk_dir = TEMP_DIR / f"chunks_{int(time.time())}"
    chunk_dir.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Chunks temporários: {chunk_dir}")

    chunks = []
    for i in range(total_chunks):
        inicio = i * chunk_bytes
        fim = min((i + 1) * chunk_bytes, data_size)
        chunk_data = raw_audio[inicio:fim]

        chunk_path = chunk_dir / f"chunk_{i:04d}.wav"
        with open(chunk_path, "wb") as f:
            # Escreve cabeçalho WAV mínimo
            f.write(b"RIFF")
            f.write((36 + len(chunk_data)).to_bytes(4, "little"))
            f.write(b"WAVE")
            f.write(b"fmt ")
            f.write((16).to_bytes(4, "little"))  # tamanho do formato
            f.write((1).to_bytes(2, "little"))  # PCM
            f.write((num_channels).to_bytes(2, "little"))
            f.write((sample_rate).to_bytes(4, "little"))
            f.write((sample_rate * bytes_per_sample).to_bytes(4, "little"))  # byte rate
            f.write((bytes_per_sample).to_bytes(2, "little"))  # block align
            f.write((bits_per_sample).to_bytes(2, "little"))
            f.write(b"data")
            f.write((len(chunk_data)).to_bytes(4, "little"))
            f.write(chunk_data)

        chunks.append(chunk_path)
        print(f"[INFO] Chunk {i+1}/{total_chunks}: {chunk_path.name} ({len(chunk_data):,} bytes)")

    # Transcreve cada chunk
    print(f"\n[INFO] Iniciando transcrição de {len(chunks)} chunks...")
    transcricoes = []
    sucesso = 0
    falhas = []

    for i, chunk_path in enumerate(chunks):
        idx = int(chunk_path.stem.split("_")[1])
        chunk_size_mb = chunk_path.stat().st_size / (1024 * 1024)
        print(f"\n[{i+1}/{len(chunks)}] {chunk_path.name} ({chunk_size_mb:.2f}MB) ", end="", flush=True)

        texto = None
        for tentativa in range(3):
            try:
                with open(chunk_path, "rb") as fh:
                    r = requests.post(
                        API_URL,
                        files={"audio": (chunk_path.name, fh, "audio/wav")},
                        timeout=180,
                    )

                if r.status_code == 200:
                    try:
                        data = r.json()
                        texto = data.get("transcricao", "").strip()
                        if not texto:
                            texto = r.text.strip()
                    except json.JSONDecodeError:
                        texto = r.text.strip()

                    if texto:
                        sucesso += 1
                        print(f"OK → {len(texto)} chars", end=" ", flush=True)
                        break
                    else:
                        print(f"vazio, retry... ({tentativa+1}/3)", end=" ", flush=True)
                else:
                    print(f"HTTP {r.status_code} ({tentativa+1}/3)", end=" ", flush=True)
            except requests.exceptions.Timeout:
                print(f"timeout ({tentativa+1}/3)", end=" ", flush=True)
            except Exception as e:
                print(f"erro: {type(e).__name__} ({tentativa+1}/3)", end=" ", flush=True)

            if tentativa < 2:
                time.sleep(3)

        if texto is None or not texto:
            falhas.append(idx)
            texto = f"[erro de transcricao — chunk {idx}]"
            print("FALHOU", flush=True)
        else:
            print(f"| {texto[:100]}...", flush=True)

        transcricoes.append(texto)

        # Limpa chunks antigos para liberar espaço
        if i >= 5:
            limite = i - 5
            for f in sorted(chunk_dir.glob("chunk_*.wav"), key=lambda p: int(p.stem.split("_")[1])):
                try:
                    file_idx = int(f.stem.split("_")[1])
                    if file_idx <= limite:
                        f.unlink()
                except (ValueError, OSError):
                    pass

    # Salva transcrição completa
    slug = wav_path.stem.replace(" ", "_").replace("-", "_").lower()
    output_file = output_dir / f"transcricao_{slug}.md"

    # Monta conteúdo Markdown
    conteudo = f"""---
transcricao_de: {wav_path.name}
data: {time.strftime("%Y-%m-%d")}
total_chunks: {total_chunks}
sucesso: {sucesso}
falhas: {len(falhas)}
caracteres: {sum(len(t) for t in transcricoes)}
---

# Transcrição

{chr(10).join(transcricoes)}
"""
    output_file.write_text(conteudo, encoding="utf-8")

    print(f"\n{'=' * 60}")
    print(f"[OK] Transcrição salva: {output_file}")
    print(f"[INFO] Total de chunks: {total_chunks}")
    print(f"[INFO] Sucesso: {sucesso}/{total_chunks}")
    print(f"[INFO] Falhas: {len(falhas)} (indices: {falhas})")
    print(f"[INFO] Caracteres totais: {sum(len(t) for t in transcricoes):,}")
    print(f"{'=' * 60}")

    # Limpa chunks temporários
    shutil.rmtree(chunk_dir, ignore_errors=True)
    print(f"[INFO] Limpeza: {chunk_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
