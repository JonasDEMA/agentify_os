# Remove Lumina/LAM References - Replace with Agentify
# This script replaces all references to Lumina, LuminaOS, and LAM with Agentify equivalents

Write-Host "🔄 Removing Lumina/LAM references and replacing with Agentify..." -ForegroundColor Cyan

# Define replacements
$replacements = @{
    # Lumina replacements
    "LuminaOS" = "Agentify"
    "Lumina OS" = "Agentify"
    "lumina-os.com" = "agentify.dev"
    "licensing@lumina-os.com" = "licensing@agentify.dev"
    "support@lumina-os.com" = "support@agentify.dev"
    "https://lumina-os.com" = "https://agentify.dev"
    "Moßler GmbH / LuminaOS" = "Moßler GmbH / Agentify"
    
    # LAM Protocol replacements
    "LAM Protocol" = "Agent Communication Protocol"
    "LAM Gateway" = "Agent Gateway"
    "LAM Message" = "Agent Message"
    "LAM \(Lumina Agent Messages\)" = "Agent Communication Protocol"
    "lam-gateway" = "agent-gateway"
    "lam_protocol" = "agent_protocol"
    "LAM message" = "agent message"
    
    # Config replacements
    "luminaos_config" = "agentify_config"
    "LuminaOSConfig" = "AgentifyConfig"
    "LUMINAOS_" = "AGENTIFY_"
    
    # URL replacements
    "luminaos-three.vercel.app" = "agentify.dev"
}

# File extensions to process
$extensions = @("*.py", "*.md", "*.ts", "*.tsx", "*.js", "*.jsx", "*.json", "*.yaml", "*.yml", "*.toml", "*.txt")

# Directories to exclude
$excludeDirs = @(".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".pytest_cache")

# Get all files
Write-Host "📂 Scanning files..." -ForegroundColor Yellow
$files = Get-ChildItem -Recurse -File -Include $extensions | Where-Object {
    $path = $_.FullName
    $exclude = $false
    foreach ($dir in $excludeDirs) {
        if ($path -like "*\$dir\*") {
            $exclude = $true
            break
        }
    }
    -not $exclude
}

Write-Host "📝 Found $($files.Count) files to process" -ForegroundColor Green

# Process each file
$totalReplacements = 0
$filesModified = 0

foreach ($file in $files) {
    $content = Get-Content -Path $file.FullName -Raw -ErrorAction SilentlyContinue
    
    if (-not $content) {
        continue
    }
    
    $originalContent = $content
    $fileReplacements = 0
    
    # Apply all replacements
    foreach ($key in $replacements.Keys) {
        $value = $replacements[$key]
        $pattern = [regex]::Escape($key)
        
        # Count matches
        $matches = [regex]::Matches($content, $pattern)
        if ($matches.Count -gt 0) {
            $content = $content -replace $pattern, $value
            $fileReplacements += $matches.Count
        }
    }
    
    # Save if modified
    if ($content -ne $originalContent) {
        Set-Content -Path $file.FullName -Value $content -NoNewline
        $filesModified++
        $totalReplacements += $fileReplacements
        Write-Host "  ✅ $($file.Name): $fileReplacements replacements" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "✨ Complete!" -ForegroundColor Cyan
Write-Host "  📝 Files modified: $filesModified" -ForegroundColor Green
Write-Host "  🔄 Total replacements: $totalReplacements" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Manual review recommended for:" -ForegroundColor Yellow
Write-Host "  - agents/desktop_rpa/config/luminaos_config.py (rename file)" -ForegroundColor Yellow
Write-Host "  - Any hardcoded URLs or API endpoints" -ForegroundColor Yellow
Write-Host "  - Documentation that references specific Lumina features" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Review changes: git diff" -ForegroundColor White
Write-Host "  2. Test the application" -ForegroundColor White
Write-Host "  3. Commit changes: git add . && git commit -m 'Remove Lumina/LAM references, replace with Agentify'" -ForegroundColor White
Write-Host ""

