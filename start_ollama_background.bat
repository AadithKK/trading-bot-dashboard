@echo off
REM Start Ollama in background without showing window
start /B ollama serve
timeout /t 5
echo Ollama started in background
