$botPath = "C:\Users\kanno\OneDrive\Desktop\Ai stuff for Ai\trading-bot-local"
$scriptPath = "$botPath\run_bot.bat"

$trigger = New-ScheduledTaskTrigger -Daily -At "08:20"
$action = New-ScheduledTaskAction -Execute $scriptPath
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable

# Remove old task if it exists
try {
    Unregister-ScheduledTask -TaskName "Trading Bot Daily" -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed old task"
} catch {}

# Create new task
Register-ScheduledTask -TaskName "Trading Bot Daily" `
  -Trigger $trigger `
  -Action $action `
  -Settings $settings `
  -Description "Runs trading bot daily at 8:20 AM" `
  -Force

Write-Host ""
Write-Host "Task created successfully!"
Write-Host ""
Get-ScheduledTask -TaskName "Trading Bot Daily" | Select-Object TaskName, State
