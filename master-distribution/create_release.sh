#!/bin/bash
# KKT Release Packaging Script
# Creates release package for GitHub distribution

VERSION=$(cat VERSION)
PACKAGE_NAME="kkt-app-v${VERSION}.tar.gz"

echo "Creating KKT Release Package v${VERSION}..."

# Create temporary directory for packaging
TEMP_DIR="kkt-release-temp"
rm -rf $TEMP_DIR
mkdir -p $TEMP_DIR

# Copy production files
echo "Copying application files..."
cp -r backend $TEMP_DIR/
cp -r bot $TEMP_DIR/
cp -r web $TEMP_DIR/
cp -r database $TEMP_DIR/
cp -r deployment $TEMP_DIR/

# Copy configuration templates
cp requirements.txt $TEMP_DIR/
cp requirements-web.txt $TEMP_DIR/
cp .env.example $TEMP_DIR/
cp VERSION $TEMP_DIR/
cp CHANGELOG.md $TEMP_DIR/
cp README.md $TEMP_DIR/

# Remove test and development files
echo "Cleaning up development files..."
find $TEMP_DIR -type f -name "*.pyc" -delete
find $TEMP_DIR -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find $TEMP_DIR -type f -name "test_*.py" -delete
find $TEMP_DIR -type f -name "*_test.py" -delete
find $TEMP_DIR -path "*/web/add_test_*.py" -delete
find $TEMP_DIR -path "*/web/check_*.py" -delete
find $TEMP_DIR -path "*/web/apply_*.py" -delete
find $TEMP_DIR -path "*/web/clear_*.py" -delete
find $TEMP_DIR -path "*/web/generate_*.py" -delete
find $TEMP_DIR -path "*/web/init_web_db.py" -delete
find $TEMP_DIR -path "*/web/update_*.py" -delete

# Create tarball
echo "Creating tarball..."
tar -czf $PACKAGE_NAME -C $TEMP_DIR .

# Generate checksum
echo "Generating checksum..."
sha256sum $PACKAGE_NAME > checksums.txt

# Cleanup
rm -rf $TEMP_DIR

echo ""
echo "✓ Release package created: $PACKAGE_NAME"
echo "✓ Checksum file: checksums.txt"
echo ""
echo "Package contents:"
tar -tzf $PACKAGE_NAME | head -20
echo "..."
echo ""
echo "Next steps:"
echo "1. Create git tag: git tag -a v${VERSION} -m \"Release v${VERSION}\""
echo "2. Push tag: git push origin v${VERSION}"
echo "3. Create GitHub release and upload:"
echo "   - $PACKAGE_NAME"
echo "   - checksums.txt"
