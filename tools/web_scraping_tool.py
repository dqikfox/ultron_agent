"""
Web Scraping Tool for ULTRON Agent

Provides web scraping capabilities for data collection and analysis
"""

import logging
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import json
import time
from typing import Dict, Any, Optional, List, Tuple, Union
from pathlib import Path
import re

# ULTRON Agent imports
from utils.ultron_logger import log_info, log_error, log_ai_decision
from utils.error_handlers import (
    NetworkError, TimeoutError, ValidationError, FileError,
    ErrorContext
)
from diagnostics import diagnostic_wrapper, track_metric


class WebScrapingTool:
    """
    Tool for web scraping and data extraction from websites
    """

    name: str = "Web Scraping Tool"
    description: str = "Extract data from websites, scrape content, and perform web analysis"

    def __init__(self) -> None:
        self.session: requests.Session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.cache_dir: Path = Path("cache/web_scraping")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def match(self, command: str) -> bool:
        """Check if command matches web scraping operations"""
        command_lower: str = command.lower()
        return any(keyword in command_lower for keyword in [
            "scrape website", "web scraping", "extract data", "crawl site",
            "web analysis", "scrape content", "website data", "html extraction"
        ])

    @diagnostic_wrapper("web_scraping", track_performance=True)
    def execute(self, command: str) -> str:
        """Execute web scraping operations"""
        try:
            command_lower: str = command.lower()
            track_metric("web_scraping", "commands_processed", 1, "count")

            if "scrape website" in command_lower or "scrape site" in command_lower:
                url: Optional[str] = self._extract_url(command)
                if url:
                    return self.scrape_website(url)
                else:
                    return "Please provide a valid URL to scrape"
            elif "extract data" in command_lower:
                url: Optional[str] = self._extract_url(command)
                if url:
                    return self.extract_structured_data(url)
                else:
                    return "Please provide a valid URL for data extraction"
            elif "web analysis" in command_lower:
                url: Optional[str] = self._extract_url(command)
                if url:
                    return self.analyze_website(url)
                else:
                    return "Please provide a valid URL for analysis"
            else:
                return self.get_help()

        except Exception as e:
            log_error("web_scraping", f"Web scraping failed: {e}")
            return f"Web scraping failed: {str(e)}"

    def scrape_website(self, url: str) -> str:
        """Scrape basic content from a website

        Args: url (str) - URL to scrape
        Returns: str - Website content or error message
        Raises: NetworkError on HTTP failures,
                TimeoutError on request timeout
        """
        with ErrorContext("web_scraping",
                         logger=logging.getLogger(
                             __name__)) as ctx:
            try:
                # Validate URL input
                if not url:
                    raise ValidationError(
                        "URL cannot be empty",
                        "url",
                        url,
                        "non-empty URL string"
                    )

                log_info("web_scraping",
                        f"Scraping: {url}")

                # Make HTTP request with timeout
                try:
                    response = self.session.get(url,
                                              timeout=30)
                    response.raise_for_status()
                except requests.Timeout as e:
                    log_error("web_scraping",
                             f"Scrape timeout: {e}")
                    raise TimeoutError(
                        f"Request timed out: {e}",
                        30,
                        "requests.get"
                    )
                except (requests.ConnectionError,
                       requests.HTTPError) as e:
                    log_error("web_scraping",
                             f"Network error: {e}")
                    raise NetworkError(
                        f"Scraping failed: {e}",
                        url,
                        "GET"
                    )

                soup: BeautifulSoup = BeautifulSoup(
                    response.content,
                    'html.parser'
                )

                # Extract basic information
                title: str = (
                    soup.title.string
                    if soup.title else "No title found"
                )
                meta_description: str = ""
                meta_desc_tag: Optional[Any] = \
                    soup.find('meta',
                             attrs={'name': 'description'})
                if meta_desc_tag:
                    meta_description = \
                        meta_desc_tag.get('content', '')

                # Extract main content
                tags: list = [
                    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
                ]
                content_tags: list = \
                    soup.find_all(tags)
                main_content: list = []
                for tag in content_tags[:20]:
                    text: str = tag.get_text().strip()
                    if text and len(text) > 20:
                        main_content.append(
                            f"{tag.name.upper()}: {text}"
                        )

                # Extract links
                links: list = []
                for link in soup.find_all(
                    'a', href=True)[:10]:
                    href: str = link['href']
                    text: str = \
                        link.get_text().strip()
                    if (href.startswith('http') or
                            href.startswith('//')):
                        links.append(
                            f"{text}: {href}"
                        )
                    elif href.startswith('/'):
                        parsed: Any = urlparse(url)
                        base_url: str = (
                            f"{parsed.scheme}://"
                            f"{parsed.netloc}"
                        )
                        full_url: str = urljoin(
                            base_url, href)
                        links.append(
                            f"{text}: {full_url}"
                        )

                result: str = f"""
🌐 **Website Scraping Results**

**URL:** {url}
**Title:** {title}
**Description:** {meta_description}

**Main Content (First 20 elements):**
{chr(10).join(f"• {c}" for c in main_content)}

**Links (First 10):**
{chr(10).join(f"• {l}" for l in links)}
"""

                log_info("web_scraping",
                        f"Scrape successful: {url}")
                return result

            except (NetworkError, TimeoutError,
                   ValidationError) as e:
                log_error("web_scraping",
                         f"Scrape error: {e}")
                ctx.error = e
                return f"Scraping error: {str(e)}"
            except Exception as e:
                log_error("web_scraping",
                         f"Unexpected scrape error: {e}")
                ctx.error = e
                return f"Scraping error: {str(e)}"

    def extract_structured_data(self,
                                url: str) -> str:
        """Extract structured data like JSON-LD

        Args: url (str) - URL to extract from
        Returns: str - Structured data or error message
        Raises: NetworkError, TimeoutError, ValidationError
        """
        with ErrorContext("web_scraping",
                         logger=logging.getLogger(
                             __name__)) as ctx:
            try:
                if not url:
                    raise ValidationError(
                        "URL cannot be empty",
                        "url",
                        url,
                        "non-empty URL string"
                    )

                log_info("web_scraping",
                        f"Extracting data: {url}")

                try:
                    response = self.session.get(url,
                                              timeout=30)
                    response.raise_for_status()
                except requests.Timeout as e:
                    log_error("web_scraping",
                             f"Extract timeout: {e}")
                    raise TimeoutError(
                        f"Request timed out: {e}",
                        30,
                        "requests.get"
                    )
                except (requests.ConnectionError,
                       requests.HTTPError) as e:
                    log_error("web_scraping",
                             f"Network error: {e}")
                    raise NetworkError(
                        f"Data extraction failed: {e}",
                        url,
                        "GET"
                    )

                soup: BeautifulSoup = BeautifulSoup(
                    response.content,
                    'html.parser'
                )
                structured_data: list = []

                # Extract JSON-LD
                json_ld_scripts: list = \
                    soup.find_all('script',
                                 type='application/ld+json'
                                 )
                for script in json_ld_scripts:
                    try:
                        data: dict = json.loads(
                            script.string)
                        structured_data.append({
                            'type': 'JSON-LD',
                            'data': data
                        })
                    except json.JSONDecodeError:
                        continue

                # Extract Open Graph data
                og_data: dict = {}
                og_metas: list = soup.find_all(
                    'meta',
                    property=lambda x: (
                        x and
                        x.startswith('og:')
                    )
                )
                for meta in og_metas:
                    prop_name: str = \
                        meta.get('property', ''). \
                        replace('og:', '')
                    content: str = \
                        meta.get('content', '')
                    og_data[prop_name] = content

                if og_data:
                    structured_data.append({
                        'type': 'Open Graph',
                        'data': og_data
                    })

                # Extract Twitter Card data
                twitter_data: dict = {}
                twitter_metas: list = \
                    soup.find_all('meta',
                                 attrs={
                                     'name': lambda x: (
                                         x and
                                         x.startswith(
                                             'twitter:'
                                         )
                                     )
                                 })
                for meta in twitter_metas:
                    name: str = \
                        meta.get('name', ''). \
                        replace('twitter:', '')
                    content: str = \
                        meta.get('content', '')
                    twitter_data[name] = content

                if twitter_data:
                    structured_data.append({
                        'type': 'Twitter Cards',
                        'data': twitter_data
                    })

                # Extract microdata
                microdata_items: list = \
                    soup.find_all(
                        attrs={'itemtype': True})
                for item in microdata_items[:5]:
                    item_data: dict = {
                        'type': item.get('itemtype'),
                        'properties': {}
                    }
                    for prop in \
                            item.find_all(
                                attrs={
                                    'itemprop': True
                                }):
                        prop_name: str = \
                            prop.get('itemprop')
                        prop_value: str = (
                            prop.get_text().strip()
                            if prop.get_text()
                            else prop.get(
                                'content', ''
                            )
                        )
                        item_data['properties'][
                            prop_name
                        ] = prop_value
                    structured_data.append({
                        'type': 'Microdata',
                        'data': item_data
                    })

                if not structured_data:
                    return (
                        f"No structured data "
                        f"found on {url}"
                    )

                result: str = f"""
📊 **Structured Data Extraction**

**URL:** {url}

**Found {len(structured_data)} elements:**
"""

                for i, data in enumerate(
                        structured_data, 1):
                    result += f"\n**{i}. " \
                              f"{data['type']}**\n"
                    if isinstance(
                        data['data'], dict):
                        for key, value in \
                                data['data']. \
                                items():
                            if isinstance(value,
                                        (dict,
                                         list)):
                                val_str = \
                                    json.dumps(
                                        value,
                                        indent=2
                                    )[:200]
                                result += (
                                    f"• {key}: "
                                    f"{val_str}...\n"
                                )
                            else:
                                result += (
                                    f"• {key}: "
                                    f"{value}\n"
                                )
                    else:
                        data_str: str = \
                            str(data['data'])[:300]
                        result += (
                            f"• Data: "
                            f"{data_str}...\n"
                        )

                log_info("web_scraping",
                        f"Extract successful: {url}")
                return result

            except (NetworkError, TimeoutError,
                   ValidationError) as e:
                log_error("web_scraping",
                         f"Extract error: {e}")
                ctx.error = e
                return f"Extraction error: {str(e)}"
            except Exception as e:
                log_error("web_scraping",
                         f"Unexpected extract error: {e}")
                ctx.error = e
                return f"Extraction error: {str(e)}"

    def analyze_website(self, url: str) -> str:
        """Perform website analysis with error handling

        Args: url (str) - URL to analyze
        Returns: str - Analysis report or error message
        Raises: NetworkError, TimeoutError, ValidationError
        """
        with ErrorContext("web_scraping",
                         logger=logging.getLogger(
                             __name__)) as ctx:
            try:
                if not url:
                    raise ValidationError(
                        "URL cannot be empty",
                        "url",
                        url,
                        "non-empty URL string"
                    )

                log_info("web_scraping",
                        f"Analyzing: {url}")

                start_time: float = time.time()
                try:
                    response = self.session.get(url,
                                              timeout=30)
                    load_time: float = \
                        time.time() - start_time
                    response.raise_for_status()
                except requests.Timeout as e:
                    log_error("web_scraping",
                             f"Analysis timeout: {e}")
                    raise TimeoutError(
                        f"Request timed out: {e}",
                        30,
                        "requests.get"
                    )
                except (requests.ConnectionError,
                       requests.HTTPError) as e:
                    log_error("web_scraping",
                             f"Network error: {e}")
                    raise NetworkError(
                        f"Analysis failed: {e}",
                        url,
                        "GET"
                    )

                soup: BeautifulSoup = BeautifulSoup(
                    response.content,
                    'html.parser'
                )

                # Basic analysis
                analysis: dict = {
                    'url': url,
                    'status_code': response.status_code,
                    'load_time': f"{load_time:.2f}s",
                    'content_type': response.headers.get(
                        'content-type', 'unknown'),
                    'content_length': len(
                        response.content),
                    'title': (
                        soup.title.string
                        if soup.title else None),
                    'meta_tags': len(
                        soup.find_all('meta')),
                    'links': len(
                        soup.find_all('a')),
                    'images': len(
                        soup.find_all('img')),
                    'scripts': len(
                        soup.find_all('script')),
                    'stylesheets': len(
                        soup.find_all(
                            'link', rel='stylesheet')),
                    'forms': len(
                        soup.find_all('form')),
                    'headings': {
                        'h1': len(
                            soup.find_all('h1')),
                        'h2': len(
                            soup.find_all('h2')),
                        'h3': len(
                            soup.find_all('h3'))
                    }
                }

                # SEO analysis
                seo_score: int = 0
                seo_feedback: list = []

                if (analysis['title'] and
                    30 <= len(
                        analysis['title']
                    ) <= 60):
                    seo_score += 20
                    seo_feedback.append(
                        "✅ Title length optimal"
                    )
                elif analysis['title']:
                    seo_score += 10
                    seo_feedback.append(
                        "⚠️ Title length needs work"
                    )

                meta_desc = soup.find(
                    'meta',
                    attrs={'name': 'description'}
                )
                if (meta_desc and
                    meta_desc.get('content')):
                    desc_len: int = len(
                        meta_desc['content']
                    )
                    if 120 <= desc_len <= 160:
                        seo_score += 20
                        seo_feedback.append(
                            "✅ Meta desc optimal"
                        )
                    else:
                        seo_score += 10
                        seo_feedback.append(
                            "⚠️ Meta desc needs work"
                        )

                if analysis['headings']['h1'] == 1:
                    seo_score += 15
                    seo_feedback.append(
                        "✅ Single H1 found"
                    )
                elif (
                    analysis['headings']['h1'] > 1
                ):
                    seo_score += 5
                    seo_feedback.append(
                        "⚠️ Multiple H1 tags"
                    )

                if analysis['images'] > 0:
                    images_with_alt: int = len([
                        img for img in
                        soup.find_all('img')
                        if img.get('alt')
                    ])
                    alt_ratio: float = (
                        images_with_alt /
                        analysis['images']
                    )
                    if alt_ratio >= 0.8:
                        seo_score += 15
                        seo_feedback.append(
                            "✅ Good alt text"
                        )
                    elif alt_ratio >= 0.5:
                        seo_score += 10
                        seo_feedback.append(
                            "⚠️ Some alt text"
                        )

                result: str = f"""
🔍 **Website Analysis Report**

**Basic Information:**
• URL: {analysis['url']}
• Status: {analysis['status_code']}
• Load Time: {analysis['load_time']}
• Content Type: {analysis['content_type']}
• Size: {analysis['content_length']:,} bytes

**Content Structure:**
• Title: {analysis['title'] or 'Not found'}
• Meta Tags: {analysis['meta_tags']}
• Links: {analysis['links']}
• Images: {analysis['images']}
• Scripts: {analysis['scripts']}
• Stylesheets: {analysis['stylesheets']}
• Forms: {analysis['forms']}
• H1: {analysis['headings']['h1']}
• H2: {analysis['headings']['h2']}
• H3: {analysis['headings']['h3']}

**SEO Analysis:**
• Score: {seo_score}/100
{chr(10).join(f"• {fb}" for fb in seo_feedback)}
"""

                log_info("web_scraping",
                        f"Analysis complete: {url}")
                return result

            except (NetworkError, TimeoutError,
                   ValidationError) as e:
                log_error("web_scraping",
                         f"Analysis error: {e}")
                ctx.error = e
                return f"Analysis error: {str(e)}"
            except Exception as e:
                log_error("web_scraping",
                         f"Unexpected analysis error: {e}")
                ctx.error = e
                return f"Analysis error: {str(e)}"

    def _extract_url(self, command: str) -> Optional[str]:
        """Extract URL from command"""
        import re
        url_pattern = r'https?://[^\s<>"{}|\\^`[\]]+'
        match = re.search(url_pattern, command)
        if match:
            return match.group(0)
        return None

    def get_help(self) -> str:
        """Get help information for the tool"""
        return """
🌐 **Web Scraping Tool**

**Capabilities:**
• Website content scraping and extraction
• Structured data extraction (JSON-LD, Open Graph, Twitter Cards)
• Website analysis and SEO evaluation
• Link discovery and content parsing

**Commands:**
• "scrape website https://example.com" - Basic website scraping
• "extract data https://example.com" - Extract structured data
• "web analysis https://example.com" - Comprehensive site analysis

**Features:**
• Respectful scraping with proper headers
• Content caching for performance
• SEO analysis and recommendations
• Multiple data format support

**Supported Data Types:**
• JSON-LD structured data
• Open Graph metadata
• Twitter Card data
• Microdata markup
• Basic HTML content analysis
"""

    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Web scraping command with URL"
                    }
                },
                "required": ["command"]
            }
        }
