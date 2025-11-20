# Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

# Usage

## Local
Run the FastAPI server:
```bash
uvicorn main:app --reload
```

The tool will be available at `http://localhost:8000`

## Docker

```bash
docker build . -t nit-py-opal-tools:1.0.0
```

```bash
docker run -d --name nit-py-optal-tools-con -p 8000:50505 nit-py-opal-tools:1.0.0
```

# Development

## Creating a New Tool

1. Define your tool in `src/tools/`
2. Import it in `main.py` after initializing the ToolsService:

```python
app = FastAPI()
opal_tools_service = ToolsService(app)

# Import your tool here
from src.tools.url_slug_generator import generate_url_slug
```

# Opal Python List of Tools

## URL Slug Generator Tool

A simple Opal tool that converts article titles into clean, SEO-friendly URL slugs.

### Features

- Converts text to lowercase
- Removes Vietnamese diacritics using unidecode
- Removes common stop words (the, a, of, and, etc.)
- Replaces spaces and special characters with hyphens
- Removes all non-alphanumeric characters except hyphens
- Validates minimum slug length (5 characters)

### Example

**Input:**
```json
{
  "title": "Hướng dẫn học Python: The Complete Guide for Beginners"
}
```

**Output:**
```json
{
  "slug": "huong-dan-hoc-python-complete-guide-beginners",
  "original_title": "Hướng dẫn học Python: The Complete Guide for Beginners",
  "original_length": 57,
  "slug_length": 48
}
```

### API

The tool exposes a single endpoint that accepts a title and returns a URL slug along with metadata about the transformation.

**Request:**
```json
{
  "title": "Your Article Title Here"
}
```

**Success Response (200):**
```json
{
  "slug": "your-article-title-here",
  "original_title": "Your Article Title Here",
  "original_length": 23,
  "slug_length": 23
}
```

**Error Response (400):**
Returns a 400 Bad Request error if the resulting slug is less than 5 characters long:
```json
{
  "detail": "The resulting slug is critically short and requires a more detailed source title"
}
```

## Broken Link Checker Tool

Checks a list of URLs and identifies broken links.

### Features

- Validates and checks multiple URLs to identify broken or dead links.
- Use this tool when you need to verify if URLs are accessible, check website health,
- or identify broken links in a list of URLs. The tool performs asynchronous checks 

### Tool Parameters

The `broken_link_checker` tool accepts the following parameters:

- **urls** (required): List of URLs to check (array of strings, minimum 1 URL)
- **timeout** (optional): Request timeout in seconds (default: 10.0, range: 0-60)
- **follow_redirects** (optional): Whether to follow HTTP redirects (default: true)

### Example Request

```json
{
  "urls": [
    "https://example.com",
    "https://example.com/nonexistent",
    "https://invalid-domain-12345.com"
  ],
  "timeout": 10.0,
  "follow_redirects": true
}
```

### Example Response

```json
[
  {
    "url": "https://example.com",
    "status_code": 200,
    "is_dead": false,
    "error_message": null,
    "elapsed_time": 0.523,
    "reason": "OK",
    "checked_at": "2025-11-19T16:00:00.000000"
  },
  {
    "url": "https://example.com/nonexistent",
    "status_code": 404,
    "is_dead": true,
    "error_message": null,
    "elapsed_time": 0.312,
    "reason": "Not Found",
    "checked_at": "2025-11-19T16:00:01.000000"
  },
  {
    "url": "https://invalid-domain-12345.com",
    "status_code": null,
    "is_dead": true,
    "error_message": "Connection error: ...",
    "elapsed_time": 10.001,
    "reason": null,
    "checked_at": "2025-11-19T16:00:02.000000"
  }
]
```

### Response Fields

Each result in the response array contains:

- **url**: The checked URL
- **status_code**: HTTP status code (if available, null for connection errors)
- **is_dead**: Boolean indicating if the link is broken (true for 4xx/5xx, timeouts, or connection errors)
- **error_message**: Error description (null if request succeeded)
- **elapsed_time**: Response time in seconds
- **reason**: HTTP reason phrase (e.g., "OK", "Not Found") - null for connection errors
- **checked_at**: ISO timestamp of when the check was performed
## Tech Stack Discovery Tool

A powerful Opal tool that analyzes websites to identify the technologies, frameworks, libraries, and tools they use.

### Features

- Automatically detects web technologies from any public URL
- Identifies frameworks (React, Angular, Vue, etc.)
- Detects CMS platforms (WordPress, Drupal, etc.)
- Finds analytics tools (Google Analytics, etc.)
- Discovers programming languages and server technologies
- Returns technology versions when available
- Provides count of detected technologies

### Example

**Input:**
```json
{
  "url": "https://www.example.com"
}
```

**Output:**
```json
{
  "technologies": [
    {
      "name": "Nginx",
      "version": "1.14.0"
    },
    {
      "name": "WordPress",
      "version": "6.2"
    },
    {
      "name": "jQuery",
      "version": "3.6.0"
    },
    {
      "name": "PHP",
      "version": ""
    }
  ],
  "count": 4
}
```

### API

The tool exposes a single endpoint that accepts a URL and returns a list of detected technologies with their versions.

**Request:**
```json
{
  "url": "https://www.example.com"
}
```

**Success Response (200):**
```json
{
  "technologies": [
    {
      "name": "Technology Name",
      "version": "1.0.0"
    }
  ],
  "count": 1
}
```

**Error Response (400):**
Returns a 400 Bad Request error if the URL is missing:
```json
{
  "detail": "URL is required"
}
```

**Error Response (500):**
Returns a 500 Internal Server Error if the analysis fails:
```json
{
  "detail": "Internal Server Error"
}
```

### Opal chat message sample

```text
Check Tech Stack of Heineken website with URL https://heineken.com
```