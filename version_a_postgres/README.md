# Version A - FastAPI + Neon PostgreSQL

## Setup (Windows PowerShell)

```powershell
cd version_a_postgres
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and paste your Neon PostgreSQL connection string. Do not commit `.env`.

```powershell
# Load .env variables into this PowerShell session
Get-Content .env | ForEach-Object {
  if ($_ -match '^([^#][^=]+)=(.*)$') {
    [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs

Tables are created automatically on startup for this learning project. For production, use Alembic migrations, managed secrets, restricted database roles, and explicit database migrations instead of `create_all`.
