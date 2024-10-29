#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up git repository for movie project...${NC}"

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo -e "${GREEN}Initializing git repository...${NC}"
    git init
fi

# Add all files
echo -e "${GREEN}Adding files to git...${NC}"
git add .

# Initial commit
echo -e "${GREEN}Creating initial commit...${NC}"
git commit -m "Initial commit: Noir-style video podcast generator"

# Get GitHub username
echo -e "${YELLOW}Enter your GitHub username:${NC}"
read username

# Add remote
echo -e "${GREEN}Adding remote repository...${NC}"
git remote add origin "https://github.com/$username/movie.git"

# Push to main
echo -e "${GREEN}Pushing to main branch...${NC}"
git branch -M main
git push -u origin main

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}Don't forget to:${NC}"
echo "1. Create the repository on GitHub first"
echo "2. Add your environment variables in GitHub repository settings"
echo "3. Configure Replit secrets if using Replit"
