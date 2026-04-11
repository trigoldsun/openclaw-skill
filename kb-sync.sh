#!/bin/bash
# Knowledge Base Auto-Sync Script
# Run this periodically to keep your GitHub backup up to date

KB_PATH="$HOME/.openclaw/workspace/skills/public/personal-knowledge-base"

cd "$KB_PATH" || exit 1

echo "🚀 Starting knowledge base sync..."

# Add and commit changes
git add -A
git diff --cached --quiet && git diff --quiet || {
    git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M')" --allow-empty
    echo "✅ Changes committed"
}

# Push to GitHub
if git push origin main; then
    echo "✅ Sync complete!"
else
    echo "❌ Sync failed - check credentials"
    exit 1
fi
