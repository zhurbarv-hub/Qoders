# KKT Release Packaging Script (PowerShell)
# Creates release package for GitHub distribution

$VERSION = Get-Content VERSION -Raw
$VERSION = $VERSION.Trim()
$PACKAGE_NAME = "kkt-app-v$VERSION.tar.gz"

Write-Host "Creating KKT Release Package v$VERSION..." -ForegroundColor Green

# Create temporary directory
$TEMP_DIR = "kkt-release-temp"
if (Test-Path $TEMP_DIR) {
    Remove-Item -Recurse -Force $TEMP_DIR
}
New-Item -ItemType Directory -Path $TEMP_DIR | Out-Null

# Copy production files
Write-Host "Copying application files..."
Copy-Item -Recurse backend $TEMP_DIR/
Copy-Item -Recurse bot $TEMP_DIR/
Copy-Item -Recurse web $TEMP_DIR/
Copy-Item -Recurse database $TEMP_DIR/
Copy-Item -Recurse deployment $TEMP_DIR/

# Copy configuration templates
Copy-Item requirements.txt $TEMP_DIR/
Copy-Item requirements-web.txt $TEMP_DIR/
Copy-Item .env.example $TEMP_DIR/
Copy-Item VERSION $TEMP_DIR/
Copy-Item CHANGELOG.md $TEMP_DIR/
Copy-Item README.md $TEMP_DIR/

# Remove test and development files
Write-Host "Cleaning up development files..."
Get-ChildItem -Path $TEMP_DIR -Recurse -Include "*.pyc" | Remove-Item -Force
Get-ChildItem -Path $TEMP_DIR -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path $TEMP_DIR -Recurse -Include "test_*.py" | Remove-Item -Force
Get-ChildItem -Path $TEMP_DIR -Recurse -Include "*_test.py" | Remove-Item -Force
Get-ChildItem -Path "$TEMP_DIR\web" -Include "add_test_*.py","check_*.py","apply_*.py","clear_*.py","generate_*.py","init_web_db.py","update_*.py" | Remove-Item -Force

# Create tarball using tar (available in Windows 10+)
Write-Host "Creating tarball..."
tar -czf $PACKAGE_NAME -C $TEMP_DIR .

# Generate checksum
Write-Host "Generating checksum..."
$hash = (Get-FileHash $PACKAGE_NAME -Algorithm SHA256).Hash.ToLower()
"$hash  $PACKAGE_NAME" | Out-File -Encoding utf8 checksums.txt

# Cleanup
Remove-Item -Recurse -Force $TEMP_DIR

Write-Host ""
Write-Host "✓ Release package created: $PACKAGE_NAME" -ForegroundColor Green
Write-Host "✓ Checksum file: checksums.txt" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Create git tag: git tag -a v$VERSION -m 'Release v$VERSION'"
Write-Host "2. Push tag: git push origin v$VERSION"
Write-Host "3. Create GitHub release and upload:"
Write-Host "   - $PACKAGE_NAME"
Write-Host "   - checksums.txt"
