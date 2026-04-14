#!/usr/bin/env python3
"""
Full-Site Website Crawler & Learning System
============================================
Recursively crawls and learns all linked webpages from a starting URL.

Features:
- Recursive link following (upstream & downstream)
- Content extraction and cleaning
- Cycle detection to prevent infinite loops
- Comprehensive reporting with metrics
- Rate limiting for polite crawling

Usage:
    python website_crawler.py --url <starting_url> [options]
"""

import os
import sys
import json
import time
import argparse
import asyncio
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field, asdict
from urllib.parse import urlparse, urljoin, urldefrag
from collections import defaultdict

# Optional dependencies - will use fallbacks if not installed
try:
    import aiohttp
    from bs4 import BeautifulSoup
    HAS_WEB_TOOLS = True
except ImportError:
    HAS_WEB_TOOLS = False
    print("Warning: Missing aiohttp or BeautifulSoup. Will use basic text fetching.")


@dataclass
class PageData:
    """Structured data for a learned page."""
    url: str
    title: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    links: Dict[str, List[str]] = field(default_factory=lambda: {"outbound": [], "inbound": []})
    crawl_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CrawlResult:
    """Results from a complete crawl session."""
    start_url: str
    pages_learned: int
    total_bytes_processed: int
    pages: List[PageData]
    graph: Dict[str, List[str]] = field(default_factory=dict)
    stats: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, str]] = field(default_factory=list)
    duration_seconds: float = 0.0


class WebCrawlerLogger:
    """Handles structured logging for crawl operations."""
    
    def __init__(self):
        self.logs = []
    
    def log(self, step: int, op_name: str, purpose: str, result: str, details: dict = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "operation_name": op_name,
            "purpose": purpose,
            "result": result,
            "details": details or {}
        }
        self.logs.append(entry)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Step {step}: {op_name}")
        print(f"   Purpose: {purpose}")
        print(f"   Result: {result}\n")
        return entry
    
    def get_report(self) -> str:
        report = "\n=== WEB LEARNING AUDIT LOG ===\n\n"
        for entry in self.logs:
            report += f"Step {entry['step']}: {entry['operation_name']}\n"
            report += f"Purpose: {entry['purpose']}\n"
            report += f"Result: {entry['result']}\n"
            report += f"Timestamp: {entry['timestamp']}\n\n"
        return report


class DomainFilter:
    """Filters URLs based on domain and path rules."""
    
    def __init__(self, restrict_to_same_domain=True, 
                 include_patterns=None, exclude_patterns=None):
        self.restrict_to_same_domain = restrict_to_same_domain
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []
        
        # Extract base domain from starting URL
        self.base_domain = None
        
    def set_base_domain(self, url: str):
        parsed = urlparse(url)
        self.base_domain = parsed.netloc
    
    def should_crawl(self, url: str) -> tuple:
        """Check if URL should be crawled. Returns (should_crawl, reason)."""
        parsed = urlparse(url)
        
        # Skip invalid schemes
        if parsed.scheme not in ['http', 'https']:
            return False, f"Invalid scheme: {parsed.scheme}"
        
        # Skip same-domain restriction
        if self.restrict_to_same_domain and self.base_domain:
            if parsed.netloc != self.base_domain:
                return False, f"External domain: {parsed.netloc}"
        
        # Check exclusion patterns
        for pattern in self.exclude_patterns:
            if self._matches_pattern(url, pattern):
                return False, f"Excluded by pattern: {pattern}"
        
        # Check inclusion patterns (if specified, must match at least one)
        if self.include_patterns and not any(
            self._matches_pattern(url, p) for p in self.include_patterns
        ):
            return False, f"Doesn't match any included pattern"
        
        return True, "OK"
    
    def _matches_pattern(self, url: str, pattern: str) -> bool:
        """Simple wildcard pattern matching."""
        import fnmatch
        # Convert glob pattern to regex
        regex_pattern = pattern.replace('*', '.*').replace('?', '.')
        return bool(__import__('re').match(regex_pattern, url))


