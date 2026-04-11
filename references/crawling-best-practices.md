# Web Crawling Best Practices

## Ethical Considerations

When learning web content, always follow these principles:

### 1. Respect robots.txt

Always check a site's `robots.txt` file before crawling:

```
https://example.com/robots.txt
```

Common directives:
- `Disallow: /admin/` - Don't crawl admin pages
- `Disallow: /private/*` - Exclude private sections
- `User-agent: *` - Applies to all bots
- `Sitemap: https://example.com/sitemap.xml` - Helpful for discovery

**Our crawler automatically respects robots.txt.**

---

### 2. Rate Limiting

Be polite to servers by limiting request frequency:

| Scenario | Recommended Delay |
|----------|-------------------|
| Small documentation site | 500ms - 1s between requests |
| Large enterprise site | 1s - 2s |
| Unknown/unfamiliar site | Start with 2s, adjust based on response |

**Why?** Too many rapid requests can:
- Overload the server
- Trigger DDoS protection/bans
- Get your IP blocked
- Be considered abusive behavior

**This skill uses configurable delays:**
```python
delay_between_requests = 0.5  # Default: 500ms
```

---

### 3. Identify Yourself

If you're doing large-scale learning:

```python
# Set custom User-Agent header
headers = {
    'User-Agent': 'MySiteLearner/1.0 (your@email.com)'
}
```

This helps site owners identify and contact you if needed.

---

### 4. Handle Errors Gracefully

Accept that not all links will work:

- **404 Not Found:** Page was moved or deleted
- **403 Forbidden:** Access restricted
- **503 Service Unavailable:** Server temporarily down
- **Timeout:** Network issues

**Best practice:** Log failures but continue crawling other paths.

---

## Technical Best Practices

### URL Normalization

Convert URLs to consistent format to avoid duplicates:

```python
# These are the same page:
"https://example.com/docs/api"
"https://example.com/docs/api/"
"http://example.com/docs/api"  # vs https

# Always normalize to:
"https://example.com/docs/api"
```

Techniques:
- Remove trailing slashes
- Force HTTPS over HTTP
- Resolve relative URLs properly
- Strip query parameters if irrelevant

---

### Relative vs Absolute URLs

Proper handling is critical:

```html
<!-- Relative paths -->
<a href="/docs">Docs</a>           → Resolves to base URL + /docs
<a href="api/reference">API</a>    → Resolves to current dir + api/reference
<a href="../faq">FAQ</a>           → Goes up one level

<!-- Absolute paths -->
<a href="https://other-site.com">External</a>

<!-- Fragment-only (skip) -->
<a href="#section">Jump</a>        → No actual page
```

**Our crawler resolves all relative paths to absolute URLs.**

---

### Content Extraction Strategies

#### Prioritize Semantic HTML

```html
<!-- Good: Use semantic elements -->
<article>                          ← Primary content container
<main>                             ← Main document content
<section class="content"></section>

<!-- Avoid including these in content -->
<nav>                              ← Navigation menu
<header>                           ← Site header
<footer>                           ← Site footer
aside>                            ← Sidebar content
```

#### Clean JavaScript-Generated Content

Some sites render content with JavaScript. Options:

1. **Static HTML only** (fastest, skips dynamic content)
2. **Headless browser** (slower, captures full rendered page)
   - Tools: Puppeteer, Playwright, Selenium
3. **Fetch API calls directly** (if known endpoints)

**This skill uses static extraction first, fallback options available.**

---

## Cycle Detection

Prevent infinite loops when pages link back to themselves:

```
Page A ──→ Page B ──→ Page C
   ↑                      │
   └──────────────────────┘
         (cycle!)
```

**Detection algorithm:**
```python
visited = set()
queue = [starting_url]

while queue:
    url = queue.pop(0)
    
    if url in visited:
        continue  # Skip cycles
    
    visited.add(url)
    # Process this page...
```

**Additional detection:** Track recursion depth and stop at max limit.

---

## Link Quality Assessment

Not all links are equal. Prioritize important ones:

### High Priority Links
- Internal navigation (site map, breadcrumbs)
- Section headers with related links
- Related articles/articles at bottom of post
- API endpoint references in docs

### Low Priority / Skip
- Social media icons
- Copyright/footer links
- Search bars (no href or javascript:)
- Login/logout buttons
- Pagination "next" pages (unless explicitly requested)

---

## Domain Boundary Management

Decide whether to stay within scope:

### Same-Domain Only (Recommended)
```
Starting: https://docs.mycompany.com/start
Crawls:   All *.mycompany.com pages
Skips:    blog.external.com, support.thirdparty.io
```

**Benefits:**
- Keeps learning focused
- Avoids accidental off-topic crawling
- Respects external site boundaries

### Allow External Links
Only when intentionally mapping cross-references:

**Use case:** Understanding how different resources relate

**Risks:**
- Can spiral into entire internet
- Takes much longer
- May encounter paywalled/private content

---

## Storage Efficiency

Learning thousands of pages requires smart storage:

### Compression
Store content compressed:
```json
{
  "url": "...",
  "content_compressed": "<base64_zlib_encoded>",
  "word_count": 2847
}
```

### Incremental Updates
Only re-crawl changed pages:
```python
# Check last modified timestamp
if page.last_modified < cached_last_modified:
    skip_update()
else:
    fetch_new_content()
```

### Metadata-Only Cache
For reference during sessions:
```json
{
  "url": "...",
  "title": "...",
  "summary": "...",
  "link_count": 15
}
# Full content stored separately or loaded on demand
```

---

## Legal Considerations

### Terms of Service
Always review website's ToS:
- Some prohibit automated scraping
- Some require explicit permission
- Commercial use may need licensing

### Copyright
Learned content is for your understanding, not redistribution:
- ✅ Personal knowledge enhancement ✓
- ❌ Republishing content ✗
- ❌ Training commercial models without consent ⚠️

### GDPR/Privacy
Avoid scraping personal data:
- User profiles
- Comments with PII
- Contact forms
- Private messages

---

## Troubleshooting Common Issues

### Issue: Getting blocked/IP banned
**Solution:** 
- Increase delay between requests
- Add User-Agent identification
- Try from different network

### Issue: Pages load slowly
**Solution:**
- Increase timeout value
- Process smaller batches
- Prioritize most relevant pages first

### Issue: Missing JavaScript content
**Solution:**
- Enable headless browser mode
- Fetch specific API endpoints directly
- Accept that some modern sites require JS rendering

### Issue: Infinite loop detected
**Solution:**
- Verify cycle detection working
- Check max_depth setting
- Review exclusion patterns

---

## Tools & Resources

### Popular Crawling Libraries
- **Python**: `requests`, `aiohttp`, `BeautifulSoup`, `Scrapy`
- **JavaScript**: `puppeteer`, `playwright`, `cheerio`
- **CLI**: `wget`, `curl`, `httrack`

### Testing & Debugging
- **Browser DevTools**: Inspect network requests
- **Postman**: Test API endpoints
- **robots.txt tester**: Google's tool

### Monitoring
- Log every request made
- Track success/failure rates
- Monitor bandwidth usage

---

**Remember:** Being a good web citizen means crawling responsibly. When in doubt, ask permission!
