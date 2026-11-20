# Version B - FastAPI + MongoDB

## Setup (Windows PowerShell)

```powershell
cd version_b_mongodb
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` with your MongoDB Atlas connection string. Add your current IP to Atlas Network Access and create a database user. Never commit `.env`.

```powershell
Get-Content .env | ForEach-Object {
  if ($_ -match '^([^#][^=]+)=(.*)$') {
    [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs

This version stores projects and tasks in separate collections. `tasks.project_id` is a reference to a project ObjectId; MongoDB does not enforce a foreign-key constraint automatically. The API checks project existence when creating a task.