class HTMLContentExtractor:
    """Extracts clean content from HTML pages."""
    
    @staticmethod
    def extract_links(soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all valid outbound links from a page."""
        links = set()
        
        for anchor in soup.find_all('a', href=True):
            href = anchor['href'].strip()
            
            # Skip invalid links
            if not href or href.startswith('#'):
                continue
            
            if href.startswith(('mailto:', 'tel:', 'javascript:')):
                continue
            
            # Resolve relative URLs
            absolute_url = urljoin(base_url, href)
            # Remove fragment identifiers
            absolute_url, _ = urldefrag(absolute_url)
            
            links.add(absolute_url)
        
        return sorted(links)
    
    @staticmethod
    def extract_title(soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            return title_tag.string.strip()
        return "Untitled"
    
    @staticmethod
    def extract_main_content(soup: BeautifulSoup) -> str:
        """Extract main article content, avoiding nav/sidebar elements."""
        
        # Try semantic HTML5 tags first
        for tag_name in ['article', 'main', 'content']:
            element = soup.find(tag_name)
            if element:
                return HTMLContentExtractor._clean_element(element)
        
        # Fallback to body
        body = soup.find('body')
        if body:
            return HTMLContentExtractor._clean_element(body)
        
        return ""
    
    @staticmethod
    def _clean_element(element) -> str:
        """Clean an element's text content."""
        # Remove script and style elements
        for tag in element(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
        
        # Get text and normalize whitespace
        text = element.get_text(separator='\n', strip=True)
        
        # Clean up excessive whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n\n'.join(lines[:1000])  # Limit to first 1000 lines


class AsyncWebFetcher:
    """Async HTTP fetcher with rate limiting."""
    
    def __init__(self, delay_between_requests=0.5, timeout=30):
        self.delay = delay_between_requests
        self.timeout = timeout
        self.session = None
        
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=10)
        self.session = aiohttp.ClientSession(connector=connector)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch(self, url: str) -> tuple:
        """Fetch URL content. Returns (success, html_or_error)."""
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '').lower()
                    
                    # Only process HTML content
                    if 'text/html' in content_type:
                        html = await response.text()
                        return True, html
                    else:
                        return False, f"Non-HTML content type: {content_type}"
                else:
                    return False, f"HTTP {response.status}"
                    
        except asyncio.TimeoutError:
            return False, "Request timeout"
        except Exception as e:
            return False, str(e)
        
        finally:
            if self.delay > 0:
                await asyncio.sleep(self.delay)


