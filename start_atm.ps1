Write-Host "Starting Mesh..."

# Set the project root directory as the Python Path search root
$env:PYTHONPATH = "."

$env:DATABASE_URL = "sqlite:///atm_logs.db"
$env:OLLAMA_URL = "http://localhost:11434/api/generate"
$env:LLM_MODEL_NAME = "tinydolphin"

# 1. Start FastAPI Core
Start-Process powershell -ArgumentList "-NoExit", "-Command", "uvicorn app.main:app --reload --port 8000"
Start-Sleep -Seconds 2

# 2. Start Streamlit UI
Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run dashboard/ui.py"
Start-Sleep -Seconds 2

# 3. Handle Ollama Layer
$ollamaCheck = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
if ($ollamaCheck) {
    Write-Host "Ollama is already running."
} else {
    Start-Process ollama -ArgumentList "serve"
}

Write-Host "All processes triggered successfully."