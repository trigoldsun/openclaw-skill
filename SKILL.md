---
name: web-site-learning
description: Comprehensive full-site webpage learning system. Provide any starting URL → I automatically crawl all upstream/downstream linked pages recursively, extracting and memorizing complete content from every page discovered within the site network. Supports configurable depth limits, exclusion patterns, and intelligent cycle detection.
---

# 🌐 Full-Site Webpage Learning System

## Overview

Give me **any starting webpage URL**, and I will recursively learn **all connected pages** within that site — following every link forward (downstream) and backward (upstream) until the entire accessible network is memorized.

Perfect for understanding documentation sites, knowledge bases, product catalogs, or any linked information network.

---

## 📊 How It Works

```
You provide: https://example.com/docs/start-page
                    │
                    ▼
        ┌─────────────────────┐
        │  Step 1: Learn      │
        │  Main Page          │
        └─────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌───────┐     ┌───────┐       ┌───────┐
│Page A │     │Page B │       │Page C │
└───────┘     └───────┘       └───────┘
    │             │               │
    └──────┬──────┴────────┬──────┘
           ▼               ▼
     ┌─────────────────────────┐
     │ Continue Following All  │
     │ Links Until Complete    │
     └─────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │   Final Report  │
         │ Summary Learned │
         └─────────────────┘
```

---

## 🎯 Use Cases

### Scenario 1: Documentation Site Understanding
```markdown
User: "Here's our new API docs: https://api.example.com/docs
       Please learn all of it so you can answer questions"

Result: I've learned 87 pages across 5 major sections
        → Now I can answer detailed questions about any endpoint
```

### Scenario 2: Competitor Analysis
```markdown
User: "Analyze their product site:
       https://competitor.com/products"

Result: Mapped entire product catalog (45 pages),
        compared feature lists, extracted pricing tiers,
        identified positioning strategies
```

### Scenario 3: Knowledge Base Migration
```markdown
User: "This legacy wiki needs reviewing:
       https://wiki.internal.company.com/start"

Result: Inventory of 200+ articles created,
        content gaps identified, updated recommendations generated
```

---

## 🔧 Configuration Options

### Depth Control
```python
# How many "hops" from the starting page
max_depth = 1  # Only direct children
max_depth = 3  # Grandchildren included (default)
max_depth = 99 # Unlimited until cycles detected
```

### Scope Filtering
```python
# Include only specific path patterns
include_patterns = ['/docs/*', '/api/*']

# Exclude certain sections
exclude_patterns = ['/admin/*', '/private/*']
```

### Domain Constraints
```python
# Stay within same domain
restrict_to_same_domain = True

# Or follow external links too
allow_external_links = False  # Recommended
```

---

## 🛠️ Learning Process Pipeline

### Phase 1: Initial Analysis
1. **Fetch starting URL**
2. **Extract page metadata:**
   - Title, description, H1 heading
   - Number and quality of outbound links
   - Content type (documentation, article, product, etc.)
3. **Build initial index**

### Phase 2: Recursive Crawling
1. **Parse HTML structure**
   - Extract all anchor tags (`<a href="...">`)
   - Filter valid URLs (avoid broken, mailto:, javascript:)
   - Resolve relative paths to absolute URLs
2. **Quality validation:**
   - Skip non-HTML pages (PDFs, images)
   - Skip authentication-required pages
   - Skip robots.txt exclusions
3. **Content extraction:**
   - Clean HTML → Markdown conversion
   - Extract semantic elements (article, nav, main)
   - Preserve table structures
   - Capture image alt text

### Phase 3: Cycle Detection & Prevention
```python
visited_urls = set()
crawl_stack = [starting_url]

while crawl_stack:
    current_url = crawl_stack.pop()
    
    if current_url in visited_urls:
        continue  # Avoid infinite loops
    
    visited_urls.add(current_url)
    
    # Extract links and add to stack
    for link in extract_outbound_links(current_url):
        if should_crawl(link) and link not in visited_urls:
            crawl_stack.append(link)
```

### Phase 4: Relationship Mapping
Build directed graph of page connections:

```
Page A ──[link]──> Page B
  │                    │
  │                    └──> Page D
  │
  └──> Page C ──────┘
```

Track:
- **Inbound count:** How many pages link TO this page
- **Outbound count:** How many pages THIS page links TO
- **Centrality score:** Hub pages vs isolated pages

### Phase 5: Memory Storage Format
Each learned page stored as structured JSON:

```json
{
  "url": "https://example.com/docs/api/authentication",
  "title": "Authentication API Reference",
  "content": { ...cleaned markdown... },
  "metadata": {
    "word_count": 2847,
    "heading_count": 23,
    "link_count": 15
  },
  "links": {
    "outbound": [
      "https://example.com/docs/api/overview",
      "https://example.com/docs/api/errors"
    ],
    "inbound": [
      "https://example.com/docs/getting-started",
      "https://example.com/docs/tutorials"
    ]
  },
  "crawl_info": {
    "depth_from_start": 2,
    "discovered_at": "2026-04-11T12:00:00Z",
    "status": "success"
  }
}
```

---

## 📝 Reporting Format

Following established protocol, every learning session includes:

```
## [Step Number] · [Operation Name]

**目的：** [Why we're doing this]

**操作细节：**
- Input: [URLs processed, pages fetched]
- Process: [Extraction method used]
- Output: [Pages learned, links mapped]

**审计记录：**
- Timestamp: [ISO timestamp]
- Pages Count: [N pages processed]
- Status: [Success/Failure details]
```

---

## 🚀 Quick Start Examples

### Example 1: Basic Usage (Recommended)
```markdown
User: "Learn this documentation site:
       https://docs.mycompany.com/start"

Skill automatically:
✓ Identifies project type (documentation)
✓ Crawls with default depth=3
✓ Stays within mycompany.com domain
✓ Generates comprehensive report
```

### Example 2: Custom Depth
```markdown
User: "Deep dive into this API docs with max 5 levels deep:
       https://api.platform.io/reference"

Configure:
- max_depth: 5
- include: [/reference/*, /guides/*]
```

### Example 3: Selective Learning
```markdown
User: "Only learn the tutorials section:
       https://learn.example.com/tutorials"

Exclude patterns:
- exclude: ['/tutorials/completed/*']
```

---

## ⚙️ Automation Script

See `scripts/website_crawler.py` for full implementation:
- Concurrent crawling with rate limiting
- intelligent retry logic
- Content quality scoring
- Graph visualization output

---

## 📚 Additional Resources

- [crawling-best-practices.md](references/crawling-best-practices.md) - Best practices for ethical web scraping
- [html-parsing-guide.md](references/html-parsing-guide.md) - DOM parsing strategies
- [output-format-example.md](references/output-format-example.md) - Sample learning reports

---

## 💡 Pro Tips

1. **Start from high-level hub pages** – Better coverage than drilling down from individual articles
2. **Use sitemap.xml when available** – Faster than discovering links
3. **Respect robots.txt** – Always check before crawling
4. **Add delays between requests** – Be polite to servers (recommended: ≥500ms delay)
5. **Bookmark important pages** – Mark critical docs for quick reference later

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
