$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    py -3 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Cannot create virtual environment. Install Python 3.10 or newer.' }
}
& .\.venv\Scripts\python.exe -m pip install --disable-pip-version-check -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
& .\.venv\Scripts\python.exe manage.py migrate
if ($LASTEXITCODE -ne 0) { throw 'Migration failed' }
& .\.venv\Scripts\python.exe manage.py init_data
if ($LASTEXITCODE -ne 0) { throw 'Data initialization failed' }
& .\.venv\Scripts\python.exe manage.py bootstrap_admin --with-viewer
if ($LASTEXITCODE -ne 0) { throw 'Account initialization failed' }
& .\.venv\Scripts\python.exe manage.py check
if ($LASTEXITCODE -ne 0) { throw 'Django check failed' }
Write-Host 'Ready. Run run.bat and open http://127.0.0.1:8000/'
Write-Host 'Account credentials: .private\admin-access.txt'
