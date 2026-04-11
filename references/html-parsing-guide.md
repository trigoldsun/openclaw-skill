# HTML Parsing Guide for Content Extraction

## Overview

This guide explains how we parse and extract meaningful content from web pages.

---

## DOM Traversal Strategy

### Priority Order for Content Elements

When extracting main content, search in this order:

```python
# 1. Semantic HTML5 tags (most reliable)
<article>           ← Primary article/content
<main>              ← Main document content
[section class="content"]
[div class="main-content"]

# 2. Common container patterns
[div id="content"]
[div class="post-content"]
[div class="article-body"]

# 3. Last resort
<body> → Extract everything, then filter out noise
```

**Why?** Semantic tags help identify actual vs boilerplate content.

---

## Content Cleaning Process

### Step 1: Remove Non-Content Elements

Delete these elements entirely:

```python
elements_to_remove = [
    'script',      # JavaScript code
    'style',       # CSS styles
    'nav',         # Navigation menus
    'header',      # Site header (often repetitive)
    'footer',      # Site footer
    'aside',       # Sidebars
    'iframe',      # Embedded content
    'noscript'     # Fallback content
]
```

### Step 2: Clean Text Content

```python
def clean_text(text):
    # 1. Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # 2. Remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 3. Strip leading/trailing spaces per line
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]  # Remove empty
    
    return '\n'.join(lines)
```

### Step 3: Preserve Important Structures

#### Tables
Keep table structure intact:

```html
<table>
  <tr><th>Feature</th><th>Free</th><th>Pro</th></tr>
  <tr><td>API Calls</td><td>100/mo</td><td>Unlimited</td></tr>
</table>
```

→ Convert to markdown table:

```markdown
| Feature     | Free    | Pro      |
|-------------|---------|----------|
| API Calls   | 100/mo  | Unlimited|
```

#### Code Blocks
Preserve formatting:

```html
<pre><code>function hello() {
  console.log("Hello!");
}</code></pre>
```

→ Keep as-is with proper indentation

#### Lists
Maintain hierarchy:

```html
<ul>
  <li>Item 1
    <ul>
      <li>Subitem 1a</li>
      <li>Subitem 1b</li>
    </ul>
  </li>
</ul>
```

→ Markdown:

```markdown
- Item 1
  - Subitem 1a
  - Subitem 1b
```

---

## Link Extraction

### Types of Links to Capture

```html
<!-- Absolute URLs (preserve as-is) -->
<a href="https://example.com/docs">Docs</a>

<!-- Relative URLs (resolve to absolute) -->
<a href="/api/reference">API</a>          → https://example.com/api/reference
<a href="../tutorials">Tutorials</a>      → https://example.com/tutorials

<!-- Skip these -->
<a href="#section">Section</a>            ← Fragment only
<a href="mailto:user@example.com">Email</a> ← Mailto
<a href="tel:+1234567890">Call</a>        ← Phone
<a href="javascript:void(0)">Click</a>    ← JS action
```

### Anchor Text Importance

The text inside `<a>` tag tells us what the link is about:

```html
<!-- Good anchor text -->
<a href="/docs/api/authentication">Authentication Reference</a>
                                          ↑ Useful description

<!-- Poor anchor text -->
<a href="/docs/api/authentication">Click here</a>
                                    ↑ Not informative
```

**We store both:** URL + descriptive anchor text for context.

---

## Title Extraction Strategies

### Method Priority

```python
def extract_title(soup):
    # 1. Look for Open Graph title (usually best)
    og_title = soup.find('meta', property='og:title')
    if og_title and og_title.get('content'):
        return og_title['content']
    
    # 2. Standard title tag
    title = soup.find('title')
    if title and title.string:
        return title.string.strip()
    
    # 3. H1 as fallback (if no title)
    h1 = soup.find('h1')
    if h1:
        return h1.get_text(strip=True)
    
    return "Untitled"
```

### Why This Order?

1. **Open Graph:** Designed for social sharing, often more descriptive
2. **Title tag:** Standard HTML definition
3. **H1 heading:** Often similar to title but sometimes more specific

---

## Image Alt Text Handling

Images should have descriptive alt text:

```html
<!-- Good -->
<img src="chart.png" alt="Revenue growth chart showing 20% increase">

<!-- Bad (skip) -->
<img src="img123.jpg" alt="">           ← Empty
<img src="photo.png">                    ← No alt attribute
```

**Action:** Store alt text as part of page content summary.

---

## Handling JavaScript-Rendered Pages

Some modern sites load content dynamically. Our strategy:

### Level 1: Static HTML Only (Default)

Fastest, captures server-rendered content.

**Works for:** Most documentation sites, blogs, standard websites

### Level 2: Headless Browser (Optional)

Slower but gets fully rendered pages.

Tools: Puppeteer, Playwright, Selenium

```python
# Example with Playwright
async def fetch_rendered(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until='networkidle')
        
        # Extract after JS execution
        content = await page.content()
        await browser.close()
        
        return content
```

**Use when:** 
- Content appears after user interaction
- Infinite scroll pagination
- SPA (Single Page Application) routing

