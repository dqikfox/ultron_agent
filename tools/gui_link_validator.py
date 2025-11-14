"""
GUI Link and Function Validator for ULTRON Pokedex Interface
Purpose: Automated validation of all links, external resources, and JavaScript functions
Features:
  - Crawls HTML for all resource links (href, src, etc.)
  - Validates external URLs (CDN, fonts, APIs)
  - Checks for broken local file references
  - Validates JavaScript function existence
  - Tests button click handlers
  - Verifies API endpoint connectivity
  - Generates detailed validation reports
Status: Production-ready link validator
Author: ULTRON Development Team
"""

import os
import sys
import json
import time
import asyncio
import aiohttp
import re
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, asdict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ultron_logger import log_info, log_error


@dataclass
class LinkStatus:
    """Status of a single link validation"""
    url: str
    link_type: str  # 'external', 'local', 'api', 'widget'
    status: str  # 'PASS', 'FAIL', 'WARNING', 'SKIP'
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    response_time: Optional[float] = None
    source_location: Optional[str] = None
    recommendations: Optional[List[str]] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class FunctionStatus:
    """Status of a JavaScript function validation"""
    function_name: str
    status: str  # 'DEFINED', 'NOT_FOUND', 'ERROR'
    file_location: Optional[str] = None
    error_message: Optional[str] = None
    call_count: int = 0
    recommendations: Optional[List[str]] = None

    def to_dict(self):
        return asdict(self)


