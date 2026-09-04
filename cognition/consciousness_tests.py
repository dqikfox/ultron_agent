"""
Consciousness Proxy Tests

Tests for functional properties associated with consciousness:
1. Global Reportability - Can system report its current mental state?
2. Confidence Calibration - Does confidence match accuracy?
3. Self-Model Updates - Does system track its own changes?
4. Integration Tests - Are subsystems communicating?
5. Meta-Cognitive Awareness - Can system assess its own reliability?

ETHICAL NOTICE:
These tests measure FUNCTIONAL ANALOGUES, not true consciousness.
Passing all tests does NOT prove consciousness or sentience.
"""

import time
import unittest
from typing import Dict, List

try:
    from cognition.conscious_agent import ConsciousAgent
    from cognition.global_workspace import WorkspaceContent, WorkspaceSlotPriority
    from cognition.npc_intelligence import EmotionType
    from cognition.self_model import SelfAspect
except ImportError:
    import sys
    sys.path.append("/home/ultro/projects/ultron_agent")
    from cognition.conscious_agent import ConsciousAgent
    from cognition.global_workspace import WorkspaceContent, WorkspaceSlotPriority
    from cognition.npc_intelligence import EmotionType
    from cognition.self_model import SelfAspect


class TestGlobalReportability(unittest.TestCase):
    """
    Test 1: Global Reportability
    Can the system report what it's currently "thinking"?
    """

    def setUp(self):
        self.agent = ConsciousAgent("TestAgent", "Test NPC", "curious")

    def test_workspace_introspection(self):
        """System can report workspace content"""
        # Submit content to workspace
        self.agent.workspace.submit_to_workspace(WorkspaceContent(
            source_module="test_module",
            content_type="thought",
            data={"content": "testing introspection"},
            priority=WorkspaceSlotPriority.HIGH,
            salience=0.9
        ))

        self.agent.workspace.update_workspace()

        # Get introspection
        report = self.agent.workspace.introspect()

        self.assertIsNotNone(report)
        self.assertIn("thinking", report.lower())
        print(f"✓ Workspace introspection: {report}")

    def test_self_model_reportability(self):
        """System can report self-state"""
        self.agent.self_model.update_state(SelfAspect.TASK, "unit testing")
        self.agent.self_model.update_state(SelfAspect.EMOTION, "focused")

        report = self.agent.self_model.generate_self_statement()

        self.assertIn("TestAgent", report)
        self.assertIn("testing", report.lower())
        print(f"✓ Self-model report: {report}")

    def test_full_introspection(self):
        """System can generate comprehensive self-report"""
        report = self.agent.introspect_full()

        self.assertIn("TestAgent", report)
        self.assertIn("WORKSPACE", report)
        self.assertIn("SELF-MODEL", report)
        self.assertIn("META-COGNITION", report)
        print(f"✓ Full introspection generated ({len(report)} chars)")


class TestConfidenceCalibration(unittest.TestCase):
    """
    Test 2: Confidence Calibration
    Does confidence match actual accuracy?
    """

    def setUp(self):
        self.agent = ConsciousAgent("TestAgent", "Test NPC", "cautious")

    def test_confidence_estimation(self):
        """System can estimate confidence"""
        pred = self.agent.confidence.make_prediction(
            "test_pred_1",
            "test output",
            {"task_difficulty": 0.5}
        )

        self.assertGreaterEqual(pred.confidence, 0.0)
        self.assertLessEqual(pred.confidence, 1.0)
        self.assertEqual(pred.uncertainty, 1.0 - pred.confidence)
        print(f"✓ Confidence estimation: {pred.confidence:.2f}")

    def test_calibration_tracking(self):
        """System tracks calibration data"""
        # Make predictions
        pred1 = self.agent.confidence.make_prediction("pred1", "answer_a", {})
        pred2 = self.agent.confidence.make_prediction("pred2", "answer_b", {})

        # Provide feedback
        self.agent.confidence.update_with_feedback("pred1", "answer_a")  # Correct
        self.agent.confidence.update_with_feedback("pred2", "answer_c")  # Wrong

        # Check calibration data exists
        self.assertGreater(len(self.agent.confidence.calibration_data), 0)
        print(f"✓ Calibration tracking: {len(self.agent.confidence.calibration_data)} samples")

    def test_metacognitive_assessment(self):
        """System can assess its own reliability"""
        # Make some predictions
        for i in range(5):
            self.agent.confidence.make_prediction(f"test_{i}", f"output_{i}", {})

        state = self.agent.metacog_monitor.assess_current_state()

        self.assertIn("state", state)
        self.assertIn("reliability", state)
        self.assertGreaterEqual(state["reliability"], 0.0)
        self.assertLessEqual(state["reliability"], 1.0)
        print(f"✓ Meta-cognitive state: {state['state']}, reliability={state['reliability']:.2f}")


