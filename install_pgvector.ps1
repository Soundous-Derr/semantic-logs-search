# Script pour installer pgvector pour PostgreSQL 17 sur Windows

Write-Host "=" * 80
Write-Host "Installation de pgvector pour PostgreSQL 17"
Write-Host "=" * 80

# Vérifier si git est installé
try {
    git --version | Out-Null
} catch {
    Write-Host "❌ Git n'est pas installé. Installez Git d'abord: https://git-scm.com/download/win"
    exit 1
}

# Vérifier si Visual Studio Build Tools est disponible
$vsPath = "C:\Program Files\Microsoft Visual Studio\2022"
if (-not (Test-Path $vsPath)) {
    Write-Host "❌ Visual Studio Build Tools n'est pas trouvé"
    Write-Host "Visitez: https://visualstudio.microsoft.com/downloads/"
    Write-Host "Installez 'Desktop development with C++'"
    exit 1
}

# Variables
$pgInstallPath = "C:\Program Files\PostgreSQL\17"
$tmpDir = "C:\Temp\pgvector-build"
$gitRepo = "https://github.com/pgvector/pgvector.git"

# Créer répertoire temporaire
if (-not (Test-Path $tmpDir)) {
    New-Item -ItemType Directory -Path $tmpDir | Out-Null
}

# Cloner pgvector
Write-Host "`n📥 Téléchargement de pgvector..."
cd $tmpDir
if (Test-Path "pgvector") {
    Remove-Item -Recurse -Force "pgvector"
}
git clone $gitRepo
cd pgvector

# Compiler avec nmake (Visual Studio)
Write-Host "`n🔨 Compilation de pgvector..."

# Chercher vcvars
$vcvarsPath = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
if (-not (Test-Path $vcvarsPath)) {
    $vcvarsPath = "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat"
}
if (-not (Test-Path $vcvarsPath)) {
    $vcvarsPath = "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvars64.bat"
}

if (-not (Test-Path $vcvarsPath)) {
    Write-Host "❌ Visual Studio Build Tools vcvars64.bat non trouvé"
    Write-Host "Assurez-vous que Visual Studio 2022 Community/Professional/Enterprise est installé"
    exit 1
}

# Compiler
& cmd.exe /c "`"$vcvarsPath`" && nmake /F makefile.win POSTGRES_PATH=`"$pgInstallPath`" PGVERSION=17"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ La compilation a échoué"
    exit 1
}

# Installer
Write-Host "`n📦 Installation dans PostgreSQL..."
& cmd.exe /c "`"$vcvarsPath`" && nmake /F makefile.win POSTGRES_PATH=`"$pgInstallPath`" PGVERSION=17 install"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ pgvector installé avec succès!"
    
    # Activer l'extension
    Write-Host "`n🔧 Activation de l'extension pgvector..."
    &"$pgInstallPath\bin\psql.exe" -U postgres -d semantic_logs -c "CREATE EXTENSION IF NOT EXISTS vector;"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Extension pgvector activée!"
    } else {
        Write-Host "⚠️  L'extension pgvector n'a pas pu être activée automatiquement"
        Write-Host "Essayez manuellement dans pgAdmin ou psql"
    }
} else {
    Write-Host "❌ L'installation a échoué"
    exit 1
}

Write-Host "`n" + "=" * 80
Write-Host "✅ Installation complète!"
Write-Host "=" * 80
