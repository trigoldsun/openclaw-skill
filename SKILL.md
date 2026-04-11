---
name: personal-knowledge-base
description: Structured personal knowledge management system with multi-dimensional classification and cross-referencing. Organize notes, decisions, meetings, projects by multiple logical dimensions (topic, project, person, time, status). Automatic relationship tracking between related items. Simple JSON-based structure for easy querying and linking.
---

# 🧠 Personal Knowledge Base System

## Overview

A **simple yet powerful** personal knowledge management system organized by **multiple logical dimensions**. Every piece of knowledge is classified, indexed, and linked to related items.

**Simple structure:** Single file per knowledge item + automatic relationship tracking  
**Multi-dimensional:** Organize by topic, project, person, time, status simultaneously  
**Linked relationships:** Automatic cross-referencing between related items

---

## 📊 Knowledge Dimensions Framework

### Primary Classification Dimensions

```
┌─────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE INDEX                          │
├──────────────┬──────────────┬──────────────┬───────────────┤
│   Topic      │   Project    │    Person    │    Time       │
│ (What?)      │ (Why?)       │ (Who?)       │ (When?)       │
├──────────────┼──────────────┼──────────────┼───────────────┤
│ Technology   │ Website Deploy│孙鑫        │ 2026-04-11   │
│ Business     │ User Permissions│系统管理     │ Q1 2026     │
│ Process      │ KB Creation  │ myself       │ Today       │
│ ...          │ ...          │ team         │ Month       │
└──────────────┴──────────────┴──────────────┴───────────────┘
```

### Dimension Details

| Dimension | Description | Examples |
|-----------|-------------|----------|
| **Topic** | What category does this belong to? | Technology, Business, Process, Personal, Learning |
| **Project** | Which project does this support? | Website Deploy, Permission System, Knowledge Base |
| **Person** | Who is involved/mentioned? | myself, 孙鑫，team, client-name |
| **Time** | When was this created/due? | YYYY-MM-DD, Q1-2026, 2026-Q1 |
| **Status** | What's the current state? | draft, review, approved, archived |

---

## 🗂️ File Structure

```
personal-knowledge-base/
├── SKILL.md                       # This documentation
├── data/
│   ├── notes/                     # Individual knowledge entries
│   │   ├── 2026-04-11-knowledge-base-design.json
│   │   ├── 2026-04-11-web-crawler-analysis.json
│   │   └── ...
│   ├── meetings/                  # Meeting records
│   │   ├── meeting-2026-04-11-team-sync.json
│   │   └── ...
│   ├── decisions/                 # Important decisions
│   │   ├── decision-tool-selection.json
│   │   └── ...
│   └── projects/                  # Project summaries
│       ├── website-deployment.json
│       └── ...
├── index/
│   ├── by-topic.json              # Index by topic
│   ├── by-project.json            # Index by project
│   ├── by-person.json             # Index by person
│   ├── by-date.json               # Index by date
│   └── relationships.json         # Relationship graph
├── scripts/
│   ├── add_entry.py               # CLI tool to add new entry
│   ├── search_kb.py               # Search across all dimensions
│   └── generate_report.py         # Generate knowledge reports
└── templates/
    └── entry-template.json        # Standard entry format
```

---

## 📄 Entry Template Format

Every knowledge entry follows this standard JSON format:

```json
{
  "id": "unique-id-generated",
  "title": "Clear descriptive title",
  "type": "note|meeting|decision|project|reference",
  "created_at": "2026-04-11T12:59:00Z",
  "updated_at": "2026-04-11T12:59:00Z",
  
  "dimensions": {
    "topic": ["Technology", "Knowledge Management"],
    "project": ["Personal KB", "Skill Development"],
    "person": ["myself", "孙鑫"],
    "time": {
      "date": "2026-04-11",
      "week": "2026-W15",
      "quarter": "2026-Q2",
      "year": 2026
    },
    "status": "draft"
  },
  
  "content": {
    "summary": "Brief one-sentence summary",
    "body": "Full content here...",
    "tags": ["automation", "system-design", "multi-dimension"]
  },
  
  "relationships": {
    "references": [
      "entry-id-of-related-item-1",
      "entry-id-of-related-item-2"
    ],
    "referenced_by": [],  // Auto-populated
    "depends_on": [],
    "blocks": []
  }
}
```

---

## 🔗 Relationship Tracking

### Relationship Types

| Type | Meaning | Example |
|------|---------|--------|
| **references** | This item links TO another | Note references a decision |
| **referenced_by** | Someone links TO this | Auto-tracked from references |
| **depends_on** | This needs another first | Feature depends on API spec |
| **blocks** | This blocks another | Release blocked by tests |

### Example Relationship Graph

