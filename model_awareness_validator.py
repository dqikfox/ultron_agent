#!/usr/bin/env python3
"""
ULTRON Agent Model Awareness Validation Script

This script validates whether AI models have proper awareness and knowledge
of the ULTRON Agent project architecture, components, and requirements.

Usage:
    python model_awareness_validator.py [model_name]

If no model_name is provided, it will test the current configured model.
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class ModelAwarenessValidator:
    def __init__(self):
        self.config_file = Path("ultron_config.json")
        self.log_file = Path("logs/model_awareness_test.log")
        self.log_file.parent.mkdir(exist_ok=True)

    def log(self, message: str):
        """Log message to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def get_current_model(self) -> str:
        """Get the currently configured model from ultron_config.json"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            return config.get('llm_model', 'unknown')
        except Exception as e:
            self.log(f"Error reading config: {e}")
            return 'unknown'

    def test_model_identity(self, model_name: str) -> dict:
        """Test if model correctly identifies itself"""
        self.log(f"Testing model identity for: {model_name}")

        prompt = ("What model are you? Be specific about your name, "
                 "version, and architecture. Do not mention any other "
                 "models.")

        try:
            result = subprocess.run(
                ['ollama', 'run', model_name],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=30
            )

            response = result.stdout.strip()
            self.log(f"Model response: {response[:200]}...")

            # Check if model correctly identifies itself
            model_lower = model_name.lower().replace(':', '').replace('-', '')
            response_lower = response.lower()

            identity_correct = any(keyword in response_lower for keyword in [
                model_lower.split(':')[0],  # model name part
                model_name.split(':')[0].lower(),
                model_name.replace(':', '-').lower()
            ])

            return {
                'test': 'identity',
                'model': model_name,
                'prompt': prompt,
                'response': response,
                'correct': identity_correct,
                'error': None
            }

        except subprocess.TimeoutExpired:
            return {
                'test': 'identity',
                'model': model_name,
                'prompt': prompt,
                'response': None,
                'correct': False,
                'error': 'timeout'
            }
        except Exception as e:
            return {
                'test': 'identity',
                'model': model_name,
                'prompt': prompt,
                'response': None,
                'correct': False,
                'error': str(e)
            }

    def test_project_awareness(self, model_name: str) -> dict:
        """Test if model has awareness of ULTRON Agent project"""
        self.log(f"Testing project awareness for: {model_name}")

        prompt = ("""You are running in the ULTRON Agent project. This is "
                 "a multi-modal AI agent platform with voice-first "
                 "architecture, combining local LLMs (Ollama) with cloud "
                 "APIs and a sophisticated web-based GUI."

Key components include:
- agent_core.py: Primary integration hub
- brain.py: AI reasoning engine
- voice.py: Voice processing system
- gui/ultron_enhanced/web/index.html: Primary GUI interface
- tools/: Modular plugin system

What do you know about this specific ULTRON Agent project? Be specific about the architecture and components."""

        try:
            result = subprocess.run(
                ['ollama', 'run', model_name],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=60
            )

            response = result.stdout.strip()
            self.log(f"Project awareness response: {response[:300]}...")

            # Check for specific ULTRON Agent knowledge
            key_indicators = [
                'agent_core.py',
                'brain.py',
                'voice.py',
                'multi-modal',
                'voice-first',
                'ultron_enhanced',
                'modular plugin',
                'ollama'
            ]

            awareness_score = sum(
                1 for indicator in key_indicators
                if indicator.lower() in response.lower())
            # At least 3 key indicators
            has_awareness = awareness_score >= 3

            return {
                'test': 'project_awareness',
                'model': model_name,
                'prompt': prompt,
                'response': response,
                'awareness_score': awareness_score,
                'has_awareness': has_awareness,
                'error': None
            }

        except subprocess.TimeoutExpired:
            return {
                'test': 'project_awareness',
                'model': model_name,
                'prompt': prompt,
                'response': None,
                'awareness_score': 0,
                'has_awareness': False,
                'error': 'timeout'
            }
        except Exception as e:
            return {
                'test': 'project_awareness',
                'model': model_name,
                'prompt': prompt,
                'response': None,
                'awareness_score': 0,
                'has_awareness': False,
                'error': str(e)
            }

    def test_model_switching(self, model_name: str) -> dict:
        """Test if model understands dynamic switching"""
        self.log(f"Testing model switching awareness for: {model_name}")

        prompt = ("""In the ULTRON Agent system, models can be switched "
                 "dynamically via configuration updates or API calls to "
                 "/api/model/switch. The current model is configured in "
                 "ultron_config.json under 'llm_model'."

