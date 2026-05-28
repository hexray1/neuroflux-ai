# NeuroFlux AI: NVIDIA NIM API Setup Instructions

This document provides instructions on how to configure the NeuroFlux AI bot to use the NVIDIA NIM API for its AI functionalities.

## 1. Update Environment Variables

To use the NVIDIA NIM API, you need to set the `NVIDIA_API_KEY` and `NVIDIA_BASE_URL` environment variables. The `OPENAI_API_KEY` and `OPENAI_BASE_URL` are no longer used.

### 1.1. Local Development (`.env.example`)

If you are running the bot locally, update the `.env.example` file (or create a `.env` file from it) with your NVIDIA API key and the correct base URL. The `NVIDIA_BASE_URL` should point to the NVIDIA NIM API endpoint.

```
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_ID=your_telegram_admin_id_here
NVIDIA_API_KEY=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
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
```

**Note:** The `NVIDIA_API_KEY` provided above is a placeholder. You should replace `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` with your actual NVIDIA API key obtained from [https://build.nvidia.com](https://build.nvidia.com).

### 1.2. Deployment on Render (`render.yaml`)

If you are deploying the bot on Render, ensure that the following environment variables are set in your Render service configuration:

*   `NVIDIA_API_KEY`: Your NVIDIA API key.
*   `NVIDIA_BASE_URL`: `https://integrate.api.nvidia.com/v1`

The `render.yaml` file has been updated to reflect these changes. You will need to manually add these environment variables in the Render dashboard for your service.

## 2. Updated AI Model

The AI engine now uses the `nv-llama2-70b` model by default. If you wish to use a different NVIDIA NIM model, you can update the `MODEL` variable in `ai_engine.py` accordingly.

## 3. Dependencies

The `requirements.txt` file has been updated to remove unused dependencies (`requests` and `beautifulsoup4`) to streamline the installation process.

## 4. Verification

After updating the environment variables and deploying the bot, test the AI functionalities to ensure they are working correctly with the NVIDIA NIM API. Send `/start` to your bot on Telegram and try out the AI chat or other AI-powered features.
