-- SCRUM-19: base de datos vectorial (Supabase + pgvector)
-- Ejecutar una sola vez en Supabase -> SQL Editor.

create extension if not exists vector;

create table if not exists conocimiento_chunks (
  id          bigserial primary key,
  fuente      text    not null,          -- nombre del archivo del que viene el chunk
  chunk_index int     not null,          -- posicion del chunk dentro del archivo
  contenido   text    not null,          -- texto del chunk
  embedding   vector(3072) not null,     -- gemini-embedding-001 (3072 dimensiones)
  creado_en   timestamptz default now(),
  unique (fuente, chunk_index)
);

-- Solo el backend (clave secreta) puede leer/escribir esta tabla.
alter table conocimiento_chunks enable row level security;

-- Busqueda por similitud coseno: devuelve los chunks mas parecidos a la pregunta.
create or replace function match_conocimiento(
  query_embedding vector(3072),
  match_count     int default 3
)
returns table (id bigint, fuente text, contenido text, similitud float)
language sql stable
as $$
  select id, fuente, contenido, 1 - (embedding <=> query_embedding) as similitud
  from conocimiento_chunks
  order by embedding <=> query_embedding
  limit match_count;
$$;
