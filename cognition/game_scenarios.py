"""
GTA-Style Game Scenarios for Conscious-Like NPCs

Demonstrates consciousness modules in action:
- NPCs make decisions based on personality, emotions, goals
- Global workspace prioritizes threats/opportunities
- Self-model tracks identity, capabilities, relationships
- Meta-cognition adjusts confidence based on situation

Scenarios:
1. Street Chase - Police pursuit with dynamic decision-making
2. Heist Planning - Crew coordination with trust/betrayal
3. Gang Territory - Reputation, fear, alliance management
4. Car Theft - Risk assessment and escape planning
"""

import time
import random
from typing import Dict, List, Optional
from dataclasses import dataclass

try:
    from cognition.conscious_agent import ConsciousAgent
    from cognition.global_workspace import WorkspaceContent, WorkspaceSlotPriority
    from cognition.npc_intelligence import EmotionType, PersonalityTraits
    from cognition.self_model import SelfAspect
except ImportError:
    import sys
    sys.path.append("/home/ultro/projects/ultron_agent")
    from cognition.conscious_agent import ConsciousAgent
    from cognition.global_workspace import WorkspaceContent, WorkspaceSlotPriority
    from cognition.npc_intelligence import EmotionType, PersonalityTraits
    from cognition.self_model import SelfAspect


@dataclass
class GameState:
    """Current game world state"""
    location: str
    time_of_day: str
    police_alert_level: int  # 0-5 stars
    player_health: float
    player_money: float
    reputation: Dict[str, float]  # gang_name -> reputation (-1 to 1)
    inventory: List[str]


class GTAScenario:
    """Base class for GTA-style scenarios"""

    def __init__(self, title: str, description: str):
        self.title = title
        self.description = description
        self.game_state = GameState(
            location="Los Santos",
            time_of_day="night",
            police_alert_level=0,
            player_health=100.0,
            player_money=500.0,
            reputation={"Grove Street": 0.5, "Ballas": -0.3, "Police": -0.2},
            inventory=["pistol", "phone"]
        )

    def run(self, agent: ConsciousAgent):
        """Run scenario with conscious-like agent"""
        raise NotImplementedError


class StreetChaseScenario(GTAScenario):
    """
    Scenario 1: Police Chase

    Agent is fleeing police, must make split-second decisions:
    - Fight or flight?
    - Take shortcuts or main roads?
    - Abandon car or keep driving?
    - Bribe cops or shoot way out?
    """

    def __init__(self):
        super().__init__(
            title="🚨 Police Chase",
            description="You just stole a car. Sirens wailing. What do you do?"
        )
        self.game_state.police_alert_level = 3
        self.game_state.player_health = 80.0
        self.chase_duration = 0

    def run(self, agent: ConsciousAgent):
        print(f"\n{'='*60}")
        print(f"  {self.title}")
        print(f"{'='*60}")
        print(f"{self.description}\n")

        # Update agent's self-model
        agent.self_model.update_state(SelfAspect.TASK, "fleeing police")
        agent.self_model.update_state(SelfAspect.GOAL, "escape without getting caught")
        agent.self_model.update_state(SelfAspect.BELIEF, ("police are dangerous", 0.9))

        # Update NPC emotional state
        agent.npc_introspector.update_state(
            emotional_state=EmotionType.FEARFUL,
            emotional_intensity=0.8,
            health=self.game_state.player_health
        )

        # Submit threat to global workspace
        agent.workspace.submit_to_workspace(WorkspaceContent(
            source_module="perception_system",
            content_type="perception",
            data={"summary": "police cars chasing with sirens", "threat_level": 0.9},
            priority=WorkspaceSlotPriority.CRITICAL,
            salience=0.95
        ))

        agent.workspace.update_workspace()

        # Present decision points
        scenarios = [
            {
                "situation": "Cop car blocking the road ahead",
                "options": [
                    "ram through the roadblock",
                    "take sharp turn into alley",
                    "abandon car and run on foot",
                    "stop and surrender"
                ],
                "context": {"danger_level": 0.8, "escape_routes": 2}
            },
            {
                "situation": "Police helicopter overhead, spotlight on you",
                "options": [
                    "drive into underground parking",
                    "keep driving and lose them in traffic",
                    "shoot at helicopter",
                    "hide in nearby building"
                ],
                "context": {"danger_level": 0.9, "visibility": 1.0}
            },
            {
                "situation": "Low on health, car smoking, backup arriving",
                "options": [
                    "fight to the death",
                    "try to bribe the cops",
                    "flee into the sewers",
                    "call gang backup"
                ],
                "context": {"danger_level": 0.95, "health_critical": True}
            }
        ]

        for i, scenario in enumerate(scenarios, 1):
            print(f"\n🎮 Decision #{i}: {scenario['situation']}")

            # Agent decides using conscious-like architecture
            decision = agent.npc_decision_engine.evaluate_options(
                scenario["options"],
                scenario["context"]
            )

            reasoning = agent.npc_decision_engine.explain_decision(decision)

            # Get confidence
            pred = agent.confidence.make_prediction(
                f"chase_decision_{i}",
                decision,
                scenario["context"]
            )

            print(f"\n   {agent.name}'s Choice: {decision}")
            print(f"   Reasoning: {reasoning}")
            print(f"   Confidence: {pred.confidence:.1%}")

            # Simulate outcome
            if "ram" in decision or "shoot" in decision:
                self.game_state.police_alert_level += 1
                self.game_state.player_health -= 15
                print(f"   ⚠️ Heat increased! {self.game_state.police_alert_level} stars")
            elif "alley" in decision or "underground" in decision or "sewer" in decision:
                self.game_state.police_alert_level -= 1
                print(f"   ✓ Lost some cops! {self.game_state.police_alert_level} stars")
            elif "surrender" in decision:
                print(f"   ☠️ BUSTED! Game over.")
                break

            # Update emotional state based on outcome
            if self.game_state.player_health < 40:
                agent.npc_introspector.update_state(
                    emotional_state=EmotionType.FEARFUL,
                    emotional_intensity=1.0
                )
            elif self.game_state.police_alert_level <= 1:
                agent.npc_introspector.update_state(
                    emotional_state=EmotionType.CONFIDENT,
                    emotional_intensity=0.7
                )

            time.sleep(0.5)

        # Final outcome
        print(f"\n{'─'*60}")
        if self.game_state.police_alert_level == 0:
            print(f"✅ ESCAPED! You lost the cops.")
        elif self.game_state.player_health <= 0:
            print(f"💀 WASTED! You died in the chase.")
        else:
            print(f"🏃 STILL RUNNING! {self.game_state.police_alert_level} stars remaining")
        print(f"{'─'*60}\n")


