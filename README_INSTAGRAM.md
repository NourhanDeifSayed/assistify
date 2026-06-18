# Instagram Integration Setup

This branch contains the Instagram Messaging integration for Assistify.

## Branch

```bash
git switch instagram-integration
```

## Requirements

- Docker Desktop
- Git
- Ollama
- ngrok
- A Meta Developer app
- An Instagram Professional account connected to the Meta app

## 1. Clone the project

```bash
git clone <REPOSITORY_URL>
cd assistify
git switch instagram-integration
```

## 2. Configure environment variables

Copy the backend example file:

### Windows PowerShell

```powershell
Copy-Item backend/.env.example backend/.env
```

Fill in `backend/.env` with your own values:

```env
DEBUG=True
SECRET_KEY=your-django-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,backend,YOUR-NGROK-HOST

INSTAGRAM_ACCESS_TOKEN=your-instagram-access-token
META_APP_SECRET=your-meta-app-secret
INSTAGRAM_APP_SECRET=your-instagram-app-secret
INSTAGRAM_VERIFY_TOKEN=your-webhook-verify-token
INSTAGRAM_API_VERSION=v25.0
INSTAGRAM_GRAPH_HOST=https://graph.instagram.com
INSTAGRAM_VERIFY_SIGNATURE=True

OLLAMA_HOST=http://host.docker.internal:11434
```

Do not commit `backend/.env`.

## 3. Configure the fine-tuned intent model

The large model weights are not included in GitHub.

Place the model directory locally at:

```text
models/intent_model_finetuned/
```

The directory should contain files such as:

```text
config.json
intent_config.json
model.safetensors
special_tokens_map.json
tokenizer.json
tokenizer_config.json
vocab.txt
```

Create a root `.env` file:

```env
INTENT_MODEL_PATH=./models/intent_model_finetuned
```

You can also set `INTENT_MODEL_PATH` to another local directory.

## 4. Install and start Ollama

Pull the model:

```bash
ollama pull qwen2.5:1.5b
```

Confirm Ollama is running:

```bash
ollama list
```

The backend container connects to Ollama through:

```text
http://host.docker.internal:11434
```

## 5. Start the project

```bash
docker compose up --build
```

In another terminal, run:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_data
```

The seed command creates Arabic medical products, offers, and deterministic recommendation interactions.

## 6. Start ngrok

Expose the Django backend:

```bash
ngrok http 8000
```

Copy the HTTPS host, for example:

```text
https://example.ngrok-free.app
```

Add only the host to `ALLOWED_HOSTS` in `backend/.env`:

```env
ALLOWED_HOSTS=localhost,127.0.0.1,backend,example.ngrok-free.app
```

Recreate the backend after changing the environment:

```bash
docker compose up --force-recreate backend
```

## 7. Configure the Meta webhook

Use this callback URL:

```text
https://YOUR-NGROK-HOST/api/v1/chat/instagram/webhook/
```

Use the same value for `INSTAGRAM_VERIFY_TOKEN` in Meta and `backend/.env`.

Subscribe the webhook to:

```text
messages
```

The privacy policy page is available at:

```text
https://YOUR-NGROK-HOST/privacy-policy/
```

## 8. Instagram account settings

Make sure that:

- The Instagram account is a Professional account.
- The account is connected to the Meta app.
- The Instagram tester invitation has been accepted when using development mode.
- Access to messages is enabled in Instagram Connected tools.
- The access token belongs to the same Instagram account used by the integration.

## 9. Verify the integration

Test Docker-to-Ollama connectivity:

```bash
docker compose exec backend curl -s http://host.docker.internal:11434/api/tags
```

Test Django:

```bash
docker compose exec backend python manage.py check
```

Send a direct message to the connected Instagram account:

```text
مرحبًا
```

Then try:

```text
إيه المنتجات الطبية المتوفرة عندكم؟
```

## Important notes

- Never commit access tokens, app secrets, verify tokens, or `.env` files.
- `model.safetensors` is intentionally excluded from Git.
- Each developer must use their own Meta app, Instagram account, access token, secrets, and ngrok URL.
- The free ngrok URL can change whenever ngrok is restarted.
