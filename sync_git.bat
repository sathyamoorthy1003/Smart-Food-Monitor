@echo off
echo Syncing changes to GitHub...

:: Add all changes
git add .

:: Commit with timestamp
set "timestamp=%date% %time%"
git commit -m "Auto-sync: %timestamp%"

:: Push to main
git push origin main

echo.
echo Sync complete!
pause
