@echo off
REM ============================================================
REM Pipeline completo: YouTube -> Transcrição -> Roteiro -> Cerebro
REM Para rodar no Windows (CMD ou PowerShell)
REM ============================================================
REM Uso:
REM   .\transcreve.bat "https://www.youtube.com/watch?v=-OxFis8Ulgg"
REM
REM Pré-requisitos:
REM   - Python 3.10+ (caminho configurável abaixo)
REM   - yt-dlp instalado (pip install yt-dlp)
REM   - ffmpeg na PATH ou caminho configurável
REM   - API Flask rodando em http://localhost:5000
REM     (endpoint POST /transcrever aceita WAV/OGG/MP3)
REM   - Acesso ao vault do Cerebro (iCloud)
REM ============================================================

setlocal enabledelayedexpansion

REM ============================================================
REM Configuração — editar conforme o ambiente de cada máquina
REM ============================================================

REM Caminho do Python (padrão: instalação local do usuário)
set PYTHON=C:\Users\ddani\AppData\Local\Programs\Python\Python312\python.exe

REM Caminho do ffmpeg (padrão: na PATH; se não estiver, especificar aqui)
set FFMPEG=ffmpeg

REM Caminho do yt-dlp (se não estiver na PATH, especificar aqui)
set YT_DLP=yt-dlp

REM URL da API Flask de transcrição
set API_URL=http://localhost:5000/transcrever

REM Tamanho dos chunks em segundos (Google SR gratuito ~1min limite)
set CHUNK_SEC=30

REM Diretórios temporários (onde baixar/converter áudio e salvar transcrições)
set TEMP_VIDEOS=E:\Temp\videos
set TEMP_TRANSCRICOES=E:\Temp\transcricoes

REM Caminho do vault do Cerebro (Obsidian / iCloud Drive)
set VAULT_PATH=C:\Users\ddani\iCloudDrive\iCloud~md~obsidian\Cerebro

REM Diretório do script (auto-detected) 
set SCRIPT_DIR=%~dp0

REM Verificar se foi passada uma URL
if "%~1"=="" (
    echo ============================================================
    echo Uso: .\transcreve.bat ^<URL_DO_VIDEO^>
    echo.
    echo Exemplo:
    echo   .\transcreve.bat "https://www.youtube.com/watch?v=-OxFis8Ulgg"
    echo ============================================================
    exit /b 1
)

set "VIDEO_URL=%~1"

REM ============================================================
REM Verificações iniciais
REM ============================================================

echo ============================================================
echo Pipeline: YouTube -› Transcrição -› Roteiro -› Cerebro
echo ============================================================
echo.
echo URL:          %VIDEO_URL%
echo Python:       %PYTHON%
echo ffmpeg:       %FFMPEG%
echo yt-dlp:       %YT_DLP%
echo API:          %API_URL%
echo Chunk:        %CHUNK_SEC%s
echo Temp vídeos:  %TEMP_VIDEOS%
echo Temp transcrições: %TEMP_TRANSCRICOES%
echo Vault:        %VAULT_PATH%
echo Script dir:   %SCRIPT_DIR%
echo.

REM Testar Python
where %PYTHON% >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python não encontrado em %PYTHON%
    echo        Instale Python 3.10+ e configure a variavel PYTHON no script.
    exit /b 1
)
echo [OK] Python: %PYTHON%

REM Testar yt-dlp
%YT_DLP% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] yt-dlp não encontrado. Tentando instalar via pip...
    %PYTHON% -m pip install yt-dlp --quiet
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao instalar yt-dlp.
        exit /b 1
    )
    echo [OK] yt-dlp instalado.
)

REM Testar ffmpeg
%FFMPEG% -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] ffmpeg nao encontrado na PATH.
    echo        Baixe em https://ffmpeg.org/download.html e adicione a PATH,
    echo        ou configure a variavel FFMPEG no inicio deste script.
)

REM Testar API Flask
echo -n "[INFO] Verificando API Flask em %API_URL%... "
curl -s -o nul -w "%{http_code}" "%API_URL%" >"%TEMP_VIDEOS%\http_code.tmp" 2>nul
set /p HTTP_CODE=<"%TEMP_VIDEOS%\http_code.tmp"
del "%TEMP_VIDEOS%\http_code.tmp"
if not "%HTTP_CODE%"=="200" (
    echo FALHA (HTTP %HTTP_CODE%). Inicie a API Flask antes de rodar.
    exit /b 1
)
echo OK

REM Criar diretorios temporarios
if not exist "%TEMP_VIDEOS%" mkdir "%TEMP_VIDEOS%"
if not exist "%TEMP_TRANSCRICOES%" mkdir "%TEMP_TRANSCRICOES%"

REM ============================================================
REM 1. Download do audio do YouTube
REM ============================================================

echo.
echo =============================================
echo Passo 1: Download do audio do YouTube
echo =============================================

REM Extrair ID do video
for /f "tokens=*" %%i in ('%YT_DLP% --print "%%(id)s" "%VIDEO_URL%" 2^>nul') do set "VIDEO_ID=%%i"

REM Extrair titulo
for /f "tokens=*" %%i in ('%YT_DLP% --print "%%(title)s" "%VIDEO_URL%" 2^>nul') do set "VIDEO_TITLE=%%i"

