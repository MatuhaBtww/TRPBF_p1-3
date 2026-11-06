$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    py -3.14 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Cannot create virtual environment' }
}
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
& .\.venv\Scripts\python.exe manage.py migrate
if ($LASTEXITCODE -ne 0) { throw 'Migration failed' }
& .\.venv\Scripts\python.exe manage.py shell -c "from tracker.models import Project,Developer,Technology,Status; import sys; sys.exit(0 if any(m.objects.exists() for m in (Project,Developer,Technology,Status)) else 7)"
if ($LASTEXITCODE -eq 7) {
    & .\.venv\Scripts\python.exe manage.py import_json
    if ($LASTEXITCODE -ne 0) { throw 'Import failed' }
} elseif ($LASTEXITCODE -ne 0) { throw 'Database check failed' }
& .\.venv\Scripts\python.exe manage.py check
if ($LASTEXITCODE -ne 0) { throw 'Django check failed' }
