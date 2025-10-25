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
from typing import Dict, Any, Optional, List
from pathlib import Path
import re

# ULTRON Agent imports
from utils.ultron_logger import log_info, log_error, log_ai_decision
from diagnostics import diagnostic_wrapper, track_metric


class WebScrapingTool:
    """
    Tool for web scraping and data extraction from websites
    """

    name = "Web Scraping Tool"
    description = "Extract data from websites, scrape content, and perform web analysis"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.cache_dir = Path("cache/web_scraping")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def match(self, command: str) -> bool:
        """Check if command matches web scraping operations"""
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in [
            "scrape website", "web scraping", "extract data", "crawl site",
            "web analysis", "scrape content", "website data", "html extraction"
        ])

    @diagnostic_wrapper("web_scraping", track_performance=True)
    def execute(self, command: str) -> str:
        """Execute web scraping operations"""
        try:
            command_lower = command.lower()
            track_metric("web_scraping", "commands_processed", 1, "count")

            if "scrape website" in command_lower or "scrape site" in command_lower:
                url = self._extract_url(command)
                if url:
                    return self.scrape_website(url)
                else:
                    return "Please provide a valid URL to scrape"
            elif "extract data" in command_lower:
                url = self._extract_url(command)
                if url:
                    return self.extract_structured_data(url)
                else:
                    return "Please provide a valid URL for data extraction"
            elif "web analysis" in command_lower:
                url = self._extract_url(command)
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
        """Scrape basic content from a website"""
        try:
            log_info("web_scraping", f"Scraping website: {url}")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract basic information
            title = soup.title.string if soup.title else "No title found"
            meta_description = ""
            meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_desc_tag:
                meta_description = meta_desc_tag.get('content', '')

            # Extract main content (simple approach)
            content_tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            main_content = []
            for tag in content_tags[:20]:  # Limit to first 20 content elements
                text = tag.get_text().strip()
                if text and len(text) > 20:  # Filter out very short texts
                    main_content.append(f"{tag.name.upper()}: {text}")

            # Extract links
            links = []
            for link in soup.find_all('a', href=True)[:10]:  # First 10 links
                href = link['href']
                text = link.get_text().strip()
                if href.startswith('http') or href.startswith('//'):
                    links.append(f"{text}: {href}")
                elif href.startswith('/'):
                    base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                    full_url = urljoin(base_url, href)
                    links.append(f"{text}: {full_url}")

            result = f"""
🌐 **Website Scraping Results**

**URL:** {url}
**Title:** {title}
**Description:** {meta_description}

**Main Content (First 20 elements):**
{chr(10).join(f"• {content}" for content in main_content)}

**Links (First 10):**
{chr(10).join(f"• {link}" for link in links)}
"""

            return result

        except Exception as e:
            log_error("web_scraping", f"Website scraping failed: {e}")
            return f"Website scraping failed: {str(e)}"

    def extract_structured_data(self, url: str) -> str:
        """Extract structured data like JSON-LD, microdata, etc."""
        try:
            log_info("web_scraping", f"Extracting structured data from: {url}")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            structured_data = []

            # Extract JSON-LD
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    structured_data.append({
                        'type': 'JSON-LD',
                        'data': data
                    })
                except json.JSONDecodeError:
                    continue

            # Extract Open Graph data
            og_data = {}
            for meta in soup.find_all('meta', property=lambda x: x and x.startswith('og:')):
                property_name = meta.get('property', '').replace('og:', '')
                content = meta.get('content', '')
                og_data[property_name] = content

            if og_data:
                structured_data.append({
                    'type': 'Open Graph',
                    'data': og_data
                })

            # Extract Twitter Card data
            twitter_data = {}
            for meta in soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')}):
                name = meta.get('name', '').replace('twitter:', '')
                content = meta.get('content', '')
                twitter_data[name] = content

            if twitter_data:
                structured_data.append({
                    'type': 'Twitter Cards',
                    'data': twitter_data
                })

            # Extract microdata
            microdata_items = soup.find_all(attrs={'itemtype': True})
            for item in microdata_items[:5]:  # Limit to first 5
                item_data = {'type': item.get('itemtype'), 'properties': {}}
                for prop in item.find_all(attrs={'itemprop': True}):
                    prop_name = prop.get('itemprop')
                    prop_value = prop.get_text().strip() if prop.get_text() else prop.get('content', '')
                    item_data['properties'][prop_name] = prop_value
                structured_data.append({
                    'type': 'Microdata',
                    'data': item_data
                })

            if not structured_data:
                return f"No structured data found on {url}"

            result = f"""
📊 **Structured Data Extraction**

**URL:** {url}

**Found {len(structured_data)} structured data elements:**
"""

            for i, data in enumerate(structured_data, 1):
                result += f"\n**{i}. {data['type']}**\n"
                if isinstance(data['data'], dict):
                    for key, value in data['data'].items():
                        if isinstance(value, (dict, list)):
                            result += f"• {key}: {json.dumps(value, indent=2)[:200]}...\n"
                        else:
                            result += f"• {key}: {value}\n"
                else:
                    result += f"• Data: {str(data['data'])[:300]}...\n"

            return result

        except Exception as e:
            log_error("web_scraping", f"Structured data extraction failed: {e}")
            return f"Structured data extraction failed: {str(e)}"

    def analyze_website(self, url: str) -> str:
        """Perform basic website analysis"""
        try:
            log_info("web_scraping", f"Analyzing website: {url}")

            start_time = time.time()
            response = self.session.get(url, timeout=30)
            load_time = time.time() - start_time
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Basic analysis
            analysis = {
                'url': url,
                'status_code': response.status_code,
                'load_time': f"{load_time:.2f}s",
                'content_type': response.headers.get('content-type', 'unknown'),
                'content_length': len(response.content),
                'title': soup.title.string if soup.title else None,
                'meta_tags': len(soup.find_all('meta')),
                'links': len(soup.find_all('a')),
                'images': len(soup.find_all('img')),
                'scripts': len(soup.find_all('script')),
                'stylesheets': len(soup.find_all('link', rel='stylesheet')),
                'forms': len(soup.find_all('form')),
                'headings': {
                    'h1': len(soup.find_all('h1')),
                    'h2': len(soup.find_all('h2')),
                    'h3': len(soup.find_all('h3'))
                }
            }

            # SEO analysis
            seo_score = 0
            seo_feedback = []

            if analysis['title'] and 30 <= len(analysis['title']) <= 60:
                seo_score += 20
                seo_feedback.append("✅ Title length is optimal")
            elif analysis['title']:
                seo_score += 10
                seo_feedback.append("⚠️ Title length could be improved")

            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                desc_len = len(meta_desc['content'])
                if 120 <= desc_len <= 160:
                    seo_score += 20
                    seo_feedback.append("✅ Meta description length is optimal")
                else:
                    seo_score += 10
                    seo_feedback.append("⚠️ Meta description length could be improved")

            if analysis['headings']['h1'] == 1:
                seo_score += 15
                seo_feedback.append("✅ Single H1 tag found")
            elif analysis['headings']['h1'] > 1:
                seo_score += 5
                seo_feedback.append("⚠️ Multiple H1 tags found")

            if analysis['images'] > 0:
                images_with_alt = len([img for img in soup.find_all('img') if img.get('alt')])
                alt_ratio = images_with_alt / analysis['images']
                if alt_ratio >= 0.8:
                    seo_score += 15
                    seo_feedback.append("✅ Most images have alt text")
                elif alt_ratio >= 0.5:
                    seo_score += 10
                    seo_feedback.append("⚠️ Some images missing alt text")

            result = f"""
🔍 **Website Analysis Report**

**Basic Information:**
• URL: {analysis['url']}
• Status: {analysis['status_code']}
• Load Time: {analysis['load_time']}
• Content Type: {analysis['content_type']}
• Content Size: {analysis['content_length']:,} bytes

**Content Structure:**
• Title: {analysis['title'] or 'Not found'}
• Meta Tags: {analysis['meta_tags']}
• Links: {analysis['links']}
• Images: {analysis['images']}
• Scripts: {analysis['scripts']}
• Stylesheets: {analysis['stylesheets']}
• Forms: {analysis['forms']}
• Headings: H1({analysis['headings']['h1']}) H2({analysis['headings']['h2']}) H3({analysis['headings']['h3']})

**SEO Analysis:**
• SEO Score: {seo_score}/100
{chr(10).join(f"• {feedback}" for feedback in seo_feedback)}
"""

            return result

        except Exception as e:
            log_error("web_scraping", f"Website analysis failed: {e}")
            return f"Website analysis failed: {str(e)}"

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
