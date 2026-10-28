-- Run this in the Supabase SQL Editor before enabling saves.
-- The application uses a server-only secret key. Browser/public roles have no
-- table access; Row Level Security remains enabled as a second safety layer.

create table if not exists public.travel_itineraries (
    id uuid primary key,
    created_at timestamptz not null default now(),
    destination text not null,
    trip_request jsonb not null,
    itinerary jsonb not null
);

alter table public.travel_itineraries enable row level security;
revoke all on table public.travel_itineraries from anon, authenticated;
grant select, insert, update on table public.travel_itineraries to service_role;
