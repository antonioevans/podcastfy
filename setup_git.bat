@echo off
setlocal EnableDelayedExpansion

:: Colors for Windows console
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "NC=[0m"

echo %YELLOW%Setting up git repository for movie project...%NC%

:: Initialize git if needed
if not exist ".git" (
    echo %GREEN%Initializing git repository...%NC%
    git init
)

:: Add all files
echo %GREEN%Adding files to git...%NC%
git add .

:: Initial commit
echo %GREEN%Creating initial commit...%NC%
git commit -m "Initial commit: Noir-style video podcast generator"

:: Get GitHub username
echo %YELLOW%Enter your GitHub username:%NC%
set /p username=

:: Add remote
echo %GREEN%Adding remote repository...%NC%
git remote add origin "https://github.com/%username%/movie.git"

:: Push to main
echo %GREEN%Pushing to main branch...%NC%
git branch -M main
git push -u origin main

echo %GREEN%Setup complete!%NC%
echo %YELLOW%Don't forget to:%NC%
echo 1. Create the repository on GitHub first
echo 2. Add your environment variables in GitHub repository settings
echo 3. Configure Replit secrets if using Replit

pause
