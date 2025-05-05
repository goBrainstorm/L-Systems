import math # Although not used directly in this class, keep for potential future rule features
import random # Keep for potential future rule features
import json # Keep for potential future rule features

class LSystem:
    """Represents an L-System with an axiom and production rules."""

    def __init__(self, axiom, rules):
        self.axiom = axiom
        self.rules = rules # Expects a dictionary e.g., {'F': 'FF', 'X': '...'}
        self.current_string = axiom

    def generate(self, iterations):
        """Generate the L-System string for a given number of iterations."""
        self.current_string = self.axiom # Reset for generation
        for _ in range(iterations):
            next_string = ""
            for char in self.current_string:
                # Get the rule for the character, or the character itself if no rule exists
                next_string += self.rules.get(char, char)
            self.current_string = next_string
        return self.current_string

    # Consider adding a method to parse rules from string here later
    # def parse_rules_from_string(self, rules_string): ... 