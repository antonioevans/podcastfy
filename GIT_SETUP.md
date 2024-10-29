# Git Setup Instructions

Follow these steps to push the project to a new repository called "movie":

1. Initialize git repository (if not already done):
```bash
git init
```

2. Add all files to git:
```bash
git add .
```

3. Create initial commit:
```bash
git commit -m "Initial commit: Noir-style video podcast generator"
```

4. Create a new repository on GitHub:
- Go to https://github.com/new
- Name: movie
- Description: AI-driven noir-style video podcast generator
- Choose public or private
- Do not initialize with README (we already have one)

5. Add the remote repository:
```bash
git remote add origin https://github.com/yourusername/movie.git
```

6. Push to main branch:
```bash
git branch -M main
git push -u origin main
```

## After Initial Push

To update the repository later:
```bash
git add .
git commit -m "Your commit message"
git push
```

## Important Notes

1. Make sure you have these files before pushing:
   - .gitignore (to exclude unnecessary files)
   - .replit and replit.nix (for Replit deployment)
   - requirements.txt (for dependencies)
   - README.md (project documentation)

2. Environment Variables:
   - Do not commit .env file
   - Add environment variables in GitHub repository settings
   - For Replit, add them in Replit Secrets

3. Data Directories:
   - data/audio/.gitkeep
   - data/images/.gitkeep
   - data/videos/.gitkeep
   - These directories are tracked but their contents are ignored

4. Before pushing, verify:
   - No sensitive data in commits
   - All necessary files are tracked
   - No large binary files included