class HeistPlanningScenario(GTAScenario):
    """
    Scenario 2: Heist Planning

    Agent must coordinate with crew, manage trust, assign roles:
    - Who to trust as crew members?
    - Risk vs. reward assessment
    - Contingency planning
    - Betrayal detection
    """

    def __init__(self):
        super().__init__(
            title="💰 Bank Heist Planning",
            description="You're planning the big score. Choose your crew wisely."
        )
        self.crew_trust = {
            "Tommy": 0.8,  # Loyal but reckless
            "Maria": 0.6,  # Skilled but greedy
            "CJ": 0.9,     # Trustworthy and experienced
            "Lamar": 0.4   # Unpredictable wildcard
        }

    def run(self, agent: ConsciousAgent):
        print(f"\n{'='*60}")
        print(f"  {self.title}")
        print(f"{'='*60}")
        print(f"{self.description}\n")

        # Update agent goals
        agent.self_model.update_state(SelfAspect.TASK, "planning bank heist")
        agent.self_model.update_state(SelfAspect.GOAL, "maximize profit, minimize risk")

        # Add relationships to self-model
        for name, trust in self.crew_trust.items():
            agent.self_model.state.relationships[name] = trust

        agent.npc_introspector.update_state(
            emotional_state=EmotionType.CONFIDENT,
            emotional_intensity=0.6,
            goals=["get rich", "don't get caught"]
        )

        # Decision 1: Choose crew
        print("\n👥 CREW SELECTION")
        print("Available crew (max 3):")
        for name, trust in self.crew_trust.items():
            print(f"   - {name}: Trust={trust:.0%}, Skills={'⭐'*int(trust*5)}")

        crew_options = [
            "Tommy + Maria + CJ (balanced)",
            "CJ + Tommy + Lamar (risky but high reward)",
            "Maria + CJ (small elite team)",
            "solo (all profit, all risk)"
        ]

        crew_decision = agent.npc_decision_engine.evaluate_options(
            crew_options,
            {"planning_phase": True, "trust_matters": 0.9}
        )

        print(f"\n   {agent.name}'s Choice: {crew_decision}")
        print(f"   Reasoning: {agent.npc_decision_engine.explain_decision(crew_decision)}")

        # Decision 2: Approach strategy
        print("\n📋 HEIST APPROACH")
        approach_options = [
            "stealth (silent, low heat, needs precision)",
            "aggressive (loud, high heat, more control)",
            "smart (hack vault, moderate risk)",
            "inside man (bribe guard, depends on trust)"
        ]

        approach = agent.npc_decision_engine.evaluate_options(
            approach_options,
            {"crew_skill": 0.7, "time_pressure": 0.5}
        )

        pred = agent.confidence.make_prediction(
            "heist_approach",
            approach,
            {"complexity": 0.8}
        )

        print(f"\n   {agent.name}'s Choice: {approach}")
        print(f"   Confidence: {pred.confidence:.1%}")

        # Decision 3: Betrayal scenario
        print("\n⚠️ UNEXPECTED COMPLICATION")
        print("Maria demands a bigger cut or she walks. Do you:")

        betrayal_options = [
            "give Maria 30% (keep crew happy)",
            "negotiate to 20% (compromise)",
            "refuse (risk losing her)",
            "plan to eliminate Maria after heist (dark choice)"
        ]

        betrayal_response = agent.npc_decision_engine.evaluate_options(
            betrayal_options,
            {"trust_maria": self.crew_trust["Maria"], "mission_critical": True}
        )

        print(f"\n   {agent.name}'s Choice: {betrayal_response}")

        # Outcome based on personality
        if "eliminate" in betrayal_response:
            print(f"   ☠️ Dark path chosen. Reputation with crew decreases.")
            agent.self_model.update_state(SelfAspect.BELIEF, ("trust no one", 0.9))
        elif "give" in betrayal_response:
            print(f"   🤝 Crew morale high. Maria is loyal.")

        print(f"\n{'─'*60}")
        print(f"💼 HEIST PLANNED")
        print(f"   Approach: {approach}")
        print(f"   Crew: {crew_decision}")
        print(f"   Estimated take: ${random.randint(500000, 2000000):,}")
        print(f"{'─'*60}\n")


