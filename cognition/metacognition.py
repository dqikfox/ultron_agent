"""
Meta-Cognitive Confidence Estimation

Implements "thinking about thinking" - the system's ability to evaluate
the reliability of its own predictions and outputs.

ETHICAL NOTICE:
This is a FUNCTIONAL confidence estimator for calibration and error
detection, NOT subjective introspection or "feelings of uncertainty".
It's a Bayesian probability calculator.

Components:
- Confidence head - estimates P(correct|output)
- Calibration tracker - monitors confidence vs. actual accuracy
- Uncertainty quantification - Bayesian or ensemble-based
- Meta-cognitive monitoring - tracks when system is unreliable

References:
- Gal, Y., & Ghahramani, Z. (2016). Dropout as a Bayesian Approximation
- Lakshminarayanan, B., et al. (2017). Simple and Scalable Predictive Uncertainty
- Fleming, S. M., & Dolan, R. J. (2012). The neural basis of metacognitive ability
"""

import numpy as np
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import deque
from enum import Enum

try:
    from utils.ultron_logger import log_info, log_error, log_ai_decision
except ImportError:
    def log_info(component, msg): print(f"[INFO] {component}: {msg}")
    def log_error(component, msg, error=None): print(f"[ERROR] {component}: {msg}")
    def log_ai_decision(component, msg, model="", confidence=0.0): print(f"[AI] {component}: {msg}")


class ConfidenceLevel(Enum):
    """Categorical confidence levels"""
    VERY_LOW = (0.0, 0.2, "guessing")
    LOW = (0.2, 0.4, "uncertain")
    MODERATE = (0.4, 0.6, "somewhat confident")
    HIGH = (0.6, 0.8, "confident")
    VERY_HIGH = (0.8, 1.0, "very confident")

    def __init__(self, min_val, max_val, description):
        self.min_val = min_val
        self.max_val = max_val
        self.description = description

    @classmethod
    def from_score(cls, score: float):
        """Get confidence level from numeric score"""
        for level in cls:
            if level.min_val <= score < level.max_val:
                return level
        return cls.VERY_HIGH  # 1.0 edge case


@dataclass
class Prediction:
    """A prediction with associated confidence"""
    prediction_id: str
    output: Any
    confidence: float  # 0.0 to 1.0
    uncertainty: float  # 0.0 to 1.0, inverse of confidence
    timestamp: float = field(default_factory=time.time)
    ground_truth: Optional[Any] = None  # Filled in later
    was_correct: Optional[bool] = None  # Evaluated later

    def evaluate(self, ground_truth: Any) -> bool:
        """
        Evaluate if prediction was correct

        Args:
            ground_truth: The actual correct answer

        Returns:
            True if prediction matched ground truth
        """
        self.ground_truth = ground_truth
        self.was_correct = (self.output == ground_truth)
        return self.was_correct


