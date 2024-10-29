#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up git repository for movie project...${NC}"

# Check for environment setup
echo -e "${YELLOW}Checking environment setup...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}Warning: No .env file found${NC}"
    echo "Please follow the steps in ENV_SETUP.md to set up your environment variables"
    read -p "Press Enter to continue anyway or Ctrl+C to cancel"
fi

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo -e "${GREEN}Initializing git repository...${NC}"
    git init
fi

# Verify GitHub repository exists
echo -e "${YELLOW}Before continuing, please ensure you have:${NC}"
echo "1. Created the repository at: https://github.com/antonievans/movie"
echo "2. Added environment variables in GitHub repository settings"
echo "3. Configured Replit secrets if using Replit"
echo
read -p "Have you created the repository? (y/N) " confirm
if [[ $confirm != [yY] ]]; then
    echo -e "${RED}Please create the repository first. See GITHUB_REPO_SETUP.md for details.${NC}"
    exit 1
fi

# Add all files
echo -e "${GREEN}Adding files to git...${NC}"
git add .

# Initial commit
echo -e "${GREEN}Creating initial commit...${NC}"
git commit -m "Initial commit: Noir-style video podcast generator"

# Add remote (using antonievans as the username)
echo -e "${GREEN}Adding remote repository...${NC}"
git remote add origin "https://github.com/antonievans/movie.git"

# Push to main
echo -e "${GREEN}Pushing to main branch...${NC}"
git branch -M main
git push -u origin main

echo -e "${GREEN}Setup complete!${NC}"
echo
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Verify your code is on GitHub: https://github.com/antonievans/movie"
echo "2. Add environment variables at: https://github.com/antonievans/movie/settings/secrets/actions"
echo "3. Set up Replit by importing from your new repository"
echo
echo "See ENV_SETUP.md for detailed environment configuration instructions"

read -p "Press Enter to continue..."
