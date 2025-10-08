# Web Scraping Implementation Summary

## Overview

Added comprehensive web scraping capabilities to load entire websites into ChromaDB using two methods:
1. **Sitemap-based** (recommended)
2. **Recursive crawling** (fallback)

## What Was Created

### 1. Sitemap-Based Scraper ⭐
**File:** `examples/web_scraping_sitemap.py`

**Features:**
- Fetches and parses sitemap.xml
- Extracts all URLs from sitemap
- Handles sitemap indexes (sitemap of sitemaps)
- Loads pages in parallel
- Generates detailed reports

**Advantages:**
- ✅ Fast (direct URLs)
- ✅ Complete (all indexed pages)
- ✅ Respectful (uses official index)
- ✅ No duplicates
- ✅ Reliable

### 2. Recursive Web Crawler
**File:** `examples/web_scraping_recursive.py`

**Features:**
- Starts from base URL
- Extracts and follows links
- Configurable depth limit
- Rate limiting (delay between requests)
- Skip patterns (login, cart, media files)
- Generates crawl reports

**Advantages:**
- ✅ Works without sitemap
- ✅ Discovers all linked pages
- ✅ Customizable scope

**Limitations:**
- ⚠️ Slower (must crawl each page)
- ⚠️ Can miss pages
- ⚠️ May hit rate limits
- ⚠️ Possible duplicates

### 3. Web Scraping Guide
**File:** `examples/WEB_SCRAPING_GUIDE.md`

**Contents:**
- Method comparison
- Quick start instructions
- Usage examples
- Finding sitemaps
- Configuration options
- Best practices
- Troubleshooting
- Tips for different site types

## Usage Examples

### Sitemap Method (Recommended)

```python
from examples.web_scraping_sitemap import load_website_from_sitemap

# Load documentation site
load_website_from_sitemap(
    sitemap_url="https://docs.python.org/3/sitemap.xml",
    max_pages=100
)
```

**Interactive:**
```bash
uv run python examples/web_scraping_sitemap.py
# Enter: https://example.com/sitemap.xml
# Enter max pages: 50
```

### Recursive Method

```python
from examples.web_scraping_recursive import load_website_recursive

# Load small website
load_website_recursive(
    base_url="https://example.com",
    max_depth=2,
    max_pages=30
)
```

**Interactive:**
```bash
uv run python examples/web_scraping_recursive.py
# Enter: https://example.com
# Enter max depth: 2
# Enter max pages: 50
```

## How to Find Sitemaps

### Method 1: Try Common URLs
```
https://example.com/sitemap.xml
https://example.com/sitemap_index.xml
https://example.com/sitemap/sitemap.xml
```

### Method 2: Check robots.txt
```
https://example.com/robots.txt
```
Look for: `Sitemap: https://example.com/sitemap.xml`

### Method 3: Google Search
```
site:example.com sitemap.xml
```

## Features

### Both Methods Include:

1. **Error Handling**
   - Network errors (timeout, connection)
   - HTTP errors (404, 500)
   - Parsing errors
   - Rate limiting

2. **Progress Tracking**
   - Current page counter
   - Success/failure status
   - Real-time updates

3. **Reporting**
   - List of loaded URLs
   - Failed URLs with errors
   - Statistics (pages, chunks)
   - Saved to `outputs/`

4. **ChromaDB Integration**
   - Stores in `website_docs` collection
   - Persistent storage
   - Ready for querying

### Sitemap-Specific:

- XML parsing
- Sitemap index support
- Fast parallel loading
- No duplicate URLs

### Recursive-Specific:

- Link extraction
- Depth limiting
- Domain restriction
- Skip patterns (login, media, etc.)
- Rate limiting (configurable delay)

## Method Comparison

| Feature | Sitemap | Recursive |
|---------|---------|-----------|
| **Speed** | Fast ⚡ | Slow 🐌 |
| **Completeness** | High ✅ | Variable ⚠️ |
| **Reliability** | High ✅ | Medium ⚠️ |
| **Rate limit risk** | Low | High |
| **Duplicates** | No | Possible |
| **Requirements** | Sitemap exists | None |
| **Best for** | Docs, blogs | Small sites |

