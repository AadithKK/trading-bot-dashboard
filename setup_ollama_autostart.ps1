# Create a task to start Ollama automatically at startup
$trigger = New-ScheduledTaskTrigger -AtStartup
$action = New-ScheduledTaskAction -Execute "ollama" -Argument "serve"
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable

# Remove old task if exists
try {
    Unregister-ScheduledTask -TaskName "Ollama Auto-Start" -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

# Create task
Register-ScheduledTask -TaskName "Ollama Auto-Start" `
  -Trigger $trigger `
  -Action $action `
  -Settings $settings `
  -Description "Starts Ollama server automatically at boot" `
  -Force

Write-Host "Ollama Auto-Start task created!"
Write-Host ""
Get-ScheduledTask -TaskName "Ollama Auto-Start" | Select-Object TaskName, State, Triggers
