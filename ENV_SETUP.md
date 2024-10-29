# Environment Setup Guide

## GitHub Repository Secrets

1. Go to your GitHub repository settings
2. Navigate to "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Add each of these secrets:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   OPENAI_API_KEY=your_openai_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   FLUX_API_KEY=your_flux_api_key
   ```

## Replit Secrets

1. Open your Replit project
2. Click on "Tools" in the left sidebar
3. Select "Secrets"
4. Add each secret:
   ```
   Key: GEMINI_API_KEY
   Value: your_gemini_api_key
   ```
   ```
   Key: OPENAI_API_KEY
   Value: your_openai_api_key
   ```
   ```
   Key: ELEVENLABS_API_KEY
   Value: your_elevenlabs_api_key
   ```
   ```
   Key: FLUX_API_KEY
   Value: your_flux_api_key
   ```

## Local Development

1. Create a .env file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   OPENAI_API_KEY=your_openai_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   FLUX_API_KEY=your_flux_api_key
   ```
   
2. Add .env to .gitignore (already done)

## API Keys

1. Gemini API Key:
   - Go to https://makersuite.google.com/app/apikey
   - Create a new API key
   - Copy the key

2. OpenAI API Key:
   - Go to https://platform.openai.com/api-keys
   - Create new secret key
   - Copy the key

3. ElevenLabs API Key:
   - Go to https://elevenlabs.io/
   - Sign in to your account
   - Go to Profile Settings
   - Copy your API key

4. Flux API Key:
   - Go to https://fal.ai/
   - Sign in to your account
   - Go to API Settings
   - Copy your API key

## Verifying Setup

1. Local Environment:
   ```bash
   python -c "import os; print('GEMINI_API_KEY:', bool(os.getenv('GEMINI_API_KEY')))"
   ```

2. Replit:
   ```python
   import os
   print("Environment variables loaded:")
   for key in ['GEMINI_API_KEY', 'OPENAI_API_KEY', 'ELEVENLABS_API_KEY', 'FLUX_API_KEY']:
       print(f"{key}: {'✓' if os.getenv(key) else '✗'}")
   ```

## Troubleshooting

1. If environment variables aren't loading:
   - Check spelling of variable names
   - Restart the Replit server
   - Verify secrets are saved

2. If API calls fail:
   - Verify API key validity
   - Check API key permissions
   - Ensure proper key format

3. Common Issues:
   - Keys with special characters need proper escaping
   - Some platforms require base64 encoding
   - Rate limits may apply to free tier keys
