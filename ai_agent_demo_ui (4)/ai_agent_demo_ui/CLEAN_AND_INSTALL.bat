@echo off
echo ========================================
echo Cleaning old dependencies...
echo ========================================
rmdir /s /q node_modules
del package-lock.json
echo.
echo ========================================
echo Installing fresh dependencies...
echo ========================================
call npm install
echo.
echo ========================================
echo Starting development server...
echo ========================================
call npm run dev
pause
