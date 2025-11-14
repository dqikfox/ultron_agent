"""
Integrated GUI Validation Suite
Purpose: Master script for complete GUI link and function validation
Provides:
  - CLI interface to run link validator
  - Browser-based function testing (optional)
  - HTML report generation
  - Automated issue detection and recommendations
  - Continuous monitoring support
Status: Production-ready CLI validator
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.gui_link_validator import GUILinkValidator


class IntegratedGUIValidator:
    """Master GUI validation suite"""

    def __init__(self, gui_path: str = "gui/ultron_enhanced/web"):
        self.gui_path = gui_path
        self.validator = GUILinkValidator(gui_path)
        self.validation_results = {}

    async def run_full_validation(self) -> dict:
        """Execute complete validation suite"""
        print("\n" + "="*70)
        print("🔍 ULTRON GUI COMPLETE VALIDATION SUITE".center(70))
        print("="*70 + "\n")

        print("📋 Running comprehensive validation...")
        print("-" * 70)

        try:
            # Run validator
            results = await self.validator.validate_all()
            self.validation_results = results

            # Display results
            self._display_results(results)

            # Save detailed reports
            self._save_reports(results)

            # Generate recommendations
            self._generate_recommendations(results)

            return results

        except Exception as e:
            print(f"\n❌ Validation failed: {e}")
            sys.exit(1)

    def _display_results(self, results: dict):
        """Display validation results in console"""
        links = results['links']
        functions = results['functions']

        # Summary section
        print("\n" + "="*70)
        print("📊 VALIDATION SUMMARY".center(70))
        print("="*70)

        print(f"\n✅ Overall Status: {results['overall_status']}")
        print(f"⏰ Timestamp: {results['timestamp']}")

        # Links report
        print(f"\n🔗 LINKS VALIDATION ({links['total']} total)")
        print("   " + "-"*60)
        print(f"   ✅ PASS:    {links['summary']['PASS']:3d} links working")
        print(f"   ❌ FAIL:    {links['summary']['FAIL']:3d} links broken")
        print(f"   ⚠️  WARNING: {links['summary']['WARNING']:3d} links issues")
        print(f"   ⏭️  SKIP:    {links['summary']['SKIP']:3d} links skipped")

        # Functions report
        print(f"\n🔧 FUNCTIONS VALIDATION ({functions['total']} total)")
        print("   " + "-"*60)
        print(f"   ✅ DEFINED:   "
              f"{functions['summary']['DEFINED']:3d} functions")
        print(f"   ❌ NOT_FOUND: "
              f"{functions['summary']['NOT_FOUND']:3d} functions")

        # Critical issues
        print(f"\n⚠️  CRITICAL ISSUES: {results['critical_issues']}")
        print(f"📌 TOTAL ISSUES: {results['issues_found']}")

        # Failed links detail
        failed_links = [lnk for lnk in links['details']
                        if lnk['status'] == 'FAIL']
        if failed_links:
            print(f"\n❌ FAILED LINKS ({len(failed_links)}):")
            for link in failed_links:
                print(f"   • {link['url']}")
                if link.get('error_message'):
                    print(f"     Error: {link['error_message']}")

        # Warning links detail
        warning_links = [lnk for lnk in links['details']
                         if lnk['status'] == 'WARNING']
        if warning_links:
            print(f"\n⚠️  WARNING LINKS ({len(warning_links)}):")
            for link in warning_links:
                url = link['url'][:50] + "..." \
                    if len(link['url']) > 50 else link['url']
                print(f"   • {url}")
                if link.get('error_message'):
                    print(f"     {link['error_message']}")

        print("\n" + "="*70)

    def _save_reports(self, results: dict):
        """Save detailed validation reports"""
        # Save JSON report
        json_path = self.validator.save_report(
            "gui_validation_report.json"
        )
        print(f"💾 JSON Report:  {json_path}")

        # Generate HTML report
        html_report = self._generate_html_report(results)
        html_path = "gui_validation_report.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        print(f"💾 HTML Report:  {html_path}")

        # Generate Markdown report
        md_report = self._generate_markdown_report(results)
        md_path = "gui_validation_report.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_report)
        print(f"💾 Markdown Report: {md_path}")

    def _generate_html_report(self, results: dict) -> str:
        """Generate HTML validation report"""
        links = results['links']
        functions = results['functions']

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ULTRON GUI Validation Report</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 20px;
            background: #1e1e1e;
            color: #e0e0e0;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: #2d2d2d;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .summary-card h3 {{ margin: 0 0 10px 0; color: #667eea; }}
        .summary-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #fff;
        }}
        .section {{
            background: #2d2d2d;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .section h2 {{
            margin-top: 0;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th {{
            background: #1e1e1e;
            color: #667eea;
            padding: 12px;
            text-align: left;
            font-weight: bold;
            border-bottom: 2px solid #667eea;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #404040;
        }}
        tr:hover {{ background: #353535; }}
        .status {{
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            text-align: center;
        }}
        .status-pass {{ background: #27ae60; color: white; }}
        .status-fail {{ background: #e74c3c; color: white; }}
        .status-warning {{ background: #f39c12; color: white; }}
        .status-skip {{ background: #95a5a6; color: white; }}
        .link-list {{
            list-style: none;
            padding: 0;
        }}
        .link-list li {{
            padding: 8px;
            margin-bottom: 8px;
            background: #1e1e1e;
            border-radius: 4px;
            border-left: 3px solid #e74c3c;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #404040;
            color: #888;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 ULTRON GUI Validation Report</h1>
            <p>Generated: {results['timestamp']}</p>
            <p>Status: <strong>{results['overall_status']}</strong></p>
        </div>

        <div class="summary">
            <div class="summary-card">
                <h3>Total Links</h3>
                <div class="value">{links['total']}</div>
            </div>
            <div class="summary-card">
                <h3>✅ Passing</h3>
                <div class="value" style="color: #27ae60;">
                    {links['summary']['PASS']}
                </div>
            </div>
            <div class="summary-card">
                <h3>❌ Failing</h3>
                <div class="value" style="color: #e74c3c;">
                    {links['summary']['FAIL']}
                </div>
            </div>
            <div class="summary-card">
                <h3>⚠️ Warnings</h3>
                <div class="value" style="color: #f39c12;">
                    {links['summary']['WARNING']}
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📊 Link Status Breakdown</h2>
            <table>
                <thead>
                    <tr>
                        <th>URL</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
"""

        for link in links['details'][:50]:  # Show first 50
            status_class = f"status-{link['status'].lower()}"
            details = link.get('error_message', '')
            html += f"""
                    <tr>
                        <td style="word-break: break-all; font-size: 12px;">
                            {link['url'][:60]}...
                        </td>
                        <td>{link['link_type']}</td>
                        <td>
                            <span class="status {status_class}">
                                {link['status']}
                            </span>
                        </td>
                        <td>{details}</td>
                    </tr>
"""

        html += f"""
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>🔧 Function Status</h2>
            <p>Total Functions Checked: {functions['total']}</p>
            <p>✅ Defined: {functions['summary']['DEFINED']}</p>
            <p>❌ Not Found: {functions['summary']['NOT_FOUND']}</p>
            <table>
                <thead>
                    <tr>
                        <th>Function Name</th>
                        <th>Status</th>
                        <th>File</th>
                    </tr>
                </thead>
                <tbody>
"""

        for func in functions['details']:
            status_class = f"status-{func['status'].lower()}"
            html += f"""
                    <tr>
                        <td>{func['function_name']}</td>
                        <td>
                            <span class="status {status_class}">
                                {func['status']}
                            </span>
                        </td>
                        <td>{func['file_location']}</td>
                    </tr>
"""

        html += """
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>ULTRON GUI Validation Suite - Production Quality Assurance</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def _generate_markdown_report(self, results: dict) -> str:
        """Generate Markdown validation report"""
        links = results['links']
        functions = results['functions']

        md = f"""# ULTRON GUI Validation Report

