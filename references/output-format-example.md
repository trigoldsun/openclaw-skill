# Web Learning Output Format Example

## Complete Report Structure

This document shows a sample output from the website learning system.

---

## JSON Format (Machine-Readable)

```json
{
  "summary": {
    "start_url": "https://docs.example.com/getting-started",
    "pages_learned": 15,
    "total_bytes": 487392,
    "duration_seconds": 12.4,
    "stats": {
      "by_type": {
        "documentation": 8,
        "tutorial": 4,
        "informational": 2,
        "product": 1
      },
      "avg_depth": 1.8,
      "external_links_excluded": 7,
      "cycles_detected": 2
    }
  },
  "pages": [
    {
      "url": "https://docs.example.com/getting-started",
      "title": "Getting Started - Example Docs",
      "type": "documentation",
      "depth": 0,
      "links_out": 12,
      "links_in": 0
    },
    {
      "url": "https://docs.example.com/api/overview",
      "title": "API Overview",
      "type": "documentation",
      "depth": 1,
      "links_out": 8,
      "links_in": 1
    },
    {
      "url": "https://docs.example.com/tutorials/hello-world",
      "title": "Hello World Tutorial",
      "type": "tutorial",
      "depth": 1,
      "links_out": 5,
      "links_in": 2
    },
    {
      "url": "https://docs.example.com/api/authentication",
      "title": "Authentication API",
      "type": "documentation",
      "depth": 2,
      "links_out": 6,
      "links_in": 1
    }
  ],
  "graph": {
    "https://docs.example.com/getting-started": [
      "https://docs.example.com/api/overview",
      "https://docs.example.com/tutorials/hello-world",
      "https://docs.example.com/product/pricing"
    ],
    "https://docs.example.com/api/overview": [
      "https://docs.example.com/api/authentication",
      "https://docs.example.com/api/endpoints"
    ]
  }
}
```

---

## Markdown Format (Human-Readable)

# 🌐 Web Learning Report

**Start URL:** https://docs.example.com/getting-started  
**Pages Learned:** 15  
**Total Size:** 487,392 bytes  
**Duration:** 12.4 seconds  

## Pages by Type

- documentation: 8
- tutorial: 4
- informational: 2
- product: 1

## Detailed Page List

### Level 0 (Starting Page)

**1.** [Getting Started - Example Docs](https://docs.example.com/getting-started)
   - Type: documentation
   - Depth: 0
   - Outbound links: 12
   - Inbound links: 0

### Level 1 (Direct Children)

**2.** [API Overview](https://docs.example.com/api/overview)
   - Type: documentation
   - Depth: 1
   - Outbound links: 8
   - Inbound links: 1

**3.** [Hello World Tutorial](https://docs.example.com/tutorials/hello-world)
   - Type: tutorial
   - Depth: 1
   - Outbound links: 5
   - Inbound links: 2

**4.** [Product Pricing](https://docs.example.com/product/pricing)
   - Type: product
   - Depth: 1
   - Outbound links: 3
   - Inbound links: 1

### Level 2 (Grandchildren)

**5.** [Authentication API](https://docs.example.com/api/authentication)
   - Type: documentation
   - Depth: 2
   - Outbound links: 6
   - Inbound links: 1

**6.** [Rate Limiting Guide](https://docs.example.com/api/rate-limiting)
   - Type: documentation
   - Depth: 2
   - Outbound links: 4
   - Inbound links: 0

... (continues for all 15 pages)

## Link Network Analysis

### Most Connected Pages

| Page | Outbound Links | Inbound Links | Centrality Score |
|------|---------------|---------------|------------------|
| Getting Started | 12 | 0 | High |
| API Overview | 8 | 1 | High |
| Hello World | 5 | 2 | Medium |
| Authentication | 6 | 1 | Medium |

### Discovery Path Examples

**To reach Authentication API:**
```
Getting Started → API Overview → Authentication API
```

**To reach Rate Limiting:**
```
Getting Started → API Overview → Authentication API → Rate Limiting Guide
```

## Content Summary

### Key Topics Covered

Based on title and structure analysis:

1. **Getting Started** (Foundation)
   - Installation instructions
   - Quick start guide
   - Account setup

2. **API Documentation** (Core Feature)
   - Overview and concepts
   - Authentication methods
   - Endpoint reference
   - Error handling

3. **Tutorials** (Learning Path)
   - Hello World example
   - Common use cases
   - Best practices

4. **Product Info** (Business Context)
   - Pricing tiers
   - Feature comparison

## Audit Trail

### Operation Log

```
Step 1: crawl_initiated
   Purpose: Starting crawl from https://docs.example.com/getting-started
   Result: Max depth set to 3

Step 2: fetch_start
   Purpose: Fetching starting page
   Result: Success - HTML received (24KB)

Step 3: page_learned
   Purpose: Learned initial page
   Result: Type: documentation, Links found: 12

Step 4-18: recursive_crawling
   Purpose: Following all outbound links
   Result: 14 additional pages learned

Step 19: crawl_complete
   Purpose: Finalize and generate report
   Result: 15 total pages in 12.4s

=== WEB LEARNING AUDIT LOG ===
```

---

## How to Interpret the Data

### Understanding Depth Levels

- **Depth 0:** Starting page you provided
- **Depth 1:** Directly linked from starting page
- **Depth 2:** Linked from depth 1 pages
- **Deeper:** Continue following the chain

### Centrality Scores

- **High:** Hub pages (many incoming + outgoing links)
- **Medium:** Important but specialized
- **Low:** Edge/niche content

### Why External Links Excluded?

Example stats show `external_links_excluded: 7` means:
- Crawler found 7 links to other domains
- Respected `restrict_to_same_domain` setting
- Could disable this if cross-domain mapping needed

### Cycle Detection

`cycles_detected: 2` means:
- Found 2 pages that created potential infinite loops
- Automatically skipped to prevent crash
- No data loss occurred

---

## Next Steps After Learning

Once you've learned a site, you can:

1. **Ask questions about specific content:**
   > "What are the authentication methods mentioned?"

2. **Compare information across pages:**
   > "How does the pricing differ between plans?"

3. **Find related topics:**
   > "Show me all pages related to API configuration"

4. **Identify gaps:**
   > "What important topics seem missing from this docs?"

---

## Customizing Output

You can modify the output format by changing the crawler options:

```python
crawler = FullSiteCrawler(logger, {
    'output_format': 'markdown',  # or 'json'
    'include_content_summary': True,
    'min_word_count': 100  # Skip very short pages
})
```

See `scripts/website_crawler.py` for full configuration options.
