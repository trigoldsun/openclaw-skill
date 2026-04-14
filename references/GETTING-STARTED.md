# 🚀 Personal Knowledge Base - Quick Start Guide

## What is this?

A **simple, structured** system to organize your personal knowledge across multiple dimensions:

- **Topic** (what it's about)
- **Project** (which project)  
- **Person** (who's involved)
- **Time** (when created)
- **Status** (current state)

Plus automatic tracking of relationships between related items.

---

## Installation (2 minutes)

### Step 1: Verify setup exists
```bash
ls ~/workspaces/personal-knowledge-base/
# Should see: data/, index/, scripts/
```

### Step 2: Initialize (first time only)
```bash
cd ~/.openclaw/workspace/skills/public/personal-knowledge-base
python3 scripts/add_entry.py --list-types
```

Expected output:
```
Available entry types:
  note            → Individual knowledge notes
  meeting         → Meeting records with participants
  decision        → Important decisions made
  project         → Project summaries and status
  reference       → External references and resources
```

✅ You're ready!

---

## Your First Entry (1 minute)

### Option A: Interactive Mode (Recommended)
```bash
python3 scripts/add_entry.py --interactive
```

Then follow the prompts:
```
Title: My first meeting notes
Type (1-5): 2
Topics: Communication, Team
Projects: Personal KB
Persons: myself, team
Summary: Weekly sync discussion
[Enter content...]
```

### Option B: Command Line
```bash
python3 scripts/add_entry.py \
    --title "Knowledge base design" \
    --type note \
    --topics Technology,Knowledge Management \
    --projects "Personal KB" \
    --persons myself \
    --summary "Initial thoughts on multi-dimensional indexing" \
    --tags "automation","system-design"
```

Result:
```
✅ Entry created: 202604111300-a1b2c3d4
   Title: Knowledge base design
   Type: note
   Location: /path/to/data/notes/202604111300-a1b2c3d4.json
```

---

## Understanding File Structure

After adding entries, you'll have:

```
personal-knowledge-base/
├── data/
│   ├── notes/          # Your notes
│   │   └── 202604111300-*.json
│   ├── meetings/       # Meeting records
│   ├── decisions/      # Important decisions
│   └── projects/       # Project summaries
├── index/              # Auto-generated indexes
│   ├── by-topic.json   # All entries tagged with each topic
│   ├── by-project.json # All entries in each project
│   ├── by-person.json  # All mentions of each person
│   ├── by-date.json    # Entries by date
│   └── relationships.json # Links between entries
└── scripts/
    ├── add_entry.py    # Add new entries
    └── search_kb.py    # Search functionality
```

---

## Daily Workflow

### Morning: Review Today's Items
```bash
TODAY=$(date +%Y-%m-%d)
cat index/by-date.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"Entries for {TODAY}:\")
for entry_id in data.get('entries', {}).get(TODAY, []):
    print(f\"  • {entry_id}\")
"
```

### During Work: Capture Thoughts
```bash
# Quick capture
echo "TODO: Review permission system API docs" > /tmp/quick-note.txt
# Then process later with proper structure
```

### Evening: Review & Link
Open your latest entries and manually connect them:

1. Open `data/notes/YYYYMMDDHHMMSS-*.json`
2. Find `relationships.references` field
3. Add IDs of related entries you just read
4. Save

Example:
```json
{
  "relationships": {
    "references": [
      "202604111259-b2c3d4e5",
      "202604111258-c3d4e5f6"
    ]
  }
}
```

---

## Searching Your Knowledge

### Find by Topic
```bash
grep -l '"topic":.*"Technology"' data/**/*.json
```

### Find All Meetings This Week
```bash
# Look at by-week index
cat index/by-date.json | grep "W$(date +%V)"
```

### Find Discussions About a Person
```bash
grep -l "\"person\":\"myself\"" data/**/*.json
```

### Full Search (When Available)
```bash
python3 scripts/search_kb.py --topic "Knowledge" --project "Personal KB"
```

---

## Best Practices

### ✅ Do:
- **Add immediately** - Don't wait until end of day
- **Link liberally** - Connect related items as you create
- **Use consistent names** - "myself" not "me", "Sun Xin" not "sun-xin"
- **Review weekly** - Update statuses, clean up stale links
- **Archive old drafts** - Move completed ideas to "archived" status

### ❌ Don't:
- **Over-index** - Only tag what's truly relevant
- **Create duplicate** - Check existing entries first
- **Store secrets** - No passwords or sensitive PII
- **Forget relationships** - If two items are related, link them

---

## Troubleshooting

### "Index files corrupted"
```bash
rm index/*.json
python3 scripts/add_entry.py --init
# Rebuild from existing entries
```

### "Multiple entries with same ID"
IDs should be unique (timestamp + random). If duplicates occur, manually rename in filename.

### "Relationships not updating"
Ensure you're using full UUID format, not partial IDs:
```
Wrong: 20260411
Right: 202604111300-a1b2c3d4
```

---

## Next Steps

1. **Add more entries** - Build your knowledge base
2. **Explore templates** - See `templates/entry-template.json`
3. **Check examples** - Refer to this skill's main documentation
4. **Customize workflow** - Adapt dimensions to your needs

---

## Support

Need help? Check:
- Main SKILL.md file - Complete documentation
- `scripts/add_entry.py --help` - CLI options
- Example entries in git history (if tracked)

---

**Happy knowledge organizing! 📚**