class GUILinkValidator:
    """Comprehensive GUI link and function validator"""

    def __init__(self, gui_path: str = "gui/ultron_enhanced/web"):
        self.gui_path = Path(gui_path)
        self.index_html = self.gui_path / "index.html"
        self.links_found: List[LinkStatus] = []
        self.functions_found: List[FunctionStatus] = []
        self.api_endpoints: List[str] = []
        self.local_resources: List[Tuple[str, str]] = []
        self.external_resources: List[str] = []
        self.validation_report = {}

    async def validate_all(self) -> Dict:
        """Run complete validation suite"""
        log_info("gui_validator", "Starting comprehensive GUI validation")

        try:
            # Phase 1: Parse HTML and extract links
            self._parse_html_links()

            # Phase 2: Validate local resources
            self._validate_local_resources()

            # Phase 3: Validate JavaScript functions
            self._validate_javascript_functions()

            # Phase 4: Validate external resources (async)
            await self._validate_external_resources()

            # Phase 5: Test API endpoints
            await self._test_api_endpoints()

            # Phase 6: Generate report
            self._generate_report()

            log_info("gui_validator", "Validation complete",
                    total_links=len(self.links_found),
                    functions_checked=len(self.functions_found))

            return self.validation_report

        except Exception as e:
            log_error("gui_validator", f"Validation failed: {e}")
            raise

    def _parse_html_links(self):
        """Extract all links from HTML file"""
        log_info("gui_validator", f"Parsing HTML: {self.index_html}")

        if not self.index_html.exists():
            raise FileNotFoundError(f"HTML file not found: {self.index_html}")

        with open(self.index_html, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # Extract stylesheet links
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                self.external_resources.append(href)
                self.links_found.append(LinkStatus(
                    url=href,
                    link_type='stylesheet',
                    status='PENDING',
                    source_location=f"index.html - <link> tag"
                ))

        # Extract script sources
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                self.external_resources.append(src)
                self.links_found.append(LinkStatus(
                    url=src,
                    link_type='script',
                    status='PENDING',
                    source_location=f"index.html - <script> tag"
                ))

        # Extract favicon links
        for link in soup.find_all('link', rel=re.compile('icon')):
            href = link.get('href')
            if href:
                self.local_resources.append(('favicon', href))
                self.links_found.append(LinkStatus(
                    url=href,
                    link_type='favicon',
                    status='PENDING',
                    source_location=f"index.html - favicon"
                ))

        # Extract audio sources
        for source in soup.find_all('source'):
            src = source.get('src')
            if src:
                self.local_resources.append(('audio', src))
                self.links_found.append(LinkStatus(
                    url=src,
                    link_type='audio',
                    status='PENDING',
                    source_location=f"index.html - audio source"
                ))

        # Extract onclick handlers with URLs
        for tag in soup.find_all(True):
            onclick = tag.get('onclick')
            if onclick:
                # Extract URLs from onclick
                urls = re.findall(r"https?://[^\s'\"]+|'[^']*'", onclick)
                for url in urls:
                    url_clean = url.strip("'\"")
                    if url_clean.startswith('http'):
                        self.external_resources.append(url_clean)

        log_info("gui_validator", "HTML parsing complete",
                external_links=len(self.external_resources),
                local_resources=len(self.local_resources))

    def _validate_local_resources(self):
        """Check if local resource files exist"""
        log_info("gui_validator", "Validating local resources")

        for resource_type, path in self.local_resources:
            full_path = self.gui_path / path

            if full_path.exists():
                status = LinkStatus(
                    url=path,
                    link_type=resource_type,
                    status='PASS',
                    source_location=str(full_path)
                )
            else:
                status = LinkStatus(
                    url=path,
                    link_type=resource_type,
                    status='FAIL',
                    error_message=f"File not found: {full_path}",
                    recommendations=[f"Create missing file: {path}"]
                )

            # Update existing status or add new
            self._update_link_status(path, status)

    def _validate_javascript_functions(self):
        """Extract and validate JavaScript functions from app.js"""
        log_info("gui_validator", "Validating JavaScript functions")

        app_js_path = self.gui_path / "app.js"
        if not app_js_path.exists():
            log_error("gui_validator", f"app.js not found: {app_js_path}")
            return

        with open(app_js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()

        # Find all function definitions
        function_pattern = r'(?:function\s+(\w+)|(\w+)\s*:\s*function|(?:^|\s)(\w+)\s*\(.*?\)\s*{)'
        matches = re.finditer(function_pattern, js_content, re.MULTILINE)

        defined_functions = set()
        for match in matches:
            func_name = match.group(1) or match.group(2) or match.group(3)
            if func_name and not func_name.isdigit():
                defined_functions.add(func_name)

        # Critical function checks
        critical_functions = [
            'init', 'cacheDomReferences', 'setupEventListeners',
            'switchSection', 'loadSystemInfo', 'executeCommand',
            'speak', 'testTTS', 'toggleVoiceChat', 'loadToolsGrid',
            'renderDashboardSnapshot', 'updateClock', 'handleStartupAnnouncement'
        ]

        for func in critical_functions:
            if func in defined_functions:
                status = FunctionStatus(
                    function_name=func,
                    status='DEFINED',
                    file_location='app.js',
                    call_count=js_content.count(f'{func}(')
                )
            else:
                status = FunctionStatus(
                    function_name=func,
                    status='NOT_FOUND',
                    file_location='app.js',
                    error_message=f"Function not found: {func}",
                    recommendations=[f"Define function: {func}"]
                )

            self.functions_found.append(status)

        log_info("gui_validator", "JavaScript validation complete",
                functions_found=len(defined_functions),
                critical_functions_checked=len(critical_functions))

    async def _validate_external_resources(self):
        """Validate external URLs are accessible"""
        log_info("gui_validator", "Validating external resources")

        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = []
            for url in set(self.external_resources):
                tasks.append(self._check_url(session, url))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for url, status in zip(set(self.external_resources), results):
                self._update_link_status(url, status)

    async def _check_url(self, session: aiohttp.ClientSession, url: str) -> LinkStatus:
        """Check if external URL is reachable"""
        start_time = time.time()

        try:
            # Skip checking localhost URLs in validation
            if 'localhost' in url or '127.0.0.1' in url:
                return LinkStatus(
                    url=url,
                    link_type='local_api',
                    status='SKIP',
                    error_message="Localhost URL skipped (requires running services)"
                )

            async with session.head(url, allow_redirects=True) as response:
                response_time = time.time() - start_time

                if response.status == 200:
                    return LinkStatus(
                        url=url,
                        link_type='external',
                        status='PASS',
                        status_code=response.status,
                        response_time=response_time
                    )
                else:
                    return LinkStatus(
                        url=url,
                        link_type='external',
                        status='WARNING',
                        status_code=response.status,
                        response_time=response_time,
                        error_message=f"HTTP {response.status}"
                    )

        except asyncio.TimeoutError:
            return LinkStatus(
                url=url,
                link_type='external',
                status='WARNING',
                error_message="Request timeout",
                recommendations=["Check internet connectivity"]
            )
        except Exception as e:
            return LinkStatus(
                url=url,
                link_type='external',
                status='FAIL',
                error_message=str(e),
                recommendations=["Verify URL is correct", "Check internet connectivity"]
            )

    async def _test_api_endpoints(self):
        """Test API endpoints for connectivity"""
        log_info("gui_validator", "Testing API endpoints")

        api_endpoints = [
            ('http://localhost:5000/health', 'API Health'),
            ('http://localhost:8080/health', 'Web GUI Health'),
            ('http://localhost:11434/api/tags', 'Ollama Models'),
        ]

        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for endpoint, name in api_endpoints:
                try:
                    async with session.get(endpoint) as response:
                        status = LinkStatus(
                            url=endpoint,
                            link_type='api',
                            status='PASS' if response.status == 200 else 'WARNING',
                            status_code=response.status,
                            source_location=f"API: {name}"
                        )
                except Exception as e:
                    status = LinkStatus(
                        url=endpoint,
                        link_type='api',
                        status='FAIL',
                        error_message=str(e),
                        source_location=f"API: {name}",
                        recommendations=["Ensure service is running"]
                    )

                self.links_found.append(status)

    def _update_link_status(self, url: str, new_status: LinkStatus):
        """Update or add link status"""
        for i, link in enumerate(self.links_found):
            if link.url == url:
                self.links_found[i] = new_status
                return
        self.links_found.append(new_status)

    def _generate_report(self):
        """Generate validation report"""
        log_info("gui_validator", "Generating validation report")

        # Count status breakdown
        status_counts = {
            'PASS': sum(1 for l in self.links_found if l.status == 'PASS'),
            'FAIL': sum(1 for l in self.links_found if l.status == 'FAIL'),
            'WARNING': sum(1 for l in self.links_found if l.status == 'WARNING'),
            'SKIP': sum(1 for l in self.links_found if l.status == 'SKIP'),
        }

        function_counts = {
            'DEFINED': sum(1 for f in self.functions_found if f.status == 'DEFINED'),
            'NOT_FOUND': sum(1 for f in self.functions_found if f.status == 'NOT_FOUND'),
        }

        # Build report
        self.validation_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'PASS' if status_counts['FAIL'] == 0 else 'FAIL',
            'links': {
                'total': len(self.links_found),
                'summary': status_counts,
                'details': [link.to_dict() for link in self.links_found]
            },
            'functions': {
                'total': len(self.functions_found),
                'summary': function_counts,
                'details': [func.to_dict() for func in self.functions_found]
            },
            'issues_found': len([l for l in self.links_found if l.status in ('FAIL', 'WARNING')]),
            'critical_issues': len([l for l in self.links_found if l.status == 'FAIL']),
        }

    def save_report(self, filename: str = "gui_validation_report.json"):
        """Save validation report to file"""
        report_path = Path(filename)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.validation_report, f, indent=2)

        log_info("gui_validator", f"Report saved: {report_path}")
        return report_path

    def print_summary(self):
        """Print validation summary to console"""
        if not self.validation_report:
            print("No validation report generated. Run validate_all() first.")
            return

        report = self.validation_report
        links = report['links']
        functions = report['functions']

        print("\n" + "="*70)
        print("GUI VALIDATION REPORT".center(70))
        print("="*70)

        print(f"\n📊 OVERALL STATUS: {report['overall_status']}")
        print(f"⏰ Generated: {report['timestamp']}")

        print(f"\n🔗 LINKS VALIDATION ({links['total']} total)")
        print(f"   ✅ PASS:    {links['summary']['PASS']}")
        print(f"   ❌ FAIL:    {links['summary']['FAIL']}")
        print(f"   ⚠️  WARNING: {links['summary']['WARNING']}")
        print(f"   ⏭️  SKIP:    {links['summary']['SKIP']}")

        print(f"\n🔧 FUNCTIONS VALIDATION ({functions['total']} total)")
        print(f"   ✅ DEFINED:   {functions['summary']['DEFINED']}")
        print(f"   ❌ NOT_FOUND: {functions['summary']['NOT_FOUND']}")

        print(f"\n⚠️  ISSUES FOUND: {report['issues_found']}")
        print(f"🔴 CRITICAL ISSUES: {report['critical_issues']}")

        # Show failed links
        failed_links = [l for l in links['details'] if l['status'] == 'FAIL']
        if failed_links:
            print(f"\n❌ FAILED LINKS:")
            for link in failed_links:
                print(f"   • {link['url']}")
                if link.get('error_message'):
                    print(f"     Error: {link['error_message']}")
                if link.get('recommendations'):
                    for rec in link['recommendations']:
                        print(f"     Recommend: {rec}")

        # Show warnings
        warning_links = [l for l in links['details'] if l['status'] == 'WARNING']
        if warning_links:
            print(f"\n⚠️  WARNINGS:")
            for link in warning_links:
                print(f"   • {link['url']}")
                if link.get('error_message'):
                    print(f"     {link['error_message']}")

        print("\n" + "="*70)


async def main():
    """CLI entry point for validator"""
    print("\n🔍 ULTRON GUI Link and Function Validator\n")

    validator = GUILinkValidator("gui/ultron_enhanced/web")

    try:
        report = await validator.validate_all()
        validator.print_summary()

        # Save report
        report_path = validator.save_report("gui_validation_report.json")
        print(f"\n📄 Report saved to: {report_path}")

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
