"""
Permadeath and risk/reward system for Charcoal 2.0
Creates high stakes gameplay focused on meaningful choices
"""

import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
from character import Character
from items import Item


class RiskLevel(Enum):
    MINIMAL = "minimal"      # 1-10% death chance
    LOW = "low"             # 11-25% death chance  
    MODERATE = "moderate"   # 26-40% death chance
    HIGH = "high"           # 41-60% death chance
    EXTREME = "extreme"     # 61-80% death chance
    CERTAIN = "certain"     # 81-95% death chance


class DeathType(Enum):
    COMBAT = "combat"
    TRAP = "trap"
    ENVIRONMENTAL = "environmental"
    MAGICAL = "magical"
    SACRIFICE = "sacrifice"
    CURSE = "curse"


@dataclass
class DeathScenario:
    """Represents a potential death situation"""
    name: str
    description: str
    death_type: DeathType
    base_risk: float  # 0.0 to 1.0
    warning_signs: List[str]
    possible_rewards: List[str]
    mitigation_strategies: List[str]
    
    def calculate_final_risk(self, character: Character, party_modifiers: Dict = None) -> float:
        """Calculate final death risk including character and party factors"""
        risk = self.base_risk
        
        # Character trait modifiers
        for trait_name in character.traits:
            if "death_defiant" in trait_name.lower():
                risk *= 0.6  # 40% risk reduction
            elif "battle_hardened" in trait_name.lower():
                risk *= 0.8  # 20% risk reduction
            elif "lucky" in trait_name.lower():
                risk *= 0.9  # 10% risk reduction
        
        # Constitution modifier
        constitution_bonus = (character.stats.constitution - 10) * 0.02
        risk = max(0.01, risk - constitution_bonus)
        
        # Party modifiers
        if party_modifiers:
            for modifier, value in party_modifiers.items():
                if modifier == "healer_present":
                    risk *= 0.8
                elif modifier == "tank_protection":
                    risk *= 0.7
                elif modifier == "party_size_bonus":
                    risk *= max(0.5, 1.0 - (value * 0.1))
        
        return min(0.95, risk)  # Cap at 95% to never guarantee death


@dataclass 
class DeathEvent:
    """Records a character death event"""
    character_name: str
    death_type: DeathType
    scenario_name: str
    final_risk: float
    timestamp: str
    location: str
    party_members: List[str]
    items_lost: List[str]
    resurrection_possible: bool = True