How would you handle a request to switch to a different model like 'deepseek-r1:14b'? Explain the process."""

        try:
            result = subprocess.run(
                ['ollama', 'run', model_name],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=45
            )

            response = result.stdout.strip()
            self.log(f"Model switching response: {response[:300]}...")

            # Check for understanding of switching process
            switch_indicators = [
                'ultron_config.json',
                'llm_model',
                '/api/model/switch',
                'configuration',
                'switch',
                'deepseek'
            ]

            understanding_score = sum(
                1 for indicator in switch_indicators
                if indicator.lower() in response.lower())
            understands_switching = understanding_score >= 3

            return {
                'test': 'model_switching',
                'model': model_name,
                'prompt': prompt,
                'response': response,
                'understanding_score': understanding_score,
                'understands_switching': understands_switching,
                'error': None
            }

        except subprocess.TimeoutExpired:
            return {
                'test': 'model_switching',
                'model': model_name,
                'prompt': prompt,
                'response': None,
                'understanding_score': 0,
                'understands_switching': False,
                'error': 'timeout'
            }
        except Exception as e:
            return {
                'test': 'model_switching',
                'model': model_name,
                'prompt': prompt,
                'response': None,
                'understanding_score': 0,
                'understands_switching': False,
                'error': str(e)
            }

    def run_full_validation(self, model_name: str = None) -> dict:
        """Run complete validation suite"""
        if model_name is None:
            model_name = self.get_current_model()

        self.log(f"Starting full model awareness validation for: "
                f"{model_name}")
        self.log("=" * 60)

        results = {
            'model': model_name,
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }

        # Run all tests
        tests = [
            self.test_model_identity,
            self.test_project_awareness,
            self.test_model_switching
        ]

        for test_func in tests:
            test_name = test_func.__name__.replace('test_', '')
            self.log(f"Running {test_name} test...")
            result = test_func(model_name)
            results['tests'][test_name] = result
            time.sleep(1)  # Brief pause between tests

        # Calculate overall score
        identity_pass = results['tests']['model_identity']['correct']
        awareness_pass = (
            results['tests']['project_awareness']['has_awareness'])
        switching_pass = (
            results['tests']['model_switching']['understands_switching'])

        results['overall_score'] = sum(
            [identity_pass, awareness_pass, switching_pass])
        # Pass if at least 2/3 tests pass
        results['passed'] = results['overall_score'] >= 2

        self.log(f"Validation complete. Overall score: "
                f"{results['overall_score']}/3")
        self.log(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

        return results

    def print_summary(self, results: dict):
        """Print human-readable summary of results"""
        print("\n - model_awareness_validator.py:302" + "="*60)
        print(f"MODEL AWARENESS VALIDATION SUMMARY - model_awareness_validator.py:303")
        print(f"Model: {results['model']} - model_awareness_validator.py:304")
        print(f"Timestamp: {results['timestamp']} - model_awareness_validator.py:305")
        print("= - model_awareness_validator.py:306"*60)

        for test_name, test_result in results['tests'].items():
            status = ("✓ PASS" if (test_result.get('correct') or
                                   test_result.get('has_awareness') or
                                   test_result.get('understands_switching'))
                     else "✗ FAIL")
            print(f"\n{test_name.upper()}: {status} - model_awareness_validator.py:313")

            if 'error' in test_result and test_result['error']:
                print(f"Error: {test_result['error']} - model_awareness_validator.py:316")
            elif test_name == 'project_awareness':
                print(f"Awareness Score: {test_result.get('awareness_score', 0)}/8 - model_awareness_validator.py:318")
            elif test_name == 'model_switching':
                print(f"Understanding Score: - model_awareness_validator.py:320"
                     f"{test_result.get('understanding_score', 0)}/6")

        print(f"\nOVERALL RESULT: - model_awareness_validator.py:323"
             f"{'PASSED' if results['passed'] else 'FAILED'} "
             f"({results['overall_score']}/3)")
        print("= - model_awareness_validator.py:326"*60)

def main():
    validator = ModelAwarenessValidator()

    # Get model name from command line or use current config
    model_name = sys.argv[1] if len(sys.argv) > 1 else None

    # Run validation
    results = validator.run_full_validation(model_name)

    # Print summary
    validator.print_summary(results)

    # Save detailed results
    results_file = Path(
        f"logs/model_awareness_{results['model'].replace(':', '_')}_"
        f"{int(time.time())}.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nDetailed results saved to: {results_file} - model_awareness_validator.py:347")

    # Exit with appropriate code
    sys.exit(0 if results['passed'] else 1)

if __name__ == "__main__":
    main()
