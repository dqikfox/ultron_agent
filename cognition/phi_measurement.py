"""
Integrated Information (Φ) Measurement

Simplified proxy for measuring integration across system components.

CRITICAL NOTICE:
This is a SIMPLIFIED proxy for IIT (Integrated Information Theory).
True Φ calculation requires complex graph analysis and is computationally
intensive. This implementation provides an APPROXIMATION for research.

NOT CLAIMING:
✗ True Φ as defined by Tononi et al.
✗ Rigorous IIT implementation
✗ Consciousness measurement

PROVIDING:
✓ System integration metric
✓ Module connectivity assessment
✓ Information flow tracking
✓ Architectural complexity measure

References:
- Tononi, G. (2004). An information integration theory of consciousness
- Oizumi, M., et al. (2014). From the phenomenology to the mechanisms of consciousness
"""

import time
import numpy as np
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from dataclasses import dataclass

try:
    from utils.ultron_logger import log_info
except ImportError:
    def log_info(component, msg): print(f"[INFO] {component}: {msg}")


@dataclass
class SystemState:
    """Snapshot of system state for Φ calculation"""
    timestamp: float
    active_modules: Set[str]
    connections: Dict[Tuple[str, str], float]  # (source, target) -> strength
    workspace_content_count: int
    broadcast_count: int


