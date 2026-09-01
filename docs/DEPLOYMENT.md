# Deployment

## Vercel (frontend)

Set the Vercel project root to `frontend`, then configure `NEXT_PUBLIC_API_URL` with the public HTTPS URL of the API. Do not add OpenAI or Supabase service-role secrets to Vercel client variables.

## Render / Railway (backend)

Use `pip install -r requirements.txt` as the build command and `uvicorn app.main:app --host 0.0.0.0 --port $PORT` as the start command. Set `OPENAI_API_KEY`, `OPENAI_MODEL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `ALLOWED_ORIGINS` as server-side environment variables.

## Supabase

Run [the initial schema](../supabase/migrations/001_initial_schema.sql) in the SQL editor, enable your desired Auth providers, and add the Vercel URL to Auth redirect URLs. The provided migration scopes data access to its owner via row-level security.
