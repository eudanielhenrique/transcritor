# Contributing to Transcritor AI

Thank you for considering contributing to Transcritor AI! This project is open source and built for the autonomous AI agent ecosystem.

## How to Get Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/transcritor.git
   cd transcritor
   ```
3. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/my-feature
   ```
4. **Make your changes** and commit:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```
5. **Push** to your fork:
   ```bash
   git push origin feature/my-feature
   ```
6. **Open a Pull Request** on GitHub.

## What to Contribute

- Enhancements to the multimodal pipeline (`yt-dlp`, transcript extractors, audio processors).
- New content output formats (Twitter threads, LinkedIn articles, Substack newsletters).
- Improvements to agent prompt engineering (`runtime/SOUL.md`).
- Bug fixes, container performance optimizations, and documentation improvements.

## Code Style & Standards

- Follow clean Python code standards (PEP 8).
- Ensure Docker builds pass without regression (`docker compose build`).
- Keep agent personas and execution rules modular.
