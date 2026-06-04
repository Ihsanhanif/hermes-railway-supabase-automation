-- Supabase schema for Hermes automations
-- Run this in your Supabase SQL editor

-- Table to log automation runs
create table automation_logs (
  id uuid default gen_random_uuid() primary key,
  automation_name text not null,
  started_at timestamp with time zone default now(),
  finished_at timestamp with time zone,
  status text check (status in ('success', 'error', 'running')),
  message text,
  details jsonb default '{}'::jsonb
);

-- Table to store LLM usage metrics
create table llm_usage (
  id uuid default gen_random_uuid() primary key,
  timestamp timestamp with time zone default now(),
  model text,
  provider text,
  prompt_tokens integer,
  completion_tokens integer,
  total_tokens integer,
  cost_usd numeric(10,6),
  response_time_ms integer
);

-- Table to store fetched market data (optional, for historical analysis)
create table market_data (
  id uuid default gen_random_uuid() primary key,
  timestamp timestamp with time zone default now(),
  symbol text not null,
  price numeric(20,8),
  change_24h numeric(10,4),
  volume_24h numeric(20,2),
  data jsonb default '{}'::jsonb
);

-- Table to log sent motivational quotes
create table quote_log (
  id uuid default gen_random_uuid() primary key,
  sent_at timestamp with time zone default now(),
  quote text not null,
  author text,
  category text
);

-- Create indexes for better query performance
create index idx_automation_logs_name_time on automation_logs (automation_name, started_at);
create index idx_llm_usage_time on llm_usage (timestamp);
create index idx_market_data_symbol_time on market_data (symbol, timestamp);
create index idx_quote_log_time on quote_log (sent_at);

-- Optional: Enable Row Level Security (RLS) if you want to restrict access
-- alter table automation_logs enable row level security;
-- alter table llm_usage enable row level security;
-- alter table market_data enable row level security;
-- alter table quote_log enable row level security;

-- (If you enable RLS, you'll need to create policies for your application)