class PermadeathManager:
    """Manages permadeath mechanics and death scenarios"""
    
    def __init__(self):
        self.death_scenarios = self._create_death_scenarios()
        self.death_history: List[DeathEvent] = []
        self.resurrection_costs = {}  # character_name -> cost
    
    def _create_death_scenarios(self) -> Dict[str, DeathScenario]:
        """Create various death scenarios"""
        scenarios = {}
        
        # Combat scenarios
        scenarios["overwhelming_odds"] = DeathScenario(
            name="Overwhelming Odds",
            description="Facing far too many enemies at once",
            death_type=DeathType.COMBAT,
            base_risk=0.4,
            warning_signs=[
                "The enemy forces vastly outnumber your party",
                "Multiple powerful foes converge on your position",
                "Your weapons seem inadequate against these threats"
            ],
            possible_rewards=[
                "Legendary weapons from fallen champions",
                "Massive experience gains from epic battles",
                "Rare artifacts guarded by powerful enemies"
            ],
            mitigation_strategies=[
                "Retreat and return better prepared",
                "Use terrain and tactics to even the odds",
                "Focus fire on the most dangerous enemies first"
            ]
        )
        
        scenarios["boss_encounter"] = DeathScenario(
            name="Boss Encounter",
            description="Confronting a legendary creature of immense power",
            death_type=DeathType.COMBAT,
            base_risk=0.3,
            warning_signs=[
                "The air itself seems to tremble with power",
                "Ancient warnings speak of this creature's might",
                "Previous adventurers' remains litter the area"
            ],
            possible_rewards=[
                "Unique boss-specific legendary items",
                "Massive treasure hoards",
                "Story progression and world changes"
            ],
            mitigation_strategies=[
                "Study the boss's patterns and weaknesses",
                "Ensure full health and mana before engaging",
                "Coordinate party abilities for maximum effect"
            ]
        )
        
        # Trap scenarios
        scenarios["deadly_trap"] = DeathScenario(
            name="Deadly Trap",
            description="A lethal trap springs without warning",
            death_type=DeathType.TRAP,
            base_risk=0.25,
            warning_signs=[
                "Scratches on the floor suggest hidden mechanisms",
                "The dust patterns seem disturbed",
                "Previous victims' belongings are scattered about"
            ],
            possible_rewards=[
                "Treasure guarded by the trap",
                "Secret passages revealed after disarming",
                "Valuable trap components for crafting"
            ],
            mitigation_strategies=[
                "Search carefully before proceeding",
                "Send the most dexterous party member first",
                "Use ranged methods to trigger traps safely"
            ]
        )
        
        # Environmental scenarios
        scenarios["environmental_hazard"] = DeathScenario(
            name="Environmental Hazard",
            description="The environment itself becomes deadly",
            death_type=DeathType.ENVIRONMENTAL,
            base_risk=0.2,
            warning_signs=[
                "The air grows thin and hard to breathe",
                "Strange vapors rise from the ground",
                "The temperature becomes extreme"
            ],
            possible_rewards=[
                "Rare materials unique to dangerous environments",
                "Shortcuts through treacherous terrain",
                "Environmental resistance training"
            ],
            mitigation_strategies=[
                "Bring appropriate protective gear",
                "Move quickly through dangerous areas",
                "Use magic to protect against environmental effects"
            ]
        )
        
        # Magical scenarios
        scenarios["magical_catastrophe"] = DeathScenario(
            name="Magical Catastrophe",
            description="Wild magic or curse effects threaten existence",
            death_type=DeathType.MAGICAL,
            base_risk=0.35,
            warning_signs=[
                "Magic feels unstable and chaotic here",
                "Reality seems to bend and warp",
                "Previous spells have had unexpected effects"
            ],
            possible_rewards=[
                "Powerful magical artifacts",
                "New spell knowledge",
                "Magical essence for enchanting"
            ],
            mitigation_strategies=[
                "Avoid casting spells in unstable areas",
                "Use magical protection items",
                "Have dispel magic ready for emergencies"
            ]
        )
        
        # Sacrifice scenarios
        scenarios["heroic_sacrifice"] = DeathScenario(
            name="Heroic Sacrifice",
            description="Choosing to sacrifice oneself to save others",
            death_type=DeathType.SACRIFICE,
            base_risk=0.9,  # Very high since it's voluntary
            warning_signs=[
                "The situation seems impossible to escape",
                "Only one can hold the line while others flee",
                "A ritual requires a willing soul"
            ],
            possible_rewards=[
                "Saving the entire party",
                "Unlocking powerful story elements",
                "Becoming a legendary figure"
            ],
            mitigation_strategies=[
                "Look for alternative solutions",
                "Ensure the sacrifice will actually work",
                "Make sure it's truly necessary"
            ]
        )
        
        return scenarios
    
    def evaluate_situation_risk(self, situation_description: str, 
                               party_size: int = 1) -> Tuple[RiskLevel, List[DeathScenario]]:
        """Evaluate the risk level of a situation and return applicable scenarios"""
        applicable_scenarios = []
        total_risk = 0.0
        
        # Simple keyword matching to determine applicable scenarios
        description_lower = situation_description.lower()
        
        if any(word in description_lower for word in ["boss", "dragon", "demon", "legendary"]):
            applicable_scenarios.append(self.death_scenarios["boss_encounter"])
        
        if any(word in description_lower for word in ["overwhelming", "horde", "surrounded"]):
            applicable_scenarios.append(self.death_scenarios["overwhelming_odds"])
        
        if any(word in description_lower for word in ["trap", "mechanism", "pressure plate"]):
            applicable_scenarios.append(self.death_scenarios["deadly_trap"])
        
        if any(word in description_lower for word in ["poison", "gas", "lava", "cold"]):
            applicable_scenarios.append(self.death_scenarios["environmental_hazard"])
        
        if any(word in description_lower for word in ["curse", "magic", "spell", "enchantment"]):
            applicable_scenarios.append(self.death_scenarios["magical_catastrophe"])
        
        # Calculate average risk
        if applicable_scenarios:
            total_risk = sum(scenario.base_risk for scenario in applicable_scenarios) / len(applicable_scenarios)
        else:
            total_risk = 0.1  # Default low risk
        
        # Determine risk level
        if total_risk <= 0.1:
            risk_level = RiskLevel.MINIMAL
        elif total_risk <= 0.25:
            risk_level = RiskLevel.LOW
        elif total_risk <= 0.4:
            risk_level = RiskLevel.MODERATE
        elif total_risk <= 0.6:
            risk_level = RiskLevel.HIGH
        elif total_risk <= 0.8:
            risk_level = RiskLevel.EXTREME
        else:
            risk_level = RiskLevel.CERTAIN
        
        return risk_level, applicable_scenarios
    
    def roll_for_death(self, character: Character, scenario: DeathScenario,
                      party_modifiers: Dict = None) -> Tuple[bool, float]:
        """Roll to see if a character dies in a scenario"""
        final_risk = scenario.calculate_final_risk(character, party_modifiers)
        death_roll = random.random()
        
        died = death_roll < final_risk
        return died, final_risk
    
    def handle_character_death(self, character: Character, scenario: DeathScenario,
                             final_risk: float, location: str, 
                             party_members: List[str]) -> DeathEvent:
        """Handle a character death and create death event"""
        # Determine items lost (not all items are lost)
        items_lost = []
        if hasattr(character, 'inventory'):
            # Lose some random items, but not all
            num_items_lost = min(len(character.inventory), random.randint(1, 3))
            items_lost = random.sample(character.inventory, num_items_lost)
        
        # Create death event
        death_event = DeathEvent(
            character_name=character.name,
            death_type=scenario.death_type,
            scenario_name=scenario.name,
            final_risk=final_risk,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            location=location,
            party_members=party_members.copy(),
            items_lost=[str(item) for item in items_lost],
            resurrection_possible=(scenario.death_type != DeathType.SACRIFICE)
        )
        
        self.death_history.append(death_event)
        
        # Update character death count
        character.death_count += 1
        
        # Set resurrection cost
        base_cost = 100 * (character.death_count ** 2)  # Exponentially increasing cost
        self.resurrection_costs[character.name] = base_cost
        
        return death_event
    
    def can_resurrect(self, character_name: str) -> Tuple[bool, int, str]:
        """Check if a character can be resurrected and at what cost"""
        # Find most recent death
        recent_death = None
        for death in reversed(self.death_history):
            if death.character_name == character_name:
                recent_death = death
                break
        
        if not recent_death:
            return False, 0, "Character has not died"
        
        if not recent_death.resurrection_possible:
            return False, 0, "Death type prevents resurrection"
        
        cost = self.resurrection_costs.get(character_name, 100)
        return True, cost, "Resurrection possible"
    
    def resurrect_character(self, character: Character, paid_cost: int) -> bool:
        """Attempt to resurrect a character"""
        can_res, required_cost, reason = self.can_resurrect(character.name)
        
        if not can_res:
            return False
        
        if paid_cost < required_cost:
            return False
        
        # Resurrection successful
        character.stats.hp = character.stats.max_hp // 2  # Revive with half health
        character.death_count = max(0, character.death_count - 1)
        
        # Remove resurrection cost
        if character.name in self.resurrection_costs:
            del self.resurrection_costs[character.name]
        
        return True
    
    def get_risk_assessment(self, character: Character, situation: str) -> Dict:
        """Get a comprehensive risk assessment for a character and situation"""
        risk_level, scenarios = self.evaluate_situation_risk(situation)
        
        assessment = {
            "risk_level": risk_level.value,
            "scenarios": [],
            "character_survival_factors": [],
            "recommendations": []
        }
        
        # Analyze each scenario
        for scenario in scenarios:
            final_risk = scenario.calculate_final_risk(character)
            assessment["scenarios"].append({
                "name": scenario.name,
                "description": scenario.description,
                "base_risk": scenario.base_risk,
                "final_risk": final_risk,
                "death_type": scenario.death_type.value,
                "warning_signs": scenario.warning_signs,
                "mitigation_strategies": scenario.mitigation_strategies
            })
        
        # Character survival factors
        assessment["character_survival_factors"] = [
            f"Constitution: {character.stats.constitution} ({'high' if character.stats.constitution > 14 else 'average' if character.stats.constitution > 10 else 'low'})",
            f"Death Count: {character.death_count} (resurrection cost: {self.resurrection_costs.get(character.name, 100)})",
            f"Survival Traits: {[trait for trait in character.traits if any(word in trait.lower() for word in ['death', 'survival', 'hardy'])]}"
        ]
        
        # Risk-based recommendations
        if risk_level in [RiskLevel.HIGH, RiskLevel.EXTREME, RiskLevel.CERTAIN]:
            assessment["recommendations"].extend([
                "Consider retreat and better preparation",
                "Ensure party has healing capabilities",
                "Check equipment for durability and effectiveness"
            ])
        
        if character.death_count > 0:
            assessment["recommendations"].append(
                f"Character has died {character.death_count} time(s) - resurrection cost is now {self.resurrection_costs.get(character.name, 100)}"
            )
        
        return assessment
    
    def get_death_statistics(self) -> Dict:
        """Get statistics about deaths in the game"""
        if not self.death_history:
            return {"total_deaths": 0}
        
        stats = {
            "total_deaths": len(self.death_history),
            "deaths_by_type": {},
            "deaths_by_character": {},
            "average_risk_of_deaths": 0,
            "most_dangerous_locations": {},
            "resurrection_attempts": len(self.resurrection_costs)
        }
        
        # Count deaths by type
        for death in self.death_history:
            death_type = death.death_type.value
            stats["deaths_by_type"][death_type] = stats["deaths_by_type"].get(death_type, 0) + 1
            
            # Count by character
            char_name = death.character_name
            stats["deaths_by_character"][char_name] = stats["deaths_by_character"].get(char_name, 0) + 1
            
            # Count by location
            location = death.location
            stats["most_dangerous_locations"][location] = stats["most_dangerous_locations"].get(location, 0) + 1
        
        # Calculate average risk
        total_risk = sum(death.final_risk for death in self.death_history)
        stats["average_risk_of_deaths"] = total_risk / len(self.death_history)
        
        return stats
    
    def create_memorial(self, character_name: str) -> str:
        """Create a memorial text for a deceased character"""
        character_deaths = [death for death in self.death_history if death.character_name == character_name]
        
        if not character_deaths:
            return f"No record found for {character_name}"
        
        most_recent = character_deaths[-1]
        total_deaths = len(character_deaths)
        
        memorial = f"""
╔══════════════════════════════════════════════════════════════╗
║                        IN MEMORIAM                          ║
║                                                              ║
║  {character_name:^58}  ║
║                                                              ║
║  Fell to: {most_recent.scenario_name:<46}  ║
║  Death Type: {most_recent.death_type.value.title():<43}  ║
║  Location: {most_recent.location:<47}  ║
║  Risk Level: {int(most_recent.final_risk * 100):>3}%{'':<44}  ║
║                                                              ║
║  Total Deaths: {total_deaths:<48}  ║
║  Party Members Present: {', '.join(most_recent.party_members):<31}  ║
║                                                              ║
║  "Not all who wander are lost, but some are permanently     ║
║   lost to the dangers of adventure."                        ║
╚══════════════════════════════════════════════════════════════╝
        """
        
        return memorial.strip()