## Query the Scraped Data

### Via Python:

```python
from ragsystem import RAGSystem

rag = RAGSystem(
    persist_directory="outputs/chroma_db",
    collection_name="website_docs"
)

answer = rag.query("What is this website about?")
print(answer)
```

### Via Gradio UI:

```bash
./start_gradio.sh
```

Then select the `website_docs` collection (if implemented) or query the default collection.

## Best Practices

### 1. Choose the Right Method

- **Use sitemap** if available (faster, better)
- **Use recursive** only if no sitemap exists

### 2. Be Respectful

- Set reasonable page limits
- Use delays (1-2 seconds)
- Check robots.txt
- Don't crawl too deep (max depth 2-3)

### 3. Handle Large Sites

For sites with 1000+ pages:
- Load in batches
- Use higher max_pages for sitemap
- Lower depth for recursive
- Monitor memory usage

### 4. Error Recovery

Both scripts:
- Continue on errors
- Log failed pages
- Save partial results
- Generate reports

## Output Structure

### ChromaDB Storage
```
outputs/chroma_db/
└── (website_docs collection)
```

### Reports
```
outputs/
├── website_scrape_YYYYMMDD_HHMMSS.txt  # Sitemap report
└── website_crawl_YYYYMMDD_HHMMSS.txt   # Recursive report
```

### Report Contents
- Timestamp
- Source URL/sitemap
- Pages loaded (success/total)
- Total chunks
- URL list
- Failed URLs with errors

## Use Cases

### Documentation Sites
```python
# Use sitemap with high limit
load_website_from_sitemap("https://docs.site.com/sitemap.xml", max_pages=500)
```

### Blogs
```python
# Use sitemap, filter by category
urls = get_sitemap_urls("https://blog.site.com/sitemap.xml")
blog_urls = [u for u in urls if '/blog/' in u]
# Then load filtered URLs
```

### Small Company Sites
```python
# Use recursive with low depth
load_website_recursive("https://company.com", max_depth=1, max_pages=20)
```

### Knowledge Bases
```python
# Use sitemap, organize by topic
# Load into different collections per category
```

## Files Created

1. **examples/web_scraping_sitemap.py** - Sitemap-based scraper
2. **examples/web_scraping_recursive.py** - Recursive crawler
3. **examples/WEB_SCRAPING_GUIDE.md** - Complete guide
4. **examples/README.md** - Updated with new examples
5. **WEB_SCRAPING_SUMMARY.md** - This file

## Integration with Existing System

### Works With:
- ✅ RAGSystem class
- ✅ ChromaDB storage
- ✅ OpenAI embeddings
- ✅ Gradio interface
- ✅ Existing loaders (PDF, DOCX, etc.)

### Collection Management:
```python
# Website in separate collection
rag_web = RAGSystem(collection_name="website_docs")

# Documents in default collection
rag_docs = RAGSystem(collection_name="rag_documents")

# Query both
answer1 = rag_web.query("website question")
answer2 = rag_docs.query("document question")
```

## Testing

### Test Sitemap Method:
```bash
uv run python examples/web_scraping_sitemap.py
# Enter a documentation site sitemap
# Verify loading and querying
```

### Test Recursive Method:
```bash
uv run python examples/web_scraping_recursive.py
# Enter a small website
# Set max_depth=1, max_pages=10
# Verify crawling works
```

## Next Steps

Potential enhancements:
- [ ] Parallel loading for recursive method
- [ ] Custom skip patterns
- [ ] Robots.txt parsing
- [ ] Resume from checkpoint
- [ ] URL filtering by pattern
- [ ] Automatic method selection
- [ ] Progress bar (tqdm)
- [ ] Export to other formats

---

**Both methods work well, but sitemap-based is strongly recommended when available!** 🕷️✨
