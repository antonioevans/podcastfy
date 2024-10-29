@echo off
setlocal EnableDelayedExpansion

:: Colors for Windows console
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "NC=[0m"

echo %YELLOW%Setting up git repository for movie project...%NC%

:: Check for environment setup
echo %YELLOW%Checking environment setup...%NC%
if not exist ".env" (
    echo %RED%Warning: No .env file found%NC%
    echo Please follow the steps in ENV_SETUP.md to set up your environment variables
    echo Press any key to continue anyway or Ctrl+C to cancel
    pause > nul
)

:: Initialize git if needed
if not exist ".git" (
    echo %GREEN%Initializing git repository...%NC%
    git init
)

:: Verify GitHub repository exists
echo %YELLOW%Before continuing, please ensure you have:%NC%
echo 1. Created the repository at: https://github.com/antonievans/movie
echo 2. Added environment variables in GitHub repository settings
echo 3. Configured Replit secrets if using Replit
echo.
echo %YELLOW%Have you created the repository? (Y/N)%NC%
set /p confirm=
if /i not "%confirm%"=="Y" (
    echo %RED%Please create the repository first. See GITHUB_REPO_SETUP.md for details.%NC%
    exit /b 1
)

:: Add all files
echo %GREEN%Adding files to git...%NC%
git add .

:: Initial commit
echo %GREEN%Creating initial commit...%NC%
git commit -m "Initial commit: Noir-style video podcast generator"

:: Add remote (using antonievans as the username)
echo %GREEN%Adding remote repository...%NC%
git remote add origin "https://github.com/antonievans/movie.git"

:: Push to main
echo %GREEN%Pushing to main branch...%NC%
git branch -M main
git push -u origin main

echo %GREEN%Setup complete!%NC%
echo.
echo %YELLOW%Next steps:%NC%
echo 1. Verify your code is on GitHub: https://github.com/antonievans/movie
echo 2. Add environment variables at: https://github.com/antonievans/movie/settings/secrets/actions
echo 3. Set up Replit by importing from your new repository
echo.
echo See ENV_SETUP.md for detailed environment configuration instructions

pause