class ConfidenceEstimator:
    """
    Bayesian confidence head that estimates P(correct|output)

    Simplified implementation - real version would be trained neural network
    """

    def __init__(self, base_confidence: float = 0.5):
        self.base_confidence = base_confidence
        self.calibration_data: List[Tuple[float, bool]] = []  # (confidence, was_correct)
        self.predictions_history: deque = deque(maxlen=1000)

        log_info("confidence", "Initialized confidence estimator")

    def estimate_confidence(self,
                          output: Any,
                          context: Optional[Dict] = None) -> float:
        """
        Estimate confidence in a prediction

        In a real system, this would be a learned function mapping
        (output, context) -> confidence. Here we use heuristics.

        Args:
            output: The prediction/output
            context: Additional context (e.g., input complexity, model activations)

        Returns:
            Confidence score 0.0 to 1.0
        """
        context = context or {}
        confidence = self.base_confidence

        # Heuristic: Longer outputs might be more confident
        if isinstance(output, str):
            if len(output) > 50:
                confidence += 0.1
            if "?" in output:  # Contains question = less confident
                confidence -= 0.15
            if any(word in output.lower() for word in ["maybe", "possibly", "might"]):
                confidence -= 0.2
            if any(word in output.lower() for word in ["definitely", "certainly", "clearly"]):
                confidence += 0.15

        # Context-based adjustments
        if "task_difficulty" in context:
            difficulty = context["task_difficulty"]  # 0.0 to 1.0
            confidence -= (difficulty * 0.3)

        if "ensemble_agreement" in context:
            # If multiple models agree, higher confidence
            agreement = context["ensemble_agreement"]  # 0.0 to 1.0
            confidence += (agreement * 0.2)

        if "input_clarity" in context:
            clarity = context["input_clarity"]  # 0.0 to 1.0
            confidence += (clarity * 0.15)

        # Historical calibration adjustment
        if self.calibration_data:
            avg_accuracy = np.mean([1.0 if correct else 0.0 for _, correct in self.calibration_data])
            calibration_shift = avg_accuracy - 0.5  # Shift toward historical performance
            confidence += calibration_shift * 0.1

        # Clamp to valid range
        return max(0.0, min(1.0, confidence))

    def make_prediction(self,
                       prediction_id: str,
                       output: Any,
                       context: Optional[Dict] = None) -> Prediction:
        """
        Make a prediction with confidence estimate

        Args:
            prediction_id: Unique identifier
            output: The predicted output
            context: Additional context

        Returns:
            Prediction object with confidence
        """
        confidence = self.estimate_confidence(output, context)
        uncertainty = 1.0 - confidence

        pred = Prediction(
            prediction_id=prediction_id,
            output=output,
            confidence=confidence,
            uncertainty=uncertainty
        )

        self.predictions_history.append(pred)

        level = ConfidenceLevel.from_score(confidence)
        log_ai_decision(
            "confidence",
            f"Prediction {prediction_id}: {level.description}",
            confidence=confidence
        )

        return pred

    def update_with_feedback(self, prediction_id: str, ground_truth: Any):
        """
        Update calibration data with actual outcome

        Args:
            prediction_id: Which prediction to update
            ground_truth: The correct answer
        """
        # Find prediction
        for pred in self.predictions_history:
            if pred.prediction_id == prediction_id:
                was_correct = pred.evaluate(ground_truth)

                # Add to calibration data
                self.calibration_data.append((pred.confidence, was_correct))

                # Keep bounded
                if len(self.calibration_data) > 1000:
                    self.calibration_data = self.calibration_data[-1000:]

                log_info("confidence",
                        f"Feedback for {prediction_id}: {'✓ correct' if was_correct else '✗ wrong'} "
                        f"(confidence was {pred.confidence:.2f})")
                return

        log_error("confidence", f"Prediction {prediction_id} not found")

    def get_calibration_curve(self, num_bins: int = 10) -> Dict:
        """
        Compute calibration curve

        Returns:
            Dictionary with binned confidence vs. accuracy
        """
        if not self.calibration_data:
            return {"bins": [], "accuracy": [], "confidence": []}

        # Bin predictions by confidence
        bins = np.linspace(0, 1, num_bins + 1)
        bin_accuracy = []
        bin_confidence = []
        bin_counts = []

        for i in range(num_bins):
            bin_min, bin_max = bins[i], bins[i+1]
            bin_preds = [(conf, correct) for conf, correct in self.calibration_data
                        if bin_min <= conf < bin_max or (i == num_bins - 1 and conf == bin_max)]

            if bin_preds:
                avg_conf = np.mean([conf for conf, _ in bin_preds])
                avg_acc = np.mean([1.0 if correct else 0.0 for _, correct in bin_preds])
                bin_confidence.append(avg_conf)
                bin_accuracy.append(avg_acc)
                bin_counts.append(len(bin_preds))
            else:
                bin_confidence.append((bin_min + bin_max) / 2)
                bin_accuracy.append(0.0)
                bin_counts.append(0)

        return {
            "bins": [(bins[i], bins[i+1]) for i in range(num_bins)],
            "confidence": bin_confidence,
            "accuracy": bin_accuracy,
            "counts": bin_counts
        }

    def is_well_calibrated(self, tolerance: float = 0.1) -> bool:
        """
        Check if confidence estimates are well-calibrated

        Args:
            tolerance: Max allowed difference between confidence and accuracy

        Returns:
            True if calibrated within tolerance
        """
        curve = self.get_calibration_curve()

        if not curve["confidence"]:
            return False

        # Check if confidence matches accuracy
        mismatches = [abs(conf - acc) for conf, acc in zip(curve["confidence"], curve["accuracy"])]
        avg_mismatch = np.mean(mismatches)

        return avg_mismatch <= tolerance


