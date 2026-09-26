@echo off
cd /d "C:\Users\ALI HAIDER\OneDrive\Desktop\ANOMYMOUS"
python -m pytest tests\ -v
if %ERRORLEVEL% ne 0 (
    echo Tests failed. Check the output above.
    pause
) else (
    echo All tests passed successfully.
)