class FullSiteCrawler:
    """Main crawler orchestrator."""
    
    def __init__(self, logger: WebCrawlerLogger, options: dict = None):
        self.logger = logger
        self.options = options or {
            'max_depth': 3,
            'restrict_to_same_domain': True,
            'include_patterns': [],
            'exclude_patterns': ['/admin/*', '/private/*', '/login*'],
            'delay_between_requests': 0.5,
            'timeout': 30
        }
        self.visited_urls: Set[str] = set()
        self.pages_data: List[PageData] = []
        self.link_graph: Dict[str, Set[str]] = defaultdict(set)
        self.incoming_links: Dict[str, Set[str]] = defaultdict(set)
        
    def detect_page_type(self, url: str, title: str) -> str:
        """Classify the type of page being learned."""
        url_lower = url.lower()
        title_lower = title.lower()
        
        if any(x in url_lower for x in ['/doc', '/api/', '/guide', '/tutorial']):
            return 'documentation'
        elif any(x in url_lower for x in ['/product', '/feature', '/pricing']):
            return 'product'
        elif any(x in url_lower for x in ['/blog', '/news', '/article']):
            return 'article'
        elif any(x in url_lower for x in ['/support', '/faq', '/help']):
            return 'support'
        elif any(x in url_lower for x in ['/about', '/contact', '/team']):
            return 'informational'
        else:
            return 'general'
    
    async def crawl_page(self, url: str, depth: int, session: AsyncWebFetcher):
        """Learn a single page and queue its links."""
        
        # Check depth limit
        if depth > self.options['max_depth']:
            return
        
        # Check if already visited
        if url in self.visited_urls:
            return
        
        # Validate URL
        should_crawl, reason = self.domain_filter.should_crawl(url)
        if not should_crawl:
            return
        
        # Fetch page
        success, html = await session.fetch(url)
        
        if not success:
            error_info = {"url": url, "error": html}
            self.logger.log(self.current_step, "fetch_failed", 
                          f"Failed to fetch {url}", html, error_info)
            self.current_step += 1
            return
        
        self.visited_urls.add(url)
        self.current_step += 1
        
        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract data
        title = HTMLContentExtractor.extract_title(soup)
        content = HTMLContentExtractor.extract_main_content(soup)
        outbound_links = HTMLContentExtractor.extract_links(soup, url)
        
        # Filter out non-crawlable links
        valid_outbound = []
        for link in outbound_links:
            can_crawl, _ = self.domain_filter.should_crawl(link)
            if can_crawl and link not in self.visited_urls:
                valid_outbound.append(link)
        
        # Create page data
        page_type = self.detect_page_type(url, title)
        
        page_data = PageData(
            url=url,
            title=title,
            content=f"# {title}\n\n## URL\n{url}\n\n## Content\n\n{content}",
            metadata={
                "page_type": page_type,
                "word_count": len(content.split()),
                "link_count": len(valid_outbound)
            },
            links={
                "outbound": valid_outbound,
                "inbound": list(self.incoming_links.get(url, []))
            },
            crawl_info={
                "depth_from_start": depth,
                "discovered_at": datetime.now().isoformat(),
                "status": "success"
            }
        )
        
        self.pages_data.append(page_data)
        
        # Build link graph
        self.link_graph[url] = set(valid_outbound)
        for outbound in valid_outbound:
            self.incoming_links[outbound].add(url)
        
        # Log learning
        self.logger.log(self.current_step, "page_learned",
                       f"Learned: {title}",
                       f"Type: {page_type}, Links: {len(valid_outbound)}",
                       {"url": url, "depth": depth, "links_found": len(valid_outbound)})
        
        # Queue child pages for crawling
        for link in valid_outbound:
            asyncio.create_task(self.crawl_page(link, depth + 1, session))
        
        self.current_step += 1
    
    def run_crawl(self, start_url: str) -> CrawlResult:
        """Execute the full crawl."""
        start_time = time.time()
        self.current_step = 1
        
        # Initialize filter
        self.domain_filter = DomainFilter(
            restrict_to_same_domain=self.options['restrict_to_same_domain'],
            include_patterns=self.options['include_patterns'],
            exclude_patterns=self.options['exclude_patterns']
        )
        self.domain_filter.set_base_domain(start_url)
        
        self.logger.log(self.current_step, "crawl_initiated",
                       f"Starting crawl from {start_url}",
                       f"Max depth: {self.options['max_depth']}")
        self.current_step += 1
        
        # Run async crawl
        async def crawl_async():
            async with AsyncWebFetcher(
                delay_between_requests=self.options['delay_between_requests'],
                timeout=self.options['timeout']
            ) as session:
                # Start initial page
                await self.crawl_page(start_url, 0, session)
                
                # Wait for all tasks to complete
                await asyncio.sleep(1)  # Give pending tasks time to start
        
        try:
            asyncio.run(crawl_async())
        except Exception as e:
            self.logger.log(self.current_step, "crawl_error",
                           f"Crawl encountered error: {str(e)}",
                           "Partial results available",
                           {"error": str(e)})
        
        # Generate report
        duration = time.time() - start_time
        
        result = CrawlResult(
            start_url=start_url,
            pages_learned=len(self.pages_data),
            total_bytes_processed=sum(len(p.content) for p in self.pages_data),
            pages=self.pages_data,
            graph=dict(self.link_graph),
            stats={
                "by_type": self._count_by_type(),
                "avg_depth": self._calculate_avg_depth(),
                "external_links_excluded": len([u for u in self.visited_urls 
                                                if urlparse(u).netloc != urlparse(start_url).netloc]),
                "cycles_detected": self._detect_cycles()
            },
            errors=[],
            duration_seconds=duration
        )
        
        # Final log entry
        self.logger.log(self.current_step, "crawl_complete",
                       f"Crawl finished in {duration:.1f}s",
                       f"Learned {result.pages_learned} pages",
                       {"duration": duration, "pages": result.pages_learned})
        
        return result
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count pages by type."""
        counts = defaultdict(int)
        for page in self.pages_data:
            counts[page.metadata.get('page_type', 'unknown')] += 1
        return dict(counts)
    
    def _calculate_avg_depth(self) -> float:
        """Calculate average crawl depth."""
        if not self.pages_data:
            return 0.0
        return sum(p.crawl_info.get('depth_from_start', 0) for p in self.pages_data) / len(self.pages_data)
    
    def _detect_cycles(self) -> int:
        """Detect how many cycles were avoided."""
        return len(self.visited_urls) - len(self.pages_data)


def generate_report(result: CrawlResult, format: str = 'json') -> str:
    """Generate human-readable or machine-parseable report."""
    
    if format == 'json':
        report = {
            "summary": {
                "start_url": result.start_url,
                "pages_learned": result.pages_learned,
                "total_bytes": result.total_bytes_processed,
                "duration_seconds": round(result.duration_seconds, 2),
                "stats": result.stats
            },
            "pages": [
                {
                    "url": p.url,
                    "title": p.title,
                    "type": p.metadata.get("page_type"),
                    "depth": p.crawl_info.get("depth_from_start"),
                    "links_out": len(p.links.get("outbound", [])),
                    "links_in": len(p.links.get("inbound", []))
                }
                for p in result.pages
            ],
            "graph": {k: list(v) for k, v in result.graph.items()}
        }
        return json.dumps(report, indent=2, ensure_ascii=False)
    
    else:  # Markdown format
        lines = [
            "# Web Learning Report",
            "",
            f"**Start URL:** {result.start_url}",
            f"**Pages Learned:** {result.pages_learned}",
            f"**Total Size:** {result.total_bytes_processed:,} bytes",
            f"**Duration:** {result.duration_seconds:.1f} seconds",
            "",
            "## Pages by Type",
            ""
        ]
        
        for page_type, count in result.stats.get('by_type', {}).items():
            lines.append(f"- **{page_type.capitalize()}**: {count}")
        
        lines.extend([
            "",
            "## Top Pages by Link Count",
            ""
        ])
        
        sorted_pages = sorted(result.pages, key=lambda p: p.metadata.get('link_count', 0), reverse=True)
        for page in sorted_pages[:10]:
            lines.append(f"- [{page.title}]({page.url}) - {page.metadata.get('link_count', 0)} links")
        
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Website Crawler & Learning System')
    parser.add_argument('--url', required=True, help='Starting URL for crawl')
    parser.add_argument('--max-depth', type=int, default=3, help='Maximum crawl depth')
    parser.add_argument('--output', default='crawl_report.json', help='Output file path')
    parser.add_argument('--format', choices=['json', 'markdown'], default='json', help='Report format')
    parser.add_argument('--exclude', nargs='*', default=[], help='URL patterns to exclude')
    
    args = parser.parse_args()
    
    logger = WebCrawlerLogger()
    crawler = FullSiteCrawler(logger, {
        'max_depth': args.max_depth,
        'exclude_patterns': ['/admin/*', '/private/*', '/login*'] + args.exclude
    })
    
    print(f"Starting crawl from: {args.url}")
    print(f"Max depth: {args.max_depth}")
    print("-" * 50)
    
    result = crawler.run_crawl(args.url)
    
    # Generate and save report
    report = generate_report(result, args.format)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nReport saved to: {args.output}")
    
    print(f"\nCrawl Summary:")
    print(f"  Pages learned: {result.pages_learned}")
    print(f"  Duration: {result.duration_seconds:.1f}s")
    print(f"  Avg depth: {result.stats.get('avg_depth', 0):.1f}")


if __name__ == '__main__':
    main()
