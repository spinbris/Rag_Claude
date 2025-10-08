## Web Scraping Guide

This guide explains how to scrape entire websites and load them into ChromaDB.

## 📊 Methods Comparison

### Method 1: Sitemap-Based ⭐ (Recommended)

**File:** `web_scraping_sitemap.py`

**How it works:**
1. Fetch sitemap.xml from website
2. Extract all URL locations
3. Load each URL in parallel

**Pros:**
- ✅ **Fast** - Direct URLs, no crawling
- ✅ **Complete** - Gets all indexed pages
- ✅ **Efficient** - No duplicate pages
- ✅ **Respectful** - Uses site's official index
- ✅ **Reliable** - Structured XML format

**Cons:**
- ❌ Requires sitemap.xml to exist
- ❌ Only gets sitemap URLs (may miss some pages)

**When to use:**
- Documentation sites
- Blogs with sitemaps
- Any site with sitemap.xml
- When you want complete coverage

---

### Method 2: Recursive Crawling

**File:** `web_scraping_recursive.py`

**How it works:**
1. Start from a base URL
2. Extract all links from the page
3. Follow links up to max depth
4. Repeat for each new page

**Pros:**
- ✅ **Works without sitemap** - Any site
- ✅ **Discovers all links** - Follows navigation
- ✅ **Customizable** - Control depth/scope

**Cons:**
- ❌ **Slow** - Must crawl each page
- ❌ **Can miss pages** - Depends on link structure
- ❌ **May hit rate limits** - Many requests
- ❌ **Can load duplicates** - Same page via different paths
- ❌ **Needs limits** - Can crawl forever

**When to use:**
- No sitemap available
- Small sites only
- Need to discover unlisted pages
- Testing/development

---

## 🚀 Quick Start

### Sitemap Method (Recommended)

```bash
uv run python examples/web_scraping_sitemap.py
```

Then enter the sitemap URL:
```
https://example.com/sitemap.xml
```

### Recursive Method

```bash
uv run python examples/web_scraping_recursive.py
```

Then enter the base URL:
```
https://example.com
```

---

## 📝 Usage Examples

### Example 1: Documentation Site (Sitemap)

```python
from examples.web_scraping_sitemap import load_website_from_sitemap

# Load Python docs
load_website_from_sitemap(
    sitemap_url="https://docs.python.org/3/sitemap.xml",
    max_pages=100
)
```

### Example 2: Blog (Sitemap)

```python
load_website_from_sitemap(
    sitemap_url="https://blog.example.com/sitemap.xml",
    max_pages=50
)
```

### Example 3: Small Site (Recursive)

```python
from examples.web_scraping_recursive import load_website_recursive

load_website_recursive(
    base_url="https://example.com",
    max_depth=2,  # Only 2 levels deep
    max_pages=30  # Maximum 30 pages
)
```

---

## 🔍 Finding Sitemaps

### Method 1: Try Common URLs

```
https://example.com/sitemap.xml
https://example.com/sitemap_index.xml
https://example.com/sitemap/sitemap.xml
https://example.com/post-sitemap.xml
```

### Method 2: Check robots.txt

```
https://example.com/robots.txt
```

Look for lines like:
```
Sitemap: https://example.com/sitemap.xml
```

### Method 3: Google Search

```
site:example.com sitemap.xml
```

---

## ⚙️ Configuration

### Sitemap Parameters

```python
load_website_from_sitemap(
    sitemap_url="https://example.com/sitemap.xml",
    max_pages=100  # Limit number of pages
)
```

### Recursive Parameters

```python
load_website_recursive(
    base_url="https://example.com",
    max_depth=2,      # How many levels deep to crawl
    max_pages=50      # Maximum total pages
)
```

**Depth explanation:**
- `depth=0`: Only the base URL
- `depth=1`: Base URL + direct links
- `depth=2`: Base + links + their links
- `depth=3`: Three levels deep (not recommended)