```
Meeting Notes (2026-04-11)
    ↓ references
Decision: Tool Selection
    ↓ depends_on
Reference: Multi-dimensional Index Design
    ↓ references
Entry: Personal KB Template
    ↓ created_from
Project: Knowledge Base Creation
```

---

## 🎯 Use Cases

### Case 1: Quick Topic Lookup
```markdown
User: "Show me everything about 'knowledge base design'"

System returns:
✓ Notes from 2026-04-11 about KB
✓ Related meeting minutes
✓ Decisions made about tools
✓ Projects using this concept
```

### Case 2: Follow-up Reminder
```markdown
User: "What tasks from last week need follow-up?"

System returns:
✓ Meetings from last week with action items
✓ All references to those meetings
✓ Tasks marked as 'review' status
```

### Case 3: Cross-reference Discovery
```markdown
User: "Show me all connections to 'permission system'"

System returns:
✓ Direct references from other notes
✓ Related projects
✓ People mentioned in those contexts
✓ Timeline evolution
```

---

## ⚙️ Adding New Entries

### Via CLI Command
```bash
python scripts/add_entry.py --title "New note" \n    --type note --topic "Technology" \n    --project "Personal KB" --person "myself"
```

### Interactive Mode
```bash
python scripts/add_entry.py --interactive
```
Prompts for details and auto-fills metadata

### Quick Add from Terminal
```bash
# Create entry with minimal info
./quick-add.sh "Meeting with team" \n    --meeting --person "myself,team" \n    --date today
```

---

## 🔍 Searching & Querying

### By Topic
```bash
python scripts/search_kb.py --topic "Technology"
```
Returns all entries tagged with Technology

### By Project
```bash
python scripts/search_kb.py --project "Personal KB"
```
Finds all work related to this project

### By Person
```bash
python scripts/search_kb.py --person "孙鑫"
```
Shows all entries mentioning this person

### Combined Filters
```bash
python scripts/search_kb.py \n    --topic "Technology" \n    --project "KB Creation" \n    --date-range 2026-04-01 2026-04-15
```

### Full-text Search
```bash
python scripts/search_kb.py --query "relationship indexing"
```
Searches content body for keywords

---

## 📈 Generating Reports

### Summary Report
```bash
python scripts/generate_report.py --type summary --output report-2026-04.md
```
Creates overview of all knowledge

### Project Status
```bash
python scripts/generate_report.py --type project-status --project "KB Creation"
```
Current state and pending actions

### Relationship Map
```bash
python scripts/generate_report.py --type relationships --format mermaid
```
Visual graph of connected knowledge

---

## 💡 Best Practices

### 1. Be Consistent
- Use same naming conventions for topics/projects
- Keep person names uniform ("myself" vs "me")
- Stick to ISO date format (YYYY-MM-DD)

### 2. Link Liberally
- Connect related notes immediately
- Document why you're linking
- Review links when updating content

### 3. Tag Wisely
- Limit to 3-7 tags per entry
- Prefer broad categories over specific ones
- Review unused tags quarterly

### 4. Status Discipline
- Always mark status when adding
- Update status when things change
- Archive old drafts regularly

### 5. Regular Maintenance
- Weekly: Review and update status
- Monthly: Clean up stale links
- Quarterly: Merge duplicate entries

---

## 🚀 Getting Started

### 1. Initialize your first entry
```bash
mkdir -p personal-knowledge-base/data/notes
cd personal-knowledge-base
python scripts/add_entry.py --init
```

### 2. Add your first knowledge item
```bash
python scripts/add_entry.py \n    --title "Meeting: Team Sync" \n    --type meeting \n    --topic "Communication" \n    --person "myself,team"
```

### 3. Build relationships
Edit the JSON and add reference IDs:
```json
"relationships": {
  "references": ["entry-uuid-from-another-note"]
}
```

### 4. Start searching
```bash
python scripts/search_kb.py --all
```
See everything you've collected!

---

## 📚 Additional Resources

- [index-structure-template.md](references/index-structure-template.md) - Index file schemas
- [entry-format-example.md](references/entry-format-example.md) - Sample filled entries
- [search-syntax-guide.md](references/search-syntax-guide.md) - Advanced search operators

---

## ⚠️ Important Notes

- **Don't over-index:** Only use dimensions that make sense for your context
- **Keep it simple:** Start with core dimensions, expand as needed
- **Manual links ok:** Not all relationships will be discoverable automatically
- **Privacy matters:** Be careful with sensitive information storage

## Resources (optional)

Create only the resource directories this skill actually needs. Delete this section if no resources are required.

### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.

**Examples from other skills:**
- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation
- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by Codex for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform Codex's process and thinking.

**Examples from other skills:**
- Product management: `communication.md`, `context_building.md` - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Codex should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the output Codex produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

**Not every skill requires all three types of resources.**
