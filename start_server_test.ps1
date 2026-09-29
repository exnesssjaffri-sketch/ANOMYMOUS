$env:ANOMYMOUS_USE_MOCK = "1"
$proc = Start-Process -FilePath "python" -ArgumentList "server.py" -RedirectStandardOutput "server_test.log" -RedirectStandardError "server_test_err.log" -PassThru -NoNewWindow
Start-Sleep -Seconds 3
Write-Host "Process running: $($proc.ProcessId)"
Write-Host "--- stdout ---"
Get-Content "server_test.log" -ErrorAction SilentlyContinue
Write-Host "--- stderr ---"
Get-Content "server_test_err.log" -ErrorAction SilentlyContinue