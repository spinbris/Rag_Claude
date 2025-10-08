"""Example: Load entire website using sitemap.xml

This example shows how to scrape an entire website using its sitemap.
This is the RECOMMENDED approach as it's:
- Fast (parallel loading)
- Respectful (uses site's index)
- Complete (gets all important pages)

Usage:
    uv run python examples/web_scraping_sitemap.py
"""

import os
import sys
from datetime import datetime
from typing import List, Set
import xml.etree.ElementTree as ET

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ragsystem import RAGSystem
import requests


def get_sitemap_urls(sitemap_url: str, max_urls: int = 100) -> List[str]:
    """
    Extract URLs from a sitemap.xml file.

    Args:
        sitemap_url: URL to sitemap.xml (e.g., https://example.com/sitemap.xml)
        max_urls: Maximum number of URLs to extract

    Returns:
        List of URLs from the sitemap
    """
    print(f"📥 Fetching sitemap: {sitemap_url}")

    try:
        response = requests.get(sitemap_url, timeout=10)
        response.raise_for_status()

        # Parse XML
        root = ET.fromstring(response.content)

        # Handle different sitemap formats
        # Standard sitemap namespace
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        urls = []

        # Try to find <loc> tags (URL locations)
        for loc in root.findall('.//ns:loc', namespace):
            if loc.text:
                urls.append(loc.text)
                if len(urls) >= max_urls:
                    break

        # If no URLs found with namespace, try without
        if not urls:
            for loc in root.findall('.//loc'):
                if loc.text:
                    urls.append(loc.text)
                    if len(urls) >= max_urls:
                        break

        # Check for sitemap index (sitemap of sitemaps)
        sitemap_locs = root.findall('.//ns:sitemap/ns:loc', namespace)
        if sitemap_locs and not urls:
            print(f"📑 Found sitemap index with {len(sitemap_locs)} sub-sitemaps")
            for sitemap_loc in sitemap_locs[:5]:  # Limit to first 5 sitemaps
                sub_urls = get_sitemap_urls(sitemap_loc.text, max_urls - len(urls))
                urls.extend(sub_urls)
                if len(urls) >= max_urls:
                    break

        print(f"✓ Found {len(urls)} URLs in sitemap")
        return urls[:max_urls]

    except ET.ParseError as e:
        print(f"❌ Failed to parse sitemap XML: {e}")
        return []
    except requests.RequestException as e:
        print(f"❌ Failed to fetch sitemap: {e}")
        return []


def load_website_from_sitemap(sitemap_url: str, max_pages: int = 50):
    """
    Load an entire website from its sitemap.

    Args:
        sitemap_url: URL to sitemap.xml
        max_pages: Maximum number of pages to load
    """
    print("="*80)
    print("WEBSITE SCRAPING - SITEMAP METHOD")
    print("="*80 + "\n")

    # Get URLs from sitemap
    urls = get_sitemap_urls(sitemap_url, max_pages)

    if not urls:
        print("❌ No URLs found in sitemap")
        return

    print(f"\n📊 Will load {len(urls)} pages\n")

    # Initialize RAG system
    rag = RAGSystem(persist_directory="outputs/chroma_db", collection_name="website_docs")

    # Track results
    successful = 0
    failed = []

    # Load each URL
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

    if failed:
        print("\nFailed URLs:")
        for item in failed[:5]:
            print(f"  - {item['url']}: {item['error'][:50]}")

    # Get stats
    stats = rag.get_stats()
    print(f"\n📊 Total documents in database: {stats['total_documents']}")

    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"outputs/website_scrape_{timestamp}.txt"
    os.makedirs('outputs', exist_ok=True)

    with open(report_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("WEBSITE SCRAPING REPORT - SITEMAP METHOD\n")
        f.write("="*80 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Sitemap: {sitemap_url}\n")
        f.write(f"Pages loaded: {successful}/{len(urls)}\n")
        f.write(f"Total chunks: {stats['total_documents']}\n\n")
        f.write("URLs Loaded:\n")
        for url in urls:
            f.write(f"  - {url}\n")
        if failed:
            f.write("\nFailed URLs:\n")
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
    # Example: Scrape a documentation site
    # Replace with your target sitemap

    print("💡 SITEMAP-BASED WEB SCRAPING")
    print("\nThis method is RECOMMENDED because:")
    print("  ✅ Fast - Parallel loading possible")
    print("  ✅ Complete - Gets all indexed pages")
    print("  ✅ Respectful - Uses site's official index")
    print("  ✅ No duplicate crawling")
    print()

    # Examples of sitemap URLs:
    examples = [
        "https://example.com/sitemap.xml",
        "https://example.com/sitemap_index.xml",
        "https://docs.example.com/sitemap.xml",
    ]

    print("Example sitemap URLs:")
    for ex in examples:
        print(f"  - {ex}")
    print()

    # Get sitemap URL from user or use example
    sitemap_url = input("Enter sitemap URL (or press Enter for demo): ").strip()

    if not sitemap_url:
        print("\n⚠️  No URL provided. Please provide a sitemap URL.")
        print("\nTo find a sitemap:")
        print("  1. Try: https://website.com/sitemap.xml")
        print("  2. Or: https://website.com/sitemap_index.xml")
        print("  3. Or check: https://website.com/robots.txt")
        sys.exit(0)

    # Get max pages
    max_pages_input = input("Max pages to load (default 50): ").strip()
    max_pages = int(max_pages_input) if max_pages_input else 50

    # Load website
    load_website_from_sitemap(sitemap_url, max_pages)

    print("\n" + "="*80)
    print("✅ DONE - Website loaded into ChromaDB")
    print("="*80)
    print("\nYou can now query this website using:")
    print("  ./start_gradio.sh")
    print("\nOr in Python:")
    print("  rag = RAGSystem(persist_directory='outputs/chroma_db', collection_name='website_docs')")
    print("  answer = rag.query('your question')")