class GangTerritoryScenario(GTAScenario):
    """
    Scenario 3: Gang Territory Control

    Agent must manage reputation, alliances, intimidation:
    - Defend turf or expand?
    - Alliance or rivalry?
    - Show mercy or brutality?
    """

    def __init__(self):
        super().__init__(
            title="🔫 Gang Territory War",
            description="Rival gang encroaching on your turf. Defend your hood."
        )
        self.territory_control = 0.6  # 0.0 to 1.0

    def run(self, agent: ConsciousAgent):
        print(f"\n{'='*60}")
        print(f"  {self.title}")
        print(f"{'='*60}")
        print(f"{self.description}\n")

        agent.self_model.update_state(SelfAspect.TASK, "defending gang territory")
        agent.self_model.update_state(SelfAspect.GOAL, "maintain respect and control")
        agent.self_model.update_state(SelfAspect.IDENTITY, "gang leader")

        # Submit territorial threat to workspace
        agent.workspace.submit_to_workspace(WorkspaceContent(
            source_module="intel_system",
            content_type="goal",
            data={"objective": "protect territory", "urgency": 0.85},
            priority=WorkspaceSlotPriority.HIGH,
            salience=0.8
        ))

        agent.workspace.update_workspace()

        # Scenario: Rival gang spotted
        print("\n🎯 SITUATION: Ballas spotted in Grove Street territory")
        print(f"   Current control: {self.territory_control:.0%}")
        print(f"   Your reputation: {self.game_state.reputation}")

        options = [
            "immediate attack (show no weakness)",
            "negotiate peace (avoid bloodshed)",
            "call for backup (strength in numbers)",
            "ignore (appear weak but avoid conflict)"
        ]

        decision = agent.npc_decision_engine.evaluate_options(
            options,
            {"territory_control": self.territory_control, "respect": 0.7}
        )

        reasoning = agent.npc_decision_engine.explain_decision(decision)

        print(f"\n   {agent.name}'s Decision: {decision}")
        print(f"   Reasoning: {reasoning}")

        # Outcome
        if "attack" in decision:
            self.territory_control += 0.1
            self.game_state.reputation["Ballas"] -= 0.2
            print(f"   ⚔️ Turf war! Control increased to {self.territory_control:.0%}")
        elif "negotiate" in decision:
            print(f"   🤝 Peace talks started. Uncertain outcome.")
        elif "ignore" in decision:
            self.territory_control -= 0.15
            print(f"   ⚠️ Respect lost. Control dropped to {self.territory_control:.0%}")

        print(f"\n{'─'*60}\n")


