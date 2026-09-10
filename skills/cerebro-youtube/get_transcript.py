#!/usr/bin/env python3
"""
Extrai transcrição e título de um vídeo do YouTube ou arquivo de áudio.
Uso:
    python3 get_transcript.py "<URL_YOUTUBE_OU_ARQUIVO_AUDIO>" [output_path]
"""

import os
import re
import sys
from pathlib import Path

def extract_video_id(url: str) -> str | None:
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:shorts\/)([0-9A-Za-z_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_title(url_or_id: str) -> str:
    import subprocess
    try:
        res = subprocess.run(
            ["yt-dlp", "--skip-download", "--print", "%(title)s", url_or_id],
            capture_output=True, text=True, timeout=15
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return "Transcrição de Conteúdo"

def get_transcript_api(video_id: str) -> str | None:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id, languages=['pt', 'pt-BR', 'pt-orig', 'en', 'es']
        )
        return " ".join(item['text'] for item in transcript_list)
    except Exception:
        return None

def get_transcript_ytdlp(url: str) -> str | None:
    import subprocess, tempfile, glob
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            cmd = [
                "yt-dlp",
                "--extractor-args", "youtube:player_client=android,web",
                "--write-auto-sub", "--write-sub",
                "--sub-lang", "pt,pt-orig,pt-BR,en",
                "--skip-download",
                "--sub-format", "vtt",
                "-o", f"{tmpdir}/%(id)s.%(ext)s",
                url
            ]
            subprocess.run(cmd, capture_output=True, timeout=30)
            vtts = glob.glob(f"{tmpdir}/*.vtt")
            if not vtts:
                return None
            
            with open(vtts[0], "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            pattern = r"(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})[^\n]*\n([\s\S]*?)(?=\n\d{2}:\d{2}:\d{2}\.\d{3}|\Z)"
            cues = re.findall(pattern, content)
            cleaned = []
            for _, _, text in cues:
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                if lines:
                    newest = re.sub(r"<[^>]+>", "", lines[-1]).strip()
                    if newest:
                        cleaned.append(newest)
            
            final_lines = []
            last = ""
            for t in cleaned:
                if t == last: continue
                if last and t.startswith(last):
                    final_lines[-1] = t
                    last = t
                    continue
                final_lines.append(t)
                last = t
            return " ".join(final_lines)
        except Exception:
            return None

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 get_transcript.py <URL_OU_ARQUIVO>")
        sys.exit(1)

    target = sys.argv[1].strip()
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    video_id = extract_video_id(target)
    if not video_id:
        print(f"[ERRO] Não foi possível extrair ID do vídeo: {target}")
        sys.exit(1)

    title = get_title(target)
    print(f"TITULO: {title}")

    text = get_transcript_api(video_id)
    if not text:
        text = get_transcript_ytdlp(target)

    if not text:
        print("[ERRO] Não foi possível obter a transcrição automática do YouTube.")
        sys.exit(1)

    print(f"\n--- INICIO TRANSCRICAO ({len(text)} caracteres) ---")
    print(text)
    print("--- FIM TRANSCRICAO ---\n")

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n{text}\n")
        print(f"Salvo em: {output_path}")

if __name__ == "__main__":
    main()