### Level 3: API Endpoint Discovery (Advanced)

For sites with known APIs:

```python
# Instead of scraping UI, call API directly
response = requests.get('https://api.example.com/docs/list')
data = response.json()

# Convert to learnable format
for item in data['items']:
    await self.learn_page(item['url'])
```

**Benefits:** Faster, more reliable, less parsing needed

---

## Special Cases Handling

### Pagination

Avoid crawling infinite sequences:

```html
<!-- Skip: Don't crawl all 100+ pages -->
<a href="?page=2">Next →</a>

<!-- Acceptable: Fixed pagination -->
<div class="pagination">
  <a href="page1.html">1</a>
  <a href="page2.html">2</a>
  <a href="page3.html">3</a>
  <span class="current">...</span>
</div>
```

**Strategy:** Only crawl initial page or first N pages.

### Single Page Applications (SPA)

SPAs use URL fragments for routing:

```
https://app.com/#/dashboard
https://app.com/#/settings/profile
```

**Challenge:** All show same HTML, different JS renders

**Solution:** Either:
1. Fetch API endpoints directly
2. Use headless browser for each view
3. Skip SPAs entirely unless critical

### Dynamic Query Parameters

```
https://site.com/products?category=electronics&sort=price
https://site.com/products?category=books&sort=name
```

**Problem:** Same page, different params = duplicate content

**Solution:** Normalize URLs:
```python
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def normalize_url(url):
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # Remove unstable params
    params_to_remove = ['session_id', 'utm_', 'tracking']
    for param in params_to_remove:
        query_params.pop(param, None)
    
    # Rebuild URL without those params
    new_query = urlencode(query_params, doseq=True)
    normalized = urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                             parsed.params, new_query, parsed.fragment))
    
    return normalized
```

---

## Error Handling Examples

### 404 Not Found

```python
try:
    response = await session.fetch(url)
    if response.status == 404:
        log_warning(f"Page not found: {url}")
        continue  # Move to next link
        
except Exception as e:
    log_error(f"Failed to fetch {url}: {e}")
    errors.append({"url": url, "error": str(e)})
```

### Blocked by robots.txt

```python
def check_robots_txt(base_url, user_agent='*'):
    """Check if crawling is allowed."""
    robots_url = f"{base_url}/robots.txt"
    
    try:
        response = requests.get(robots_url)
        if response.status == 200:
            return parse_robots(response.text, user_agent)
    except:
        pass
    
    return True  # Default: allow if can't determine
```

### Rate Limiting (429 Too Many Requests)

```python
if response.status == 429:
    retry_after = response.headers.get('Retry-After', '5')
    await asyncio.sleep(int(retry_after))
    # Retry once
```

---

## Performance Optimization

### Parallel Crawling

Fetch multiple pages concurrently:

```python
async def parallel_fetch(urls, max_concurrent=10):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_with_limit(url):
        async with semaphore:
            return await fetch(url)
    
    tasks = [fetch_with_limit(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results
```

**Benefits:**
- 10x faster than sequential
- Still polite (limit concurrent connections)

### Connection Pooling

Reuse TCP connections:

```python
connector = aiohttp.TCPConnector(limit=50)
session = aiohttp.ClientSession(connector=connector)
```

**Reduces:** DNS lookups, handshake overhead

### Caching Responses

Save fetched HTML locally:

```python
CACHE_DIR = "./crawl_cache"

def cache_get(url):
    filepath = os.path.join(CACHE_DIR, hashlib.md5(url.encode()).hexdigest())
    if os.path.exists(filepath):
        return open(filepath).read()
    return None

def cache_set(url, content):
    filepath = os.path.join(CACHE_DIR, hashlib.md5(url.encode()).hexdigest())
    os.makedirs(CACHE_DIR, exist_ok=True)
    open(filepath, 'w').write(content)
```

---

## Testing Your Parser

### Manual Testing Checklist

For each crawled page, verify:

- [ ] Title extracted correctly
- [ ] Main content readable
- [ ] Navigation/footer excluded
- [ ] Links properly resolved
- [ ] Images have alt text captured
- [ ] Tables preserved
- [ ] Code blocks formatted

### Automated Validation

```python
def validate_extraction(page_data):
    checks = []
    
    # Minimum content length
    checks.append(len(page_data['content']) > 100)
    
    # At least one valid link
    checks.append(len(page_data['links']['outbound']) >= 0)
    
    # Reasonable word count
    word_count = len(page_data['content'].split())
    checks.append(word_count < 50000)  # Sanity check
    
    return all(checks)
```

---

## Tools Mentioned

| Tool | Purpose | Installation |
|------|---------|--------------|
| BeautifulSoup | HTML parsing | `pip install beautifulsoup4` |
| aiohttp | Async HTTP client | `pip install aiohttp` |
| Playwright | Headless browser | `playwright install` |
| lxml | Fast XML/HTML parser | `pip install lxml` |
| cssselect | CSS selector matching | Included with lxml |

---

**Next:** See [output-format-example.md](./output-format-example.md) for sample outputs from this extraction process.
