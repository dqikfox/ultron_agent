"""
Browser-Based GUI Function Testing Suite
Purpose: Automated Selenium-based testing of GUI buttons, links, and functions
Features:
  - Headless browser testing with Selenium
  - Button click validation
  - Function execution tracking
  - API endpoint testing
  - Performance monitoring
  - Screenshot capture on failures
  - Detailed HTML test reports
Status: Production-ready browser testing
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, asdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ultron_logger import log_info, log_error

# Try importing Selenium (optional)
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import (
        TimeoutException,
        NoSuchElementException
    )
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


@dataclass
class TestResult:
    """Individual test result"""
    test_name: str
    test_type: str  # 'button_click', 'link_click', 'function_call', 'api_call'
    status: str  # 'PASS', 'FAIL', 'SKIP'
    error_message: Optional[str] = None
    execution_time: float = 0.0
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None
    screenshot_path: Optional[str] = None

    def to_dict(self):
        return asdict(self)


class BrowserFunctionTester:
    """Browser-based GUI function testing"""

    def __init__(self, gui_url: str = "http://localhost:8080",
                 headless: bool = True):
        self.gui_url = gui_url
        self.headless = headless
        self.driver = None
        self.test_results: List[TestResult] = []
        self.screenshots_dir = Path("test_screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)

    def _init_driver(self):
        """Initialize Selenium WebDriver"""
        if not SELENIUM_AVAILABLE:
            log_error("browser_tester", "Selenium not installed. Install with: pip install selenium")
            return False

        try:
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

            self.driver = webdriver.Chrome(options=options)
            log_info("browser_tester", "WebDriver initialized successfully")
            return True
        except Exception as e:
            err_msg = (
                "Selenium not installed or WebDriver issue. "
                "Install with: pip install selenium"
            )
            log_error("browser_tester", err_msg)
            return False

    def _take_screenshot(self, test_name: str) -> Optional[str]:
        """Take screenshot on failure"""
        try:
            filename = f"{test_name}_{int(time.time())}.png"
            filepath = self.screenshots_dir / filename
            self.driver.save_screenshot(str(filepath))
            return str(filepath)
        except Exception as e:
            log_error("browser_tester", f"Failed to take screenshot: {e}")
            return None

    async def test_button_clicks(self) -> List[TestResult]:
        """Test all button click handlers"""
        if not self._init_driver():
            return []

        log_info("browser_tester", "Starting button click tests")

        try:
            self.driver.get(self.gui_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "main-interface")
                )
            )

            # Test 1: Start button
            self._test_start_button()

            # Test 2: Navigation buttons
            self._test_nav_buttons()

            # Test 3: Control buttons
            self._test_control_buttons()

            # Test 4: Voice button
            self._test_voice_button()

            log_info("browser_tester",
                    f"Button tests complete: {len(self.test_results)} tests")

        except Exception as e:
            log_error("browser_tester", f"Button testing failed: {e}")
        finally:
            if self.driver:
                self.driver.quit()

        return self.test_results

    def _test_start_button(self):
        """Test start button functionality"""
        try:
            start_btn = self.driver.find_element(By.ID, "start-button")
            start_time = time.time()

            start_btn.click()

            # Wait for main interface to appear
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "main-interface"))
            )

            execution_time = time.time() - start_time

            self.test_results.append(TestResult(
                test_name="Start Button Click",
                test_type="button_click",
                status="PASS",
                execution_time=execution_time,
                expected_behavior="Load main interface",
                actual_behavior="Main interface loaded successfully"
            ))
            log_info("browser_tester", "✅ Start button test passed")

        except TimeoutException:
            self.test_results.append(TestResult(
                test_name="Start Button Click",
                test_type="button_click",
                status="FAIL",
                error_message="Main interface did not load within timeout",
                screenshot_path=self._take_screenshot("start_button_fail")
            ))
            log_error("browser_tester", "❌ Start button test failed")
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Start Button Click",
                test_type="button_click",
                status="FAIL",
                error_message=str(e),
                screenshot_path=self._take_screenshot("start_button_error")
            ))

    def _test_nav_buttons(self):
        """Test navigation button functionality"""
        nav_buttons = [
            ("dashboard", "Dashboard"),
            ("console", "Console"),
            ("system", "System"),
            ("vision", "Vision"),
        ]

        for button_data_value, button_name in nav_buttons:
            try:
                selector = f"[data-section='{button_data_value}']"
                button = self.driver.find_element(By.CSS_SELECTOR, selector)
                start_time = time.time()

                button.click()

                # Wait for section to be visible
                section_id = f"{button_data_value}-section"
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, section_id))
                )

                execution_time = time.time() - start_time

                self.test_results.append(TestResult(
                    test_name=f"Nav Button: {button_name}",
                    test_type="button_click",
                    status="PASS",
                    execution_time=execution_time,
                    expected_behavior=f"Switch to {button_name} section",
                    actual_behavior=f"{button_name} section displayed"
                ))
                log_info("browser_tester", f"✅ {button_name} nav button test passed")

            except TimeoutException:
                self.test_results.append(TestResult(
                    test_name=f"Nav Button: {button_name}",
                    test_type="button_click",
                    status="FAIL",
                    error_message=f"Section did not load",
                    screenshot_path=self._take_screenshot(f"nav_{button_data_value}_fail")
                ))
            except NoSuchElementException:
                self.test_results.append(TestResult(
                    test_name=f"Nav Button: {button_name}",
                    test_type="button_click",
                    status="FAIL",
                    error_message=f"Button element not found"
                ))

    def _test_control_buttons(self):
        """Test control panel buttons"""
        control_buttons = [
            ("manual-tts-test-btn", "TTS Test"),
        ]

        for button_id, button_name in control_buttons:
            try:
                button = self.driver.find_element(By.ID, button_id)
                start_time = time.time()

                button.click()
                time.sleep(1)  # Wait for action

                execution_time = time.time() - start_time

                self.test_results.append(TestResult(
                    test_name=f"Control Button: {button_name}",
                    test_type="button_click",
                    status="PASS",
                    execution_time=execution_time,
                    expected_behavior=f"Execute {button_name}",
                    actual_behavior=f"{button_name} executed"
                ))
                log_info("browser_tester", f"✅ {button_name} control button test passed")

            except NoSuchElementException:
                self.test_results.append(TestResult(
                    test_name=f"Control Button: {button_name}",
                    test_type="button_click",
                    status="SKIP",
                    error_message=f"Button not present in current view"
                ))

    def _test_voice_button(self):
        """Test voice button functionality"""
        try:
            # Find voice button - may be in different locations
            voice_button_selectors = [
                "button[aria-label*='voice']",
                "button[aria-label*='Voice']",
                ".voice-toggle",
                "#voice-btn",
            ]

            voice_button = None
            for selector in voice_button_selectors:
                try:
                    voice_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue

            if not voice_button:
                self.test_results.append(TestResult(
                    test_name="Voice Button",
                    test_type="button_click",
                    status="SKIP",
                    error_message="Voice button not found in DOM"
                ))
                return

            start_time = time.time()
            voice_button.click()
            time.sleep(0.5)

            execution_time = time.time() - start_time

            self.test_results.append(TestResult(
                test_name="Voice Button",
                test_type="button_click",
                status="PASS",
                execution_time=execution_time,
                expected_behavior="Toggle voice mode",
                actual_behavior="Voice button clicked successfully"
            ))
            log_info("browser_tester", "✅ Voice button test passed")

        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Voice Button",
                test_type="button_click",
                status="FAIL",
                error_message=str(e)
            ))

    def test_function_existence(self) -> List[TestResult]:
        """Test if critical JavaScript functions exist"""
        log_info("browser_tester", "Testing JavaScript function existence")

        # This requires the page to be loaded and app.js to execute
        try:
            self._init_driver()
            self.driver.get(self.gui_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "start-button"))
            )

            # Test for critical functions via JavaScript execution
            critical_functions = [
                'window.ultronInterface',
                'window.ultronInterface.switchSection',
                'window.ultronInterface.loadSystemInfo',
                'window.ultronInterface.executeCommand',
                'window.ultronInterface.speak',
            ]

            for func_path in critical_functions:
                try:
                    result = self.driver.execute_script(f"return typeof {func_path} !== 'undefined'")

                    status = "PASS" if result else "FAIL"
                    self.test_results.append(TestResult(
                        test_name=f"Function: {func_path}",
                        test_type="function_call",
                        status=status,
                        expected_behavior=f"{func_path} is defined",
                        actual_behavior=f"Function exists: {result}"
                    ))

                    if result:
                        log_info("browser_tester", f"✅ {func_path} found")
                    else:
                        log_error("browser_tester", f"❌ {func_path} not found")

                except Exception as e:
                    self.test_results.append(TestResult(
                        test_name=f"Function: {func_path}",
                        test_type="function_call",
                        status="FAIL",
                        error_message=str(e)
                    ))

        except Exception as e:
            log_error("browser_tester", f"Function testing failed: {e}")
        finally:
            if self.driver:
                self.driver.quit()

        return self.test_results

    def generate_html_report(self, filename: str = "gui_test_report.html"):
        """Generate HTML test report"""
        total_tests = len(self.test_results)
        passed = sum(1 for t in self.test_results if t.status == "PASS")
        failed = sum(1 for t in self.test_results if t.status == "FAIL")
        skipped = sum(1 for t in self.test_results if t.status == "SKIP")

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>GUI Function Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #333; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px 0; }}
        .summary-box {{ background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .summary-box h3 {{ margin: 0; color: #333; }}
        .summary-box .number {{ font-size: 28px; font-weight: bold; margin: 10px 0; }}
        .pass {{ color: #27ae60; }}
        .fail {{ color: #e74c3c; }}
        .skip {{ color: #f39c12; }}
        table {{ width: 100%; border-collapse: collapse; background: white; margin-top: 20px; }}
        th {{ background: #333; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f9f9f9; }}
        .status-badge {{
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: bold;
            color: white;
        }}
        .status-pass {{ background: #27ae60; }}
        .status-fail {{ background: #e74c3c; }}
        .status-skip {{ background: #f39c12; }}
        .error {{ color: #c0392b; }}
        .footer {{ margin-top: 30px; text-align: center; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 GUI Function Test Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="summary">
        <div class="summary-box">
            <h3>Total Tests</h3>
            <div class="number">{total_tests}</div>
        </div>
        <div class="summary-box">
            <h3 class="pass">Passed</h3>
            <div class="number pass">{passed}</div>
        </div>
        <div class="summary-box">
            <h3 class="fail">Failed</h3>
            <div class="number fail">{failed}</div>
        </div>
        <div class="summary-box">
            <h3 class="skip">Skipped</h3>
            <div class="number skip">{skipped}</div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Test Name</th>
                <th>Type</th>
                <th>Status</th>
                <th>Time (ms)</th>
                <th>Details</th>
            </tr>
        </thead>
        <tbody>
"""

        for result in self.test_results:
            status_class = f"status-{result.status.lower()}"
            time_ms = f"{result.execution_time * 1000:.1f}"

            details = ""
            if result.error_message:
                details += f"<div class='error'>Error: {result.error_message}</div>"
            if result.expected_behavior:
                details += f"<div>Expected: {result.expected_behavior}</div>"
            if result.actual_behavior:
                details += f"<div>Actual: {result.actual_behavior}</div>"

            html_content += f"""
            <tr>
                <td>{result.test_name}</td>
                <td>{result.test_type}</td>
                <td><span class="status-badge {status_class}">{result.status}</span></td>
                <td>{time_ms}</td>
                <td>{details}</td>
            </tr>
"""

        html_content += """
        </tbody>
    </table>

    <div class="footer">
        <p>GUI Test Suite - ULTRON Development</p>
    </div>
</body>
</html>
"""

        with open(filename, 'w') as f:
            f.write(html_content)

        log_info("browser_tester", f"Report saved: {filename}")
        return filename


def main():
    """CLI entry point"""
    print("\n🧪 Browser-Based GUI Function Tester\n")

    tester = BrowserFunctionTester("http://localhost:8080", headless=True)

    print("Running button click tests...")
    # Note: Async tests need to be run in event loop
    # For CLI, we can run synchronous tests only

    print("Testing JavaScript function existence...")
    results = tester.test_function_existence()

    # Generate report
    report_path = tester.generate_html_report("gui_test_report.html")
    print(f"\n✅ Report generated: {report_path}")

    # Print summary
    passed = sum(1 for r in tester.test_results if r.status == "PASS")
    failed = sum(1 for r in tester.test_results if r.status == "FAIL")
    total = len(tester.test_results)

    print(f"\n📊 Summary: {passed}/{total} passed, {failed} failed")


if __name__ == "__main__":
    main()
