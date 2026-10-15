<#
.SYNOPSIS
    Automated Local AI Training, Ollama Pipeline, and Project Expansion Runner.
.DESCRIPTION
    Checks Ollama server status, extracts knowledge from G:\My Drive\Antigravity\Projects,
    updates custom Ollama models, triggers automated brainstorming for income/views/gaming/tech,
    and commits progress to Git.
#>

$ErrorActionPreference = "Continue"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " [How to train your AI] Local Ollama & Multi-Project Engine" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Ensure Ollama is running
$ollamaPort = 11434
$portCheck = Test-NetConnection -ComputerName 127.0.0.1 -Port $ollamaPort -InformationLevel Quiet -WarningAction SilentlyContinue

if (-not $portCheck) {
    Write-Host "[*] Ollama server is not running. Launching background daemon..." -ForegroundColor Yellow
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 4
} else {
    Write-Host "[+] Ollama server is active on port $ollamaPort." -ForegroundColor Green
}

# 2. Extract knowledge and rebuild datasets
$pythonExe = "C:\Users\chase\AppData\Local\Programs\Python\Python312\python.exe"
if (Test-Path $pythonExe) {
    Write-Host "[*] Scanning all 38+ projects and building training datasets..." -ForegroundColor Yellow
    & $pythonExe "extract_project_knowledge.py"
} else {
    Write-Host "[!] Python 3.12 executable not found at $pythonExe" -ForegroundColor Red
}

# 3. Refresh custom Ollama models
Write-Host "[*] Updating custom Ollama models..." -ForegroundColor Yellow
ollama create project-forge -f Modelfile.forge
ollama create dev-deepseek -f Modelfile.deepseek_dev

# 4. Prompt Ollama to generate fresh initiatives for Income, Views, Tech Expansion, and Game Development
Write-Host "[*] Querying local Ollama model (project-forge) for today's high-impact objectives..." -ForegroundColor Yellow
$promptBody = @{
    model = "project-forge"
    prompt = "Generate 1 killer monetization idea, 1 viral YouTube/short-form content concept for gaming, and 1 high-leverage technical expansion for our indie game studio. Format clearly with actionable steps."
    stream = $false
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/generate" -Method Post -Body $promptBody -ContentType "application/json" -TimeoutSec 300
    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
    $outputFile = "daily_initiatives_$timestamp.md"
    Set-Content -Path $outputFile -Value $response.response
    Write-Host "[+] Saved daily initiatives to $outputFile" -ForegroundColor Green
} catch {
    Write-Host "[!] Could not query Ollama generate endpoint: $_" -ForegroundColor Yellow
}

# 5. Git Snapshot
$gitExe = "C:\Users\chase\AppData\Local\PortableGit\cmd\git.exe"
if (Test-Path $gitExe) {
    Write-Host "[*] Staging and committing changes to Git..." -ForegroundColor Yellow
    & $gitExe add -A
    & $gitExe commit -m "Auto-train update: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " [*] Daily Training and AI Evolution Complete!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
