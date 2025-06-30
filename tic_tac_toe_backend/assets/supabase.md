# Supabase Integration for FastAPI Backend

## Supabase Project Info
- **Project name**: tic_tac_toe_app
- **Supabase URL**: `https://sifshblvwjgyketwesog.supabase.co`
- **Anon Public Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpZnNoYmx2d2pneWtldHdlc29nIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzMDE4NzksImV4cCI6MjA2Njg3Nzg3OX0.ZDxL8P5gYekwUnzWEsB2TZugTAwncNK_UJmL6cieUMw`
- **Database URL**: `postgresql://postgres:Prasanth232%40@db.sifshblvwjgyketwesog.supabase.co:5432/postgres`

## Environment Setup
- Store required credentials in `.env` file at the project root:
  ```
  SUPABASE_URL=...
  SUPABASE_KEY=...
  SUPABASE_DB_URL=...
  ```
- Use `python-dotenv` in FastAPI to load these credentials.

## Authentication Integration
- Use Supabase authentication endpoints for sign-up, sign-in, and session management.
- Recommend using the official [supabase-py](https://github.com/supabase-community/supabase-py) client for Python for native integration.
- Example usage:
  ```python
  from supabase import create_client, Client
  import os

  url = os.getenv('SUPABASE_URL')
  key = os.getenv('SUPABASE_KEY')
  supabase: Client = create_client(url, key)
  ```

## Storage Integration
- Use Supabase Storage for file uploads (if required for user avatars, etc).
- [supabase-py docs](https://supabase.com/docs/reference/python/storage-upload)

## Additional Notes
- Update/extend this file with new database tables, auth scopes, or schema migrations as you build out the backend.