REM Sanitizar titulo para nome de arquivo
set "VIDEO_SLUG=%VIDEO_TITLE:"
set "VIDEO_SLUG=%VIDEO_SLUG: =_%
set "VIDEO_SLUG=%VIDEO_SLUG:&=and%
set "VIDEO_SLUG=%VIDEO_SLUG:/=_%
set "VIDEO_SLUG=%VIDEO_SLUG:?=_%
set "VIDEO_SLUG=%VIDEO_SLUG:<=_%
set "VIDEO_SLUG=%VIDEO_SLUG:>=_%
set "VIDEO_SLUG=%VIDEO_SLUG:|=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^<=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^>=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^*=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^?_%
set "VIDEO_SLUG=%VIDEO_SLUG:^,=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^;=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^:_=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^.=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^~=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^!=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^@=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^#=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^$=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^%=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^^=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^&=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^(=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^)=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^[=_%
set "VIDEO_SLUG=%VIDEO_SLUG:^]=_%"

set "WAV_OUTPUT=%TEMP_VIDEOS%\%VIDEO_SLUG%.wav"
set "WAV_16K=%TEMP_VIDEOS%\%VIDEO_SLUG%_16k.wav"

echo [INFO] ID do video: %VIDEO_ID%
echo [INFO] Titulo: %VIDEO_TITLE%
echo [INFO] Slug: %VIDEO_SLUG%
echo [INFO] WAV de saida: %WAV_OUTPUT%

if exist "%WAV_OUTPUT%" (
    echo [INFO] Arquivo WAV ja existe — pulando download
) else (
    echo [INFO] Baixando audio...
    %YT_DLP% ^
        --extract-audio ^
        --audio-format wav ^
        --audio-quality 0 ^
        --output "%WAV_OUTPUT%" ^
        "%VIDEO_URL%" 2>&1 | tail -5
)

if not exist "%WAV_OUTPUT%" (
    echo [ERRO] Falha ao baixar audio. Verifique a URL e a conexao.
    exit /b 1
)

for %%A in ("%WAV_OUTPUT%") do set "WAV_SIZE=%%~zA"
echo [OK] Audio baixado: %WAV_OUTPUT% (tamanho: %WAV_SIZE% bytes)

REM ============================================================
REM 2. Convertar para 16kHz mono
REM ============================================================

echo.
echo =============================================
echo Passo 2: Convertacao para 16kHz mono
echo =============================================

if exist "%WAV_16K%" (
    echo [INFO] Arquivo 16kHz ja existe — pulando conversao
) else (
    echo [INFO] Convertendo para 16kHz mono...
    %FFMPEG% -y -i "%WAV_OUTPUT%" -vn -acodec pcm_s16le -ar 16000 -ac 1 "%WAV_16K%" 2>&1 | tail -3
)

if not exist "%WAV_16K%" (
    echo [ERRO] Falha ao converter audio. Verifique se ffmpeg esta instalado.
    exit /b 1
)

for %%A in ("%WAV_16K%") do set "WAV_16K_SIZE=%%~zA"
echo [OK] Audio 16kHz: %WAV_16K% (tamanho: %WAV_16K_SIZE% bytes)

REM ============================================================
REM 3. Transcricao chunk por chunk
REM ============================================================

echo.
echo =============================================
echo Passo 3: Transcricao (chunk por chunk)
echo =============================================

set "TRANSCRIVE_API_URL=%API_URL%"
set "TRANSCRIVE_CHUNK_SEC=%CHUNK_SEC%"
set "TRANSCRIVE_TEMP_DIR=%TEMP_VIDEOS%"
set "TRANSCRIVE_OUTPUT_DIR=%TEMP_TRANSCRICOES%"

%PYTHON% "%SCRIPT_DIR%transcreve.py" "%WAV_16K%"

set "TRANSCRICAO_FILE=%TEMP_TRANSCRICOES%\transcricao_%VIDEO_SLUG%.md"

if not exist "%TRANSCRICAO_FILE%" (
    echo [ERRO] Transcricao nao foi gerada. Verifique os logs acima.
    exit /b 1
)

echo [OK] Transcricao concluida: %TRANSCRICAO_FILE%

REM ============================================================
REM 4. Geracao do roteiro
REM ============================================================

echo.
echo =============================================
echo Passo 4: Geracao do roteiro
echo =============================================

set "TRANSCRIVE_VIDEO_URL=%VIDEO_URL%"
set "TRANSCRIVE_VIDEO_TITLE=%VIDEO_TITLE%"
set "TRANSCRIVE_OUTPUT_DIR=%TEMP_TRANSCRICOES%"

%PYTHON% "%SCRIPT_DIR%roteiro.py" "%TRANSCRICAO_FILE%"

set "ROTEIRO_FILE=%TEMP_TRANSCRICOES%\roteiro_%VIDEO_SLUG%.md"

if not exist "%ROTEIRO_FILE%" (
    echo [AVISO] Roteiro nao foi gerado — verifique a transcricao
) else (
    echo [OK] Roteiro gerado: %ROTEIRO_FILE%
)

REM ============================================================
REM 5. Salvar no Cerebro (Obsidian vault)
REM ============================================================

echo.
echo =============================================
echo Passo 5: Salvando no Cerebro
echo =============================================

set "CEREBRO_VAULT_PATH=%VAULT_PATH%"
set "CEREBRO_ARTICLE_SLUG=%VIDEO_SLUG%"

%PYTHON% "%SCRIPT_DIR%wiki.py" "%ROTEIRO_FILE%" "%TRANSCRICAO_FILE%" "%VIDEO_SLUG%"

echo.
echo ============================================================
echo Pipeline concluido com sucesso!
echo ============================================================
echo.
echo Arquivos no Cerebro:
echo   Raw:  %VAULT_PATH%\raw\sources\videos\%VIDEO_SLUG%__raw_transcript.md
echo   Wiki: %VAULT_PATH%\wiki\articles\%VIDEO_SLUG%.md
echo.
echo Arquivos intermediarios (E:\Temp):
echo   Audio:       %WAV_16K%
echo   Transcricao: %TRANSCRICAO_FILE%
echo   Roteiro:     %ROTEIRO_FILE%
echo.

endlocal