---

## 🛡️ Best Practices

### 1. Be Respectful

- ✅ Use sitemap when available
- ✅ Add delays between requests (1-2 seconds)
- ✅ Check robots.txt
- ✅ Set reasonable limits
- ❌ Don't crawl too deep
- ❌ Don't make too many requests

### 2. Handle Errors

Both scripts handle:
- Network errors (timeout, connection)
- HTTP errors (404, 500, etc.)
- Parsing errors (invalid HTML)
- Rate limiting (429 errors)

Failed pages are logged but don't stop the process.

### 3. Monitor Progress

Both scripts show:
- Current page being loaded
- Progress counter
- Success/failure status
- Final statistics

### 4. Save Reports

Both scripts save reports to `outputs/`:
- List of URLs loaded
- Failed URLs with errors
- Statistics (pages, chunks, etc.)

---

## 📊 Output

### ChromaDB Collection

Both methods store data in:
```python
RAGSystem(
    persist_directory="outputs/chroma_db",
    collection_name="website_docs"
)
```

### Query the Data

```python
from ragsystem import RAGSystem

rag = RAGSystem(
    persist_directory="outputs/chroma_db",
    collection_name="website_docs"
)

answer = rag.query("What is this website about?")
print(answer)
```

Or use the Gradio interface:
```bash
./start_gradio.sh
```

---

## 🐛 Troubleshooting

### "No sitemap found"

**Solutions:**
1. Check if sitemap exists: Visit URL in browser
2. Try different sitemap URLs (see Finding Sitemaps)
3. Use recursive method instead

### "Rate limited" / "429 errors"

**Solutions:**
1. Increase delay between requests
2. Reduce max_pages
3. Try again later
4. Check site's robots.txt for crawl-delay

### "SSL certificate errors"

**Solutions:**
1. Update Python's certifi package: `uv add certifi`
2. Check your internet connection
3. Try HTTP instead of HTTPS (not recommended)

### "Memory errors" for large sites

**Solutions:**
1. Reduce max_pages
2. Process in batches
3. Use smaller chunk_size in RAGSystem

---

## 🔄 Comparison Table

| Feature | Sitemap | Recursive |
|---------|---------|-----------|
| **Speed** | Fast ⚡ | Slow 🐌 |
| **Completeness** | High ✅ | Variable ⚠️ |
| **Reliability** | High ✅ | Medium ⚠️ |
| **Setup** | Easy | Easy |
| **Dependencies** | Sitemap required | None |
| **Rate limiting risk** | Low | High |
| **Duplicate pages** | No | Yes |
| **Best for** | Any site with sitemap | Small sites, no sitemap |

---

## 💡 Tips

### For Documentation Sites

Use sitemap method with high max_pages:
```python
load_website_from_sitemap("https://docs.site.com/sitemap.xml", max_pages=500)
```

### For Blogs

Use sitemap method with category filters:
```python
# Only load blog posts (filter in your code)
urls = get_sitemap_urls("https://blog.site.com/sitemap.xml")
blog_urls = [u for u in urls if '/blog/' in u]
```

### For Small Company Sites

Use recursive method with low depth:
```python
load_website_recursive("https://company.com", max_depth=1, max_pages=20)
```

### For Large Sites

Use sitemap method in batches:
```python
# Load first 100 pages
load_website_from_sitemap("...", max_pages=100)

# Later, load next 100 (modify script to skip first 100)
```

---

## 📚 Related Examples

- [pdf_summary.py](pdf_summary.py) - Load single PDF
- [load_multiple_files.py](load_multiple_files.py) - Load multiple local files
- [manage_collections.py](manage_collections.py) - Manage different document sets

---

## 🆘 Support

If you encounter issues:

1. Check the error message
2. Review this guide
3. Try the alternative method
4. Reduce max_pages/max_depth
5. Check site's robots.txt
6. Report issues on GitHub

---

**Happy scraping! 🕷️**
