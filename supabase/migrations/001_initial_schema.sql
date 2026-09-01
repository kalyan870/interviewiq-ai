-- Run in the Supabase SQL editor. Auth users remain in auth.users.
create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  created_at timestamptz not null default now()
);
create table public.interviews (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null, experience_level text not null check (experience_level in ('entry','mid','senior')),
  interview_type text not null, total_questions smallint not null check (total_questions between 3 and 20),
  overall_score numeric(5,2), created_at timestamptz not null default now()
);
create table public.questions (
  id uuid primary key default gen_random_uuid(), interview_id uuid not null references public.interviews(id) on delete cascade,
  question text not null, topic text not null, difficulty smallint not null check (difficulty between 1 and 5), question_number smallint not null, is_follow_up boolean not null default false
);
create table public.answers (
  id uuid primary key default gen_random_uuid(), question_id uuid not null references public.questions(id) on delete cascade,
  answer text not null, score numeric(4,2) not null, evaluation jsonb not null, created_at timestamptz not null default now()
);
create table public.interview_results (
  interview_id uuid primary key references public.interviews(id) on delete cascade, report jsonb not null, created_at timestamptz not null default now()
);
alter table public.profiles enable row level security;
alter table public.interviews enable row level security;
alter table public.questions enable row level security;
alter table public.answers enable row level security;
alter table public.interview_results enable row level security;
create policy "own profile" on public.profiles for all using (auth.uid() = id) with check (auth.uid() = id);
create policy "own interviews" on public.interviews for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own questions" on public.questions for all using (exists(select 1 from public.interviews i where i.id=interview_id and i.user_id=auth.uid()));
create policy "own answers" on public.answers for all using (exists(select 1 from public.questions q join public.interviews i on i.id=q.interview_id where q.id=question_id and i.user_id=auth.uid()));
create policy "own reports" on public.interview_results for all using (exists(select 1 from public.interviews i where i.id=interview_id and i.user_id=auth.uid()));
