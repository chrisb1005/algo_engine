# Kill all running agent_service processes
Get-Process python | Where-Object { $_.Path -like "*python*" } | ForEach-Object {
    $processId = $_.Id
    $commandLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $processId").CommandLine
    if ($commandLine -like "*agent_service.py*") {
        Write-Host "Killing agent_service process (PID: $processId)" -ForegroundColor Yellow
        Stop-Process -Id $processId -Force
    }
}

Write-Host "`n✅ All agent_service processes killed" -ForegroundColor Green
Write-Host "`n📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Open Streamlit app" -ForegroundColor White
Write-Host "2. Load your portfolio from cloud" -ForegroundColor White
Write-Host "3. Click 'Sync to Cloud' to save agent config" -ForegroundColor White
Write-Host "4. Run: python agent_service.py your_portfolio_name" -ForegroundColor White