class MetaCognitiveMonitor:
    """
    Meta-level monitoring of cognitive processes
    "Am I being reliable right now?"
    """

    def __init__(self, confidence_estimator: ConfidenceEstimator):
        self.confidence_estimator = confidence_estimator
        self.meta_observations: List[Dict] = []
        log_info("metacognition", "Initialized meta-cognitive monitoring")

    def assess_current_state(self) -> Dict:
        """
        Assess current meta-cognitive state

        Returns:
            Dictionary with meta-cognitive observations
        """
        recent_preds = list(self.confidence_estimator.predictions_history)[-10:]

        if not recent_preds:
            return {
                "state": "no_predictions",
                "reliability": 0.5,
                "notes": ["No recent predictions to assess"]
            }

        # Calculate recent confidence
        recent_confidence = np.mean([p.confidence for p in recent_preds])
        recent_uncertainty = np.mean([p.uncertainty for p in recent_preds])

        # Check calibration
        well_calibrated = self.confidence_estimator.is_well_calibrated()

        # Determine state
        if recent_uncertainty > 0.7:
            state = "high_uncertainty"
            notes = ["System is highly uncertain about recent predictions"]
        elif recent_confidence > 0.8:
            state = "high_confidence"
            notes = ["System is confident about recent predictions"]
        else:
            state = "moderate"
            notes = ["System confidence is moderate"]

        if not well_calibrated and len(self.confidence_estimator.calibration_data) > 50:
            notes.append("⚠️ Warning: Confidence estimates may be poorly calibrated")

        observation = {
            "timestamp": time.time(),
            "state": state,
            "recent_confidence": recent_confidence,
            "recent_uncertainty": recent_uncertainty,
            "calibration_quality": "good" if well_calibrated else "poor",
            "reliability": 1.0 - recent_uncertainty,
            "notes": notes
        }

        self.meta_observations.append(observation)

        return observation

    def should_request_help(self, uncertainty_threshold: float = 0.8) -> bool:
        """
        Determine if system should request human assistance

        Args:
            uncertainty_threshold: Above this, request help

        Returns:
            True if should ask for help
        """
        recent_preds = list(self.confidence_estimator.predictions_history)[-5:]

        if not recent_preds:
            return False

        avg_uncertainty = np.mean([p.uncertainty for p in recent_preds])

        return avg_uncertainty > uncertainty_threshold

    def generate_meta_report(self) -> str:
        """Generate natural language meta-cognitive report"""
        state = self.assess_current_state()

        # Handle case where no recent confidence
        recent_confidence = state.get("recent_confidence", 0.5)
        confidence_level = ConfidenceLevel.from_score(recent_confidence)

        report = f"Meta-Cognitive Self-Assessment:\n"
        report += f"  State: {state.get('state', 'unknown')}\n"
        report += f"  Confidence: {confidence_level.description} ({recent_confidence:.1%})\n"
        report += f"  Calibration: {state.get('calibration_quality', 'unknown')}\n"
        report += f"  Reliability: {state.get('reliability', 0.5):.1%}\n"

        if state["notes"]:
            report += f"  Notes: {'; '.join(state['notes'])}\n"

        if self.should_request_help():
            report += "  ⚠️ Recommendation: Consider requesting human assistance\n"

        return report


# ═══════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n🧠 META-COGNITIVE CONFIDENCE DEMO\n")

    # Create confidence estimator
    estimator = ConfidenceEstimator(base_confidence=0.6)

    print("✅ Confidence estimator initialized\n")

    # Make some predictions
    print("📊 Making predictions...\n")

    predictions = [
        ("pred1", "The capital of France is Paris",
         {"task_difficulty": 0.1, "input_clarity": 0.9}),
        ("pred2", "Quantum mechanics might involve wave-particle duality",
         {"task_difficulty": 0.7, "input_clarity": 0.6}),
        ("pred3", "Maybe the answer is 42?",
         {"task_difficulty": 0.9, "input_clarity": 0.3}),
        ("pred4", "I am certain that 2+2=4",
         {"task_difficulty": 0.0, "input_clarity": 1.0}),
    ]

    made_predictions = []
    for pid, output, context in predictions:
        pred = estimator.make_prediction(pid, output, context)
        made_predictions.append(pred)
        level = ConfidenceLevel.from_score(pred.confidence)
        print(f"   {pid}: {level.description} (confidence: {pred.confidence:.2f})")

    print("\n📝 Providing ground truth feedback...\n")

    # Simulate feedback
    estimator.update_with_feedback("pred1", "The capital of France is Paris")  # Correct
    estimator.update_with_feedback("pred2", "Wave-particle duality")  # Partially correct
    estimator.update_with_feedback("pred3", "42")  # Wrong context
    estimator.update_with_feedback("pred4", "4")  # Correct

    # Create meta-cognitive monitor
    print("🔍 Meta-Cognitive Assessment:\n")
    monitor = MetaCognitiveMonitor(estimator)

    report = monitor.generate_meta_report()
    print(report)

    # Check calibration
    print("\n📈 Calibration Analysis:\n")
    curve = estimator.get_calibration_curve(num_bins=5)

    for i, (conf, acc, count) in enumerate(zip(curve["confidence"],
                                                curve["accuracy"],
                                                curve["counts"])):
        if count > 0:
            match = "✓" if abs(conf - acc) < 0.15 else "✗"
            print(f"   Bin {i+1}: confidence={conf:.2f}, accuracy={acc:.2f}, n={count} {match}")

    is_calibrated = estimator.is_well_calibrated()
    print(f"\n   Overall calibration: {'✓ Good' if is_calibrated else '✗ Poor'}")

    print("\n✅ Meta-cognitive demo complete!")
    print("\nKey Properties Demonstrated:")
    print("  ✓ Confidence estimation (0.0 to 1.0)")
    print("  ✓ Uncertainty quantification")
    print("  ✓ Calibration tracking (confidence vs. accuracy)")
    print("  ✓ Meta-cognitive self-assessment")
    print("  ✓ Help-seeking behavior (high uncertainty → request assistance)")