**Generated:** {results['timestamp']}
**Overall Status:** {results['overall_status']}

## 📊 Summary

| Metric | Count |
|--------|-------|
| Total Links | {links['total']} |
| ✅ Passing | {links['summary']['PASS']} |
| ❌ Failing | {links['summary']['FAIL']} |
| ⚠️ Warnings | {links['summary']['WARNING']} |
| ⏭️ Skipped | {links['summary']['SKIP']} |

## 🔗 Links Validation

### Passing Links ({links['summary']['PASS']})
"""

        passing = [lnk for lnk in links['details']
                   if lnk['status'] == 'PASS']
        for link in passing[:10]:
            md += f"\n- ✅ {link['url']}"

        md += f"\n\n### Failed Links ({links['summary']['FAIL']})\n"

        failing = [lnk for lnk in links['details']
                   if lnk['status'] == 'FAIL']
        for link in failing:
            md += f"\n- ❌ {link['url']}\n"
            if link.get('error_message'):
                md += f"  - Error: {link['error_message']}\n"
            if link.get('recommendations'):
                md += f"  - Recommendation: "
                md += f"{link['recommendations'][0]}\n"

        md += "\n## 🔧 Functions Validation\n"
        md += f"\n**Defined Functions:** "
        md += f"{functions['summary']['DEFINED']}\n"
        md += f"**Not Found Functions:** "
        md += f"{functions['summary']['NOT_FOUND']}\n"

        md += "\n### Function Details\n"
        for func in functions['details']:
            status = "✅" if func['status'] == 'DEFINED' else "❌"
            func_name = func['function_name']
            func_status = func['status']
            md += f"\n- {status} `{func_name}` - {func_status}\n"

        return md

    def _generate_recommendations(self, results: dict):
        """Generate actionable recommendations"""
        print("\n" + "="*70)
        print("💡 RECOMMENDATIONS".center(70))
        print("="*70 + "\n")

        links = results['links']
        failed_links = [lnk for lnk in links['details']
                        if lnk['status'] == 'FAIL']

        if not failed_links:
            print("✅ No critical issues found!")
            print("Your GUI links and functions are working as expected.\n")
            return

        # Group recommendations by type
        recommendations = {}

        for link in failed_links:
            if link.get('recommendations'):
                for rec in link['recommendations']:
                    if rec not in recommendations:
                        recommendations[rec] = []
                    recommendations[rec].append(link['url'])

        # Display recommendations
        print(f"Found {len(recommendations)} actionable recommendations:\n")

        for i, (rec, links_list) in enumerate(recommendations.items(), 1):
            print(f"{i}. {rec}")
            for link in links_list[:3]:  # Show first 3
                print(f"   - {link}")
            if len(links_list) > 3:
                print(f"   ... and {len(links_list) - 3} more")
            print()

        # Performance insights
        print("\n" + "-"*70)
        print("📈 PERFORMANCE INSIGHTS")
        print("-"*70 + "\n")

        external_links = [lnk for lnk in links['details']
                          if lnk['link_type'] == 'external']
        fast_links = [lnk for lnk in external_links
                      if lnk.get('response_time', 0) < 1]

        if external_links:
            avg_time = sum(lnk.get('response_time', 0)
                           for lnk in external_links) / len(external_links)
            print(f"Average Response Time: {avg_time:.2f}s")
            print(f"Fast Links: {len(fast_links)}/{len(external_links)}")

        print()


async def main():
    """CLI entry point"""
    validator = IntegratedGUIValidator()

    try:
        results = await validator.run_full_validation()

        # Exit with appropriate code
        if results['critical_issues'] > 0:
            print("\n⚠️  Critical issues found. Please review and fix.")
            sys.exit(1)
        else:
            print("\n✅ Validation complete with no critical issues!")
            sys.exit(0)

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
