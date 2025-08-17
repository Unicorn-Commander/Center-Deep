#!/bin/bash

# Repository Migration Script
# Migrates Center-Deep from MagicUnicornInc to Unicorn-Commander organization

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
OLD_REPO="https://github.com/MagicUnicornInc/Center-Deep.git"
NEW_REPO="https://github.com/Unicorn-Commander/Center-Deep.git"
BACKUP_DIR="center-deep-backup-$(date +%Y%m%d-%H%M%S)"

echo -e "${BLUE}🚀 Center-Deep Repository Migration Script${NC}"
echo -e "${BLUE}===========================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        exit 1
    fi
    
    if ! git remote -v | grep -q "MagicUnicornInc/Center-Deep"; then
        print_error "This script must be run from the Center-Deep repository"
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Create backup
create_backup() {
    print_info "Creating backup..."
    
    cd ..
    git clone --mirror Center-Deep "$BACKUP_DIR"
    cd Center-Deep
    
    print_status "Backup created at ../$BACKUP_DIR"
}

# Verify new repository exists
verify_new_repo() {
    print_info "Verifying new repository exists..."
    
    if ! git ls-remote "$NEW_REPO" &> /dev/null; then
        print_error "New repository does not exist or is not accessible"
        print_info "Please create the repository at: $NEW_REPO"
        exit 1
    fi
    
    print_status "New repository verified"
}

# Update remote URL
update_remote() {
    print_info "Updating remote URL..."
    
    # Add new remote
    git remote add new-origin "$NEW_REPO" 2>/dev/null || true
    
    # Push all branches and tags to new remote
    print_info "Pushing all branches to new repository..."
    git push new-origin --all
    git push new-origin --tags
    
    # Update origin to point to new repository
    git remote set-url origin "$NEW_REPO"
    git remote remove new-origin 2>/dev/null || true
    
    print_status "Remote URL updated successfully"
}

# Update documentation references
update_documentation() {
    print_info "Updating documentation references..."
    
    # Update README.md references
    if [[ -f "README.md" ]]; then
        sed -i.bak 's|MagicUnicornInc/Center-Deep|Unicorn-Commander/Center-Deep|g' README.md
        rm README.md.bak 2>/dev/null || true
    fi
    
    # Update other documentation files
    find . -name "*.md" -not -path "./.git/*" -exec sed -i.bak 's|MagicUnicornInc/Center-Deep|Unicorn-Commander/Center-Deep|g' {} \;
    find . -name "*.bak" -delete 2>/dev/null || true
    
    print_status "Documentation references updated"
}

# Update UC-1 Pro integration
update_uc1_integration() {
    print_info "Checking UC-1 Pro integration updates..."
    
    UC1_COMPOSE="../docker-compose.yml"
    if [[ -f "$UC1_COMPOSE" ]]; then
        print_warning "UC-1 Pro docker-compose.yml found"
        print_info "You may need to update the build context in UC-1 Pro"
        print_info "File location: $UC1_COMPOSE"
    fi
    
    print_status "UC-1 Pro integration check completed"
}

# Commit changes
commit_changes() {
    print_info "Committing migration changes..."
    
    if git diff --quiet && git diff --staged --quiet; then
        print_info "No changes to commit"
        return
    fi
    
    git add .
    git commit -m "Update repository references for migration to Unicorn-Commander organization

- Update all documentation links
- Update repository URLs in configuration files
- Prepare for enterprise positioning under Unicorn Commander

🤖 Generated with Magic Unicorn Technology & Stuff Inc"
    
    git push origin main
    
    print_status "Changes committed and pushed"
}

# Verify migration
verify_migration() {
    print_info "Verifying migration..."
    
    # Check remote URL
    CURRENT_REMOTE=$(git remote get-url origin)
    if [[ "$CURRENT_REMOTE" == "$NEW_REPO" ]]; then
        print_status "Remote URL correctly updated"
    else
        print_error "Remote URL not updated correctly"
        print_info "Expected: $NEW_REPO"
        print_info "Actual: $CURRENT_REMOTE"
    fi
    
    # Test connectivity
    if git fetch origin &> /dev/null; then
        print_status "Connection to new repository verified"
    else
        print_error "Cannot connect to new repository"
    fi
    
    print_status "Migration verification completed"
}

# Main migration process
main() {
    echo -e "${BLUE}Starting migration process...${NC}"
    echo ""
    
    check_prerequisites
    echo ""
    
    # Ask for confirmation
    echo -e "${YELLOW}This will migrate the repository from:${NC}"
    echo -e "  ${RED}FROM:${NC} $OLD_REPO"
    echo -e "  ${GREEN}TO:${NC}   $NEW_REPO"
    echo ""
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Migration cancelled"
        exit 0
    fi
    
    echo ""
    
    create_backup
    echo ""
    
    verify_new_repo
    echo ""
    
    update_remote
    echo ""
    
    update_documentation
    echo ""
    
    update_uc1_integration
    echo ""
    
    commit_changes
    echo ""
    
    verify_migration
    echo ""
    
    print_status "🎉 Migration completed successfully!"
    echo ""
    print_info "Next steps:"
    echo "  1. Verify all features work correctly"
    echo "  2. Update UC-1 Pro integration if needed"
    echo "  3. Update website and documentation links"
    echo "  4. Notify team members of new repository location"
    echo "  5. Archive old repository with migration notice"
    echo ""
    print_info "Backup location: ../$BACKUP_DIR"
    print_info "New repository: $NEW_REPO"
}

# Run migration
main "$@"