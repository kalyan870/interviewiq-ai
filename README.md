# InterviewIQ AI

> **AI-powered interview intelligence for deliberate practice.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit%20InterviewIQ%20AI-246BFE?style=for-the-badge)](https://ai-mock-interview-pj03qbplx-kalyan870s-projects.vercel.app)

InterviewIQ AI is a full-stack mock-interview platform that conducts a role-specific interview one question at a time, evaluates every answer, adapts difficulty, and produces an actionable readiness report.

**[Open the live application →](https://ai-mock-interview-pj03qbplx-kalyan870s-projects.vercel.app)**

## What it delivers

- Role, experience-level, interview-mode, and question-count configuration
- Technical, Coding, System Design, Generative AI, HR / Behavioral, and Mixed modes
- Adaptive interview flow: answer → evaluation → knowledge-gap detection → difficulty decision → next question
- Structured answer evaluation across correctness, relevance, completeness, clarity, and technical depth
- Interview readiness report with strengths, improvement areas, and recommended practice topics
- Resume Intelligence: validated PDF upload and text extraction for contextual questions
- Project-defense-ready interview configuration
- Responsive InterviewIQ dashboard with readiness score and progress visualisation

## Application Architecture

The application keeps browser presentation, backend orchestration, AI evaluation, and persisted data responsibilities separate. The diagram below captures the wider product architecture and planned production integrations.

![InterviewIQ AI application architecture](docs/images/application-architecture.png)

## Final Architecture

The current implementation uses a Next.js frontend and FastAPI API, with a secure server-side OpenAI integration point and Supabase schema prepared for production persistence and authentication. When no OpenAI key is present, the service intentionally runs in a local demo mode so the full interview experience remains runnable.

![InterviewIQ AI final architecture](docs/images/final-architecture.png)

## Technology

| Layer | Technology |
| --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| API | Python, FastAPI, Pydantic |
| AI | OpenAI structured JSON output with a deterministic local fallback |
| Resume parsing | PyMuPDF |
| Data model | PostgreSQL / Supabase migration with row-level security |
| Deployment | Vercel |

## Repository structure

```text
frontend/     Next.js application and InterviewIQ dashboard
backend/      FastAPI service, interview engine, resume parser, API tests
supabase/     Supabase/PostgreSQL schema and RLS policies
docs/         deployment notes and architecture visuals
```

## Run locally

1. Copy `.env.example` to `frontend/.env.local` and `backend/.env`.
2. Start the API:

   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. Start the frontend in another terminal:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

Visit `http://localhost:3000`.

## Environment variables

Never expose server secrets in the browser. Use the provided `.env.example` files:

```env
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000

# backend/.env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
ALLOWED_ORIGINS=http://localhost:3000
```

## Deployment

- Frontend: Vercel
- FastAPI API: Vercel serverless deployment or Render/Railway
- Production data/auth: Supabase

See [deployment notes](docs/DEPLOYMENT.md) and the [Supabase migration](supabase/migrations/001_initial_schema.sql).

## Roadmap

- Supabase Auth connected to protected API routes
- Database-backed interview history and cross-device analytics
- LangGraph interview-state orchestration
- Safe sandbox service for executable coding assessments
- Voice transcription and downloadable report exports

## License

This project is available under the [MIT License](LICENSE).