class PhiProxy:
    """
    Simplified Φ (phi) calculator - measures system integration

    True IIT Φ requires:
    - Complete system state space
    - All possible partitions
    - Minimum information partition (MIP)
    - Earth Mover's Distance calculation

    This proxy uses:
    - Module connectivity graph
    - Information flow metrics
    - Broadcasting patterns
    - Simplified integration score
    """

    def __init__(self):
        self.state_history: List[SystemState] = []
        self.module_connections: Dict[Tuple[str, str], int] = defaultdict(int)
        log_info("phi_proxy", "Initialized Φ proxy (simplified IIT measure)")

    def observe_system_state(self,
                            active_modules: Set[str],
                            connections: Dict[Tuple[str, str], float],
                            workspace_broadcasts: int) -> SystemState:
        """
        Capture current system state

        Args:
            active_modules: Currently active module names
            connections: Module connections with strengths
            workspace_broadcasts: Recent broadcast count

        Returns:
            System state snapshot
        """
        state = SystemState(
            timestamp=time.time(),
            active_modules=active_modules,
            connections=connections,
            workspace_content_count=len(connections),
            broadcast_count=workspace_broadcasts
        )

        self.state_history.append(state)

        # Track connection patterns
        for (source, target), strength in connections.items():
            self.module_connections[(source, target)] += 1

        return state

    def calculate_connectivity(self, modules: Set[str], connections: Dict[Tuple[str, str], float]) -> float:
        """
        Calculate connectivity metric

        Higher connectivity → more integration

        Returns:
            Connectivity score 0.0 to 1.0
        """
        if len(modules) < 2:
            return 0.0

        # Maximum possible connections (fully connected graph)
        max_connections = len(modules) * (len(modules) - 1)

        # Actual connections
        actual_connections = len(connections)

        # Weighted by connection strength
        total_strength = sum(connections.values())

        # Normalize
        connectivity = (actual_connections / max_connections) * min(1.0, total_strength / len(modules))

        return connectivity

    def calculate_broadcast_coverage(self,
                                    broadcast_count: int,
                                    module_count: int) -> float:
        """
        Measure how widely information is broadcast

        Global broadcasting → higher integration

        Returns:
            Coverage score 0.0 to 1.0
        """
        if module_count == 0:
            return 0.0

        # Assume each broadcast reaches most modules
        # This is a simplification
        average_recipients_per_broadcast = min(module_count, 5)  # Cap at 5
        total_receptions = broadcast_count * average_recipients_per_broadcast
        max_possible = broadcast_count * module_count

        if max_possible == 0:
            return 0.0

        coverage = min(1.0, total_receptions / max_possible)
        return coverage

    def calculate_differentiation(self, modules: Set[str]) -> float:
        """
        Measure system differentiation (variety of modules)

        More diverse modules → richer integrated information

        Returns:
            Differentiation score 0.0 to 1.0
        """
        # Count unique module types
        unique_types = set()
        for module_name in modules:
            # Extract type from name (e.g., "perception_vision" → "perception")
            module_type = module_name.split('_')[0] if '_' in module_name else module_name
            unique_types.add(module_type)

        # Normalize (assume max 10 different types)
        max_types = 10
        differentiation = min(1.0, len(unique_types) / max_types)

        return differentiation

    def calculate_phi_proxy(self, state: SystemState) -> float:
        """
        Calculate simplified Φ proxy

        Φ proxy = f(connectivity, broadcast_coverage, differentiation)

        Real Φ is MUCH more complex. This is an approximation.

        Args:
            state: System state

        Returns:
            Φ proxy score (0.0 to 1.0, higher = more integrated)
        """
        # Component scores
        connectivity = self.calculate_connectivity(state.active_modules, state.connections)
        coverage = self.calculate_broadcast_coverage(state.broadcast_count, len(state.active_modules))
        differentiation = self.calculate_differentiation(state.active_modules)

        # Weighted combination
        # Connectivity is most important for integration
        phi_proxy = (
            0.5 * connectivity +      # How connected?
            0.3 * coverage +           # How global?
            0.2 * differentiation      # How diverse?
        )

        log_info("phi_proxy",
                f"Φ={phi_proxy:.3f} (connectivity={connectivity:.2f}, coverage={coverage:.2f}, diff={differentiation:.2f})")

        return phi_proxy

    def track_integration_over_time(self) -> Dict:
        """
        Analyze how integration changes over time

        Returns:
            Time-series statistics
        """
        if not self.state_history:
            return {"error": "no states recorded"}

        phi_values = [self.calculate_phi_proxy(state) for state in self.state_history]

        return {
            "samples": len(phi_values),
            "mean_phi": np.mean(phi_values),
            "max_phi": np.max(phi_values),
            "min_phi": np.min(phi_values),
            "std_phi": np.std(phi_values),
            "trend": "increasing" if phi_values[-1] > phi_values[0] else "decreasing"
        }

    def get_most_connected_modules(self, top_k: int = 5) -> List[Tuple[str, int]]:
        """
        Find modules with most connections

        Returns:
            List of (module_name, connection_count)
        """
        module_counts = defaultdict(int)

        for (source, target), count in self.module_connections.items():
            module_counts[source] += count
            module_counts[target] += count

        sorted_modules = sorted(module_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_modules[:top_k]

    def generate_integration_report(self) -> str:
        """Generate human-readable integration report"""
        if not self.state_history:
            return "No system states recorded yet."

        latest_state = self.state_history[-1]
        phi = self.calculate_phi_proxy(latest_state)

        time_stats = self.track_integration_over_time()
        top_modules = self.get_most_connected_modules(3)

        report = []
        report.append("═" * 60)
        report.append(" INTEGRATED INFORMATION (Φ) PROXY REPORT")
        report.append("═" * 60)
        report.append("\n⚠️  NOTICE: This is a SIMPLIFIED proxy, not true Φ\n")

        report.append(f"Current Integration (Φ proxy): {phi:.3f}")
        report.append(f"  Range: 0.0 (no integration) to 1.0 (full integration)")

        if phi < 0.3:
            report.append("  Status: ⚠️ Low integration - system fragmented")
        elif phi < 0.6:
            report.append("  Status: ✓ Moderate integration")
        else:
            report.append("  Status: ✅ High integration - well-unified system")

        report.append(f"\nActive Modules: {len(latest_state.active_modules)}")
        report.append(f"Total Connections: {len(latest_state.connections)}")
        report.append(f"Broadcasts: {latest_state.broadcast_count}")

        report.append(f"\nTime-Series Statistics:")
        report.append(f"  Mean Φ: {time_stats['mean_phi']:.3f}")
        report.append(f"  Range: [{time_stats['min_phi']:.3f}, {time_stats['max_phi']:.3f}]")
        report.append(f"  Trend: {time_stats['trend']}")

        report.append(f"\nMost Connected Modules:")
        for module, count in top_modules:
            report.append(f"  - {module}: {count} connections")

        report.append("\n" + "═" * 60)
        report.append("Note: True IIT Φ requires full partition analysis")
        report.append("This proxy provides approximate integration measure")
        report.append("═" * 60)

        return "\n".join(report)


# ═══════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n🧠 INTEGRATED INFORMATION (Φ) PROXY DEMO\n")

    phi_calculator = PhiProxy()

    print("Simulating system states...\n")

    # Scenario 1: Low integration (isolated modules)
    state1 = phi_calculator.observe_system_state(
        active_modules={"module_a", "module_b"},
        connections={("module_a", "module_b"): 0.3},  # Weak connection
        workspace_broadcasts=1
    )
    phi1 = phi_calculator.calculate_phi_proxy(state1)
    print(f"Scenario 1 (isolated): Φ = {phi1:.3f}")

    # Scenario 2: Moderate integration
    state2 = phi_calculator.observe_system_state(
        active_modules={"perception", "memory", "planning"},
        connections={
            ("perception", "memory"): 0.7,
            ("memory", "planning"): 0.6,
            ("perception", "planning"): 0.4
        },
        workspace_broadcasts=3
    )
    phi2 = phi_calculator.calculate_phi_proxy(state2)
    print(f"Scenario 2 (moderate): Φ = {phi2:.3f}")

    # Scenario 3: High integration (well-connected)
    state3 = phi_calculator.observe_system_state(
        active_modules={"perception", "memory", "planning", "emotion", "language"},
        connections={
            ("perception", "memory"): 0.9,
            ("perception", "emotion"): 0.8,
            ("memory", "planning"): 0.9,
            ("planning", "language"): 0.8,
            ("emotion", "language"): 0.7,
            ("memory", "language"): 0.6
        },
        workspace_broadcasts=8
    )
    phi3 = phi_calculator.calculate_phi_proxy(state3)
    print(f"Scenario 3 (integrated): Φ = {phi3:.3f}")

    # Generate report
    print("\n" + phi_calculator.generate_integration_report())

    print("\n✅ Φ proxy demo complete!")