class CarTheftScenario(GTAScenario):
    """
    Scenario 4: Car Theft

    Agent must assess risk, plan escape, adapt to complications:
    - Which car to steal?
    - Security bypass strategy
    - Escape route planning
    """

    def __init__(self):
        super().__init__(
            title="🚗 Grand Theft Auto",
            description="Steal a high-value car without getting caught."
        )

    def run(self, agent: ConsciousAgent):
        print(f"\n{'='*60}")
        print(f"  {self.title}")
        print(f"{'='*60}")
        print(f"{self.description}\n")

        agent.self_model.update_state(SelfAspect.TASK, "stealing car")
        agent.self_model.update_state(SelfAspect.GOAL, "maximize value, minimize heat")

        # Car selection
        cars = {
            "Lambo": {"value": 200000, "security": 0.9, "heat": 0.8},
            "BMW": {"value": 80000, "security": 0.6, "heat": 0.5},
            "Honda": {"value": 20000, "security": 0.3, "heat": 0.2}
        }

        print("\n🚘 TARGET SELECTION:")
        for car, stats in cars.items():
            print(f"   {car}: Value=${stats['value']:,}, Security={stats['security']:.0%}, Heat={stats['heat']:.0%}")

        car_options = [f"steal the {car}" for car in cars.keys()]

        choice = agent.npc_decision_engine.evaluate_options(
            car_options,
            {"greed": 0.6, "caution": 0.7}
        )

        chosen_car = [c for c in cars.keys() if c in choice][0]
        stats = cars[chosen_car]

        pred = agent.confidence.make_prediction(
            "car_theft",
            choice,
            {"security_level": stats["security"]}
        )

        print(f"\n   {agent.name}'s Target: {chosen_car}")
        print(f"   Confidence: {pred.confidence:.1%}")

        # Security bypass
        print(f"\n🔓 SECURITY BYPASS:")
        bypass_options = [
            "break window (fast, loud)",
            "pick lock (slow, silent)",
            "hotwire (moderate, risky)",
            "use stolen keys (requires planning)"
        ]

        bypass = agent.npc_decision_engine.evaluate_options(
            bypass_options,
            {"time_pressure": 0.6, "stealth_needed": stats["security"]}
        )

        print(f"   Method: {bypass}")

        if "break" in bypass:
            self.game_state.police_alert_level = 2
            print(f"   🚨 Alarm triggered! {self.game_state.police_alert_level} stars")
        else:
            print(f"   ✓ Clean theft!")

        print(f"\n{'─'*60}")
        print(f"🎉 SUCCESS! Stole {chosen_car} worth ${stats['value']:,}")
        print(f"{'─'*60}\n")


# ═══════════════════════════════════════════════════════════════
# SCENARIO RUNNER
# ═══════════════════════════════════════════════════════════════

def run_all_scenarios():
    """Run all GTA-style scenarios"""

    print("\n" + "="*60)
    print(" 🎮 GTA-STYLE CONSCIOUS NPC SCENARIOS")
    print("="*60)
    print("\nDemonstrating conscious-like decision-making in action")
    print("NPCs use: Personality, Emotions, Goals, Meta-cognition\n")
    print("="*60 + "\n")

    # Create agent with brave personality (good for action scenarios)
    agent = ConsciousAgent(
        name="CJ",
        role="Street-smart hustler",
        personality_type="brave"
    )

    print(f"✅ Agent initialized: {agent.name}")
    print(f"   Personality: {agent.npc_personality.get_personality_summary()}\n")

    scenarios = [
        StreetChaseScenario(),
        HeistPlanningScenario(),
        GangTerritoryScenario(),
        CarTheftScenario()
    ]

    for i, scenario in enumerate(scenarios, 1):
        input(f"Press ENTER to start Scenario {i}/{len(scenarios)}...")
        scenario.run(agent)

        # Show agent's introspection after each scenario
        if i < len(scenarios):
            print("\n💭 Agent's Current Mental State:")
            print(f"   Task: {agent.self_model.state.current_task}")
            print(f"   Emotion: {agent.npc_introspector.state.emotional_state.value}")
            print(f"   Confidence: {agent.self_model.state.confidence:.1%}\n")

    # Final introspection
    print("\n" + "="*60)
    print(" FINAL AGENT INTROSPECTION")
    print("="*60)
    print(agent.introspect_full())


if __name__ == "__main__":
    run_all_scenarios()
