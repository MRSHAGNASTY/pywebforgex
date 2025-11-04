Param(
  [string]$Name = (Split-Path -Leaf (Get-Location)),
  [string]$Owner = "",
  [ValidateSet("public","private","internal")]
  [string]$Visibility = "public",
  [string]$Description = "$((Split-Path -Leaf (Get-Location))) – auto-published",
  [string]$Homepage = "",
  [string]$Topics = "python,automation,tooling",
  [string]$LicenseKey = "mit",
  [string]$DefaultBranch = "main"
)

function Require-Cmd($cmd, $msg) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { throw $msg }
}
Require-Cmd gh "GitHub CLI 'gh' not found. Install https://cli.github.com/ and run 'gh auth login'"
Require-Cmd git "git not found. Install Git."

if (-not (Test-Path ".git")) {
  git init | Out-Null
  git branch -M $DefaultBranch | Out-Null
}

if (-not (Test-Path ".gitignore")) {
@"
__pycache__/
*.py[cod]
*.egg-info/
.venv/
.env
node_modules/
.DS_Store
Thumbs.db
dist/
build/
*.log
"@ | Set-Content -NoNewline ".gitignore"
}

if (-not (Test-Path "LICENSE")) {
  $year = (Get-Date).Year
  $name = (git config user.name); if (-not $name) { $name = "Your Name" }
  $body = gh api -H "Accept: application/vnd.github+json" "/licenses/$LicenseKey" --jq ".body" 2>$null
  if (-not $body) { $body = "Copyright (c) [year] [fullname]" }
  $body = $body -replace "\[year\]", $year -replace "\[fullname\]", $name
  Set-Content -Path "LICENSE" -Value $body -Encoding UTF8
}

if (-not (Test-Path "README.md")) {
@"
# $Name

$Description

## What it does
Briefly describe the problem it solves and who it's for.

## How it works
- Key components and flow
- Tech stack
- Any constraints or assumptions

## Quick start
\`\`\`powershell
pip install -r requirements.txt
python app.py
\`\`\`

## License
See [LICENSE](./LICENSE).
"@ | Set-Content -Path "README.md" -Encoding UTF8
} else {
  $readme = Get-Content README.md -Raw
  if ($readme -notmatch '## How it works') {
@"

## How it works
- Components, flow, and key design decisions.
"@ | Add-Content README.md
  }
}

git add -A
git diff --cached --quiet; if ($LASTEXITCODE -ne 0) { git commit -m "chore: initial publish via script" | Out-Null }

$fullName = if ($Owner) { "$Owner/$Name" } else { "$((gh api user --jq .login))/$Name" }

if (gh repo view $fullName 2>$null) {
  if (-not (git remote get-url origin 2>$null)) { git remote add origin "https://github.com/$fullName.git" }
} else {
  $args = @("repo","create",$fullName,"--$Visibility","--description",$Description,"--source",".","--remote","origin","--push")
  if ($Homepage) { $args += @("--homepage",$Homepage) }
  gh @args
}

gh repo edit $fullName --description "$Description" | Out-Null
if ($Homepage) { gh repo edit $fullName --homepage "$Homepage" | Out-Null }
$Topics.Split(",") | ForEach-Object { gh repo edit $fullName --add-topic ($_.Trim()) | Out-Null }

Write-Host "✅ Published: https://github.com/$fullName"
