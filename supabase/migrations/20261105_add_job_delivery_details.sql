alter table public.jobs_sent
  add column if not exists location text not null default 'Colombia',
  add column if not exists snippet text not null default '',
  add column if not exists status text not null default 'sent';

do $$
begin
  if not exists (
    select 1
    from pg_constraint
    where conname = 'jobs_sent_status_check'
      and conrelid = 'public.jobs_sent'::regclass
  ) then
    alter table public.jobs_sent
      add constraint jobs_sent_status_check
      check (status in ('pending', 'sent', 'failed'));
  end if;
end
$$;

create index if not exists jobs_sent_status_idx
  on public.jobs_sent (status);