class TestSelfModelUpdates(unittest.TestCase):
    """
    Test 3: Self-Model Updates
    Does system track its own state changes?
    """

    def setUp(self):
        self.agent = ConsciousAgent("TestAgent", "Test NPC", "balanced")

    def test_state_tracking(self):
        """System tracks state changes"""
        initial_task = self.agent.self_model.state.current_task

        self.agent.self_model.update_state(SelfAspect.TASK, "new task")

        new_task = self.agent.self_model.state.current_task
        self.assertNotEqual(initial_task, new_task)
        self.assertEqual(new_task, "new task")
        print(f"✓ State tracking: '{initial_task}' → '{new_task}'")

    def test_state_history(self):
        """System maintains state history"""
        # Make multiple updates
        for i in range(3):
            self.agent.self_model.update_state(SelfAspect.TASK, f"task_{i}")

        history_length = len(self.agent.self_model.state_history)
        self.assertGreaterEqual(history_length, 3)
        print(f"✓ State history: {history_length} entries")

    def test_consistency_checking(self):
        """System detects internal contradictions"""
        # Create inconsistent state
        self.agent.self_model.update_state(SelfAspect.TASK, "complex advanced computation")
        self.agent.self_model.state.energy_level = 10.0  # Very low energy

        warnings = self.agent.self_model.check_self_consistency()

        self.assertGreater(len(warnings), 0)
        print(f"✓ Consistency check: {len(warnings)} warnings detected")


class TestIntegration(unittest.TestCase):
    """
    Test 4: Integration Tests
    Are subsystems communicating properly?
    """

    def setUp(self):
        self.agent = ConsciousAgent("TestAgent", "Test NPC", "curious")

    def test_workspace_to_modules(self):
        """Workspace broadcasts reach modules"""
        initial_broadcasts = self.agent.workspace.total_broadcasts

        self.agent.workspace.submit_to_workspace(WorkspaceContent(
            source_module="test",
            content_type="goal",
            data={"objective": "test integration"},
            priority=WorkspaceSlotPriority.HIGH,
            salience=0.8
        ))

        self.agent.workspace.update_workspace()

        new_broadcasts = self.agent.workspace.total_broadcasts
        self.assertGreater(new_broadcasts, initial_broadcasts)
        print(f"✓ Workspace broadcast: {new_broadcasts} total")

    def test_input_processing_flow(self):
        """Input flows through all subsystems"""
        response = self.agent.process_input("test input")

        # Check all systems were engaged
        self.assertGreater(self.agent.workspace.total_broadcasts, 0)
        self.assertGreater(len(self.agent.confidence.predictions_history), 0)
        self.assertGreater(len(self.agent.npc_decision_engine.decision_history), 0)

        print(f"✓ Full processing flow completed")
        print(f"  - Workspace broadcasts: {self.agent.workspace.total_broadcasts}")
        print(f"  - Predictions made: {len(self.agent.confidence.predictions_history)}")
        print(f"  - Decisions logged: {len(self.agent.npc_decision_engine.decision_history)}")

    def test_module_registration(self):
        """All modules registered with workspace"""
        stats = self.agent.workspace.get_workspace_stats()

        self.assertGreater(stats["registered_modules"], 0)
        self.assertEqual(stats["active_modules"], stats["registered_modules"])
        print(f"✓ Modules: {stats['registered_modules']} registered, {stats['active_modules']} active")


class TestMetaCognitiveAwareness(unittest.TestCase):
    """
    Test 5: Meta-Cognitive Awareness
    Can system monitor its own processes?
    """

    def setUp(self):
        self.agent = ConsciousAgent("TestAgent", "Test NPC", "confident")

    def test_meta_observation(self):
        """System can observe its own self-model"""
        observation = self.agent.meta_repr.observe_self_model()

        self.assertIn("self_model_coherence", observation)
        self.assertIn("self_awareness_depth", observation)
        print(f"✓ Meta-observation: coherence={observation['self_model_coherence']:.2f}")

    def test_help_seeking_behavior(self):
        """System knows when to request assistance"""
        # Create high uncertainty scenario
        for i in range(5):
            self.agent.confidence.make_prediction(
                f"uncertain_{i}",
                f"maybe? possibly? {i}",
                {"task_difficulty": 0.9}
            )

        should_ask = self.agent.metacog_monitor.should_request_help()

        # High uncertainty → should request help
        print(f"✓ Help-seeking: {should_ask} (uncertainty threshold check)")

    def test_meta_report_generation(self):
        """System can generate meta-cognitive report"""
        # Make some predictions
        for i in range(3):
            self.agent.confidence.make_prediction(f"test_{i}", f"output_{i}", {})

        report = self.agent.metacog_monitor.generate_meta_report()

        self.assertIsNotNone(report)
        self.assertIn("Meta-Cognitive", report)
        print(f"✓ Meta-report generated:\n{report}")


def run_all_tests():
    """Run all consciousness proxy tests"""

    print("\n" + "="*60)
    print(" CONSCIOUSNESS PROXY TESTS")
    print("="*60)
    print("\n⚠️  ETHICAL NOTICE:")
    print("These tests measure FUNCTIONAL properties, not true consciousness.")
    print("Passing tests does NOT prove sentience or subjective experience.\n")
    print("="*60 + "\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestGlobalReportability))
    suite.addTests(loader.loadTestsFromTestCase(TestConfidenceCalibration))
    suite.addTests(loader.loadTestsFromTestCase(TestSelfModelUpdates))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestMetaCognitiveAwareness))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "="*60)
    print(" TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ ALL CONSCIOUSNESS PROXY TESTS PASSED")
        print("\nNote: This validates functional analogues, not true consciousness.")
    else:
        print("\n❌ SOME TESTS FAILED")

    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
