"""Example: Recursively crawl a website

This example shows how to recursively crawl a website by following links.

⚠️  WARNING: Use with caution!
- Can be slow for large sites
- May hit rate limits
- Can load duplicate pages
- Should set depth limit

Use sitemap method instead if available (web_scraping_sitemap.py)

Usage:
    uv run python examples/web_scraping_recursive.py
"""

import os
import sys
from datetime import datetime
from typing import List, Set
from urllib.parse import urljoin, urlparse
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ragsystem import RAGSystem
import requests
from bs4 import BeautifulSoup


class RecursiveWebCrawler:
    """Recursively crawl a website."""

    def __init__(self, base_url: str, max_depth: int = 2, max_pages: int = 50, delay: float = 1.0):
        """
        Initialize crawler.

        Args:
            base_url: Starting URL (e.g., https://example.com)
            max_depth: Maximum depth to crawl (0 = only base, 1 = base + direct links, etc.)
            max_pages: Maximum total pages to crawl
            delay: Delay between requests in seconds (be respectful!)
        """
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.delay = delay

        self.visited: Set[str] = set()
        self.to_visit: List[tuple] = [(base_url, 0)]  # (url, depth)
        self.failed: List[dict] = []

    def is_valid_url(self, url: str) -> bool:
        """Check if URL should be crawled."""
        parsed = urlparse(url)

        # Must be same domain
        if parsed.netloc != self.domain:
            return False

        # Skip common non-content pages
        skip_patterns = [
            '/login', '/signin', '/signup', '/register',
            '/cart', '/checkout', '/account',
            '.pdf', '.jpg', '.jpeg', '.png', '.gif',
            '.zip', '.tar', '.gz',
            '#', 'javascript:', 'mailto:'
        ]

        url_lower = url.lower()
        for pattern in skip_patterns:
            if pattern in url_lower:
                return False

        return True

    def get_links(self, url: str, html: str) -> List[str]:
        """Extract links from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        links = []

        for a in soup.find_all('a', href=True):
            href = a['href']
            # Convert relative URLs to absolute
            absolute_url = urljoin(url, href)
            # Remove fragments
            absolute_url = absolute_url.split('#')[0]

            if self.is_valid_url(absolute_url):
                links.append(absolute_url)

        return list(set(links))  # Deduplicate

    def crawl(self) -> List[str]:
        """
        Crawl the website.

        Returns:
            List of successfully crawled URLs
        """
        print(f"🕷️  Starting recursive crawl from: {self.base_url}")
        print(f"   Max depth: {self.max_depth}")
        print(f"   Max pages: {self.max_pages}")
        print(f"   Delay: {self.delay}s between requests\n")

        crawled_urls = []

        while self.to_visit and len(self.visited) < self.max_pages:
            url, depth = self.to_visit.pop(0)

            # Skip if already visited
            if url in self.visited:
                continue

            # Skip if max depth exceeded
            if depth > self.max_depth:
                continue

            # Mark as visited
            self.visited.add(url)

            # Crawl the page
            try:
                print(f"[{len(self.visited)}/{self.max_pages}] Depth {depth}: {url}")

                response = requests.get(url, timeout=10)
                response.raise_for_status()

                # Extract links if not at max depth
                if depth < self.max_depth:
                    links = self.get_links(url, response.text)
                    print(f"  → Found {len(links)} links")

                    # Add new links to queue
                    for link in links:
                        if link not in self.visited:
                            self.to_visit.append((link, depth + 1))

                crawled_urls.append(url)

                # Be respectful - delay between requests
                time.sleep(self.delay)

            except Exception as e:
                print(f"  ❌ Failed: {str(e)[:50]}")
                self.failed.append({'url': url, 'error': str(e)})

        print(f"\n✓ Crawled {len(crawled_urls)} pages")
        print(f"✓ Found {len(self.to_visit)} more URLs (not visited due to limits)")

        return crawled_urls


def load_website_recursive(base_url: str, max_depth: int = 2, max_pages: int = 50):
    """
    Recursively crawl and load a website.

    Args:
        base_url: Starting URL
        max_depth: Maximum crawl depth
        max_pages: Maximum pages to load
    """
    print("="*80)
    print("WEBSITE SCRAPING - RECURSIVE METHOD")
    print("="*80 + "\n")

    # Crawl website
    crawler = RecursiveWebCrawler(base_url, max_depth, max_pages, delay=1.0)
    urls = crawler.crawl()

    if not urls:
        print("❌ No URLs crawled")
        return

    # Initialize RAG system
    print("\n" + "="*80)
    print("LOADING INTO CHROMADB")
    print("="*80 + "\n")

    rag = RAGSystem(persist_directory="outputs/chroma_db", collection_name="website_docs")

    # Load each URL
    successful = 0
    failed = []

    for i, url in enumerate(urls, 1):
        try:
            print(f"[{i}/{len(urls)}] Loading: {url}")
            chunks = rag.load_website(url)
            successful += 1
            print(f"  ✓ Added {chunks} chunks")
        except Exception as e:
            print(f"  ❌ Failed: {str(e)[:50]}")
            failed.append({'url': url, 'error': str(e)})

    # Summary
    print("\n" + "="*80)
    print("SCRAPING COMPLETE")
    print("="*80)
    print(f"\n✅ Successful: {successful}/{len(urls)}")
    print(f"❌ Failed: {len(failed)}/{len(urls)}")

    # Get stats
    stats = rag.get_stats()
    print(f"\n📊 Total documents in database: {stats['total_documents']}")

    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"outputs/website_crawl_{timestamp}.txt"
    os.makedirs('outputs', exist_ok=True)

    with open(report_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("WEBSITE SCRAPING REPORT - RECURSIVE METHOD\n")
        f.write("="*80 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Base URL: {base_url}\n")
        f.write(f"Max depth: {max_depth}\n")
        f.write(f"Pages loaded: {successful}/{len(urls)}\n")
        f.write(f"Total chunks: {stats['total_documents']}\n\n")
        f.write("Crawl Statistics:\n")
        f.write(f"  - Pages visited: {len(crawler.visited)}\n")
        f.write(f"  - Pages not visited: {len(crawler.to_visit)}\n")
        f.write(f"  - Failed during crawl: {len(crawler.failed)}\n\n")
        f.write("URLs Loaded:\n")
        for url in urls:
            f.write(f"  - {url}\n")
        if failed:
            f.write("\nFailed to Load:\n")
            for item in failed:
                f.write(f"  - {item['url']}: {item['error']}\n")
        f.write("="*80 + "\n")

    print(f"\n✓ Report saved to: {report_file}")

    # Test query
    print("\n" + "="*80)
    print("TEST QUERY")
    print("="*80 + "\n")

    query = "What is this website about?"
    print(f"Query: {query}")
    answer = rag.query(query, top_k=5, max_tokens=200)
    print(f"\nAnswer:\n{answer}")


if __name__ == "__main__":
    print("⚠️  RECURSIVE WEB CRAWLING")
    print("\nThis method:")
    print("  ⚠️  Can be slow (follows all links)")
    print("  ⚠️  May hit rate limits (many requests)")
    print("  ⚠️  Can load duplicates")
    print("  ⚠️  Requires depth limits")
    print()
    print("💡 TIP: Use sitemap method instead if available!")
    print("   (See web_scraping_sitemap.py)")
    print()

    # Get URL from user
    base_url = input("Enter website URL to crawl: ").strip()

    if not base_url:
        print("❌ No URL provided")
        sys.exit(1)

    # Ensure URL has scheme
    if not base_url.startswith(('http://', 'https://')):
        base_url = 'https://' + base_url

    # Get parameters
    max_depth_input = input("Max depth (default 2, recommended: 1-3): ").strip()
    max_depth = int(max_depth_input) if max_depth_input else 2

    max_pages_input = input("Max pages (default 50, recommended: 20-100): ").strip()
    max_pages = int(max_pages_input) if max_pages_input else 50

    # Warning for large crawls
    if max_depth > 3 or max_pages > 100:
        confirm = input("⚠️  This may take a long time. Continue? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled")
            sys.exit(0)

    # Crawl website
    load_website_recursive(base_url, max_depth, max_pages)

    print("\n" + "="*80)
    print("✅ DONE - Website loaded into ChromaDB")
    print("="*80)
    print("\nYou can now query this website using:")
    print("  ./start_gradio.sh")
    print("\nOr in Python:")
    print("  rag = RAGSystem(persist_directory='outputs/chroma_db', collection_name='website_docs')")
    print("  answer = rag.query('your question')")
