import math
import random

class Turtle:
    """Simulates a turtle for interpreting L-System commands and generating drawing data."""

    def __init__(self, x, y, angle_deg):
        self.start_x = x
        self.start_y = y
        self.start_angle_rad = math.radians(angle_deg)
        self.reset()

    def reset(self):
        """Reset turtle to its initial state and clear commands."""
        self.x = self.start_x
        self.y = self.start_y
        self.angle_rad = self.start_angle_rad
        self.stack = []  # Stack to save turtle state (position and angle)
        # Store drawing commands (e.g., line segments)
        # Format: [ ((x1, y1), (x2, y2)), ... ]
        self.drawing_commands = []
        # Keep track of bounds for scaling
        self.min_x = self.x
        self.max_x = self.x
        self.min_y = self.y
        self.max_y = self.y

    def _update_bounds(self):
        self.min_x = min(self.min_x, self.x)
        self.max_x = max(self.max_x, self.x)
        self.min_y = min(self.min_y, self.y)
        self.max_y = max(self.max_y, self.y)

    def turn_left(self, angle_rad):
        """Turn the turtle left by a given angle in radians."""
        self.angle_rad -= angle_rad

    def turn_right(self, angle_rad):
        """Turn the turtle right by a given angle in radians."""
        self.angle_rad += angle_rad

    def move_forward(self, length):
        """Move the turtle forward, recording the line segment."""
        start_pos = (self.x, self.y)
        self.x += length * math.cos(self.angle_rad)
        self.y -= length * math.sin(self.angle_rad)
        end_pos = (self.x, self.y)
        self.drawing_commands.append((start_pos, end_pos))
        self._update_bounds() # Update bounds after moving

    def push_state(self):
        """Save the current state (position and angle) onto the stack."""
        self.stack.append(((self.x, self.y), self.angle_rad))

    def pop_state(self):
        """Restore the state from the top of the stack."""
        if self.stack:
            (self.x, self.y), self.angle_rad = self.stack.pop()
            # Note: We don't update bounds when popping, as the turtle teleports

    def interpret(self, lsystem_string, angle_deg, length, angle_variation_deg=0.0, length_variation_factor=0.0):
        """Interpret the L-system string and generate drawing commands with variations."""
        self.reset()
        base_angle_rad = math.radians(angle_deg)

        for command in lsystem_string:
            if command == 'F' or command == 'A' or command == 'B': # Treat F, A, B as draw forward
                current_length = length * random.uniform(1.0 - length_variation_factor, 1.0 + length_variation_factor)
                if current_length > 0: # Avoid zero-length moves
                    self.move_forward(current_length)
            elif command == '+':
                turn_angle = base_angle_rad + math.radians(random.uniform(-angle_variation_deg, angle_variation_deg))
                self.turn_right(turn_angle)
            elif command == '-':
                turn_angle = base_angle_rad + math.radians(random.uniform(-angle_variation_deg, angle_variation_deg))
                self.turn_left(turn_angle)
            elif command == '[':
                self.push_state()
            elif command == ']':
                self.pop_state()
            # Ignore other characters

        # Ensure bounds have some dimension if it was just a point or straight line
        if self.min_x == self.max_x: self.max_x += 1
        if self.min_y == self.max_y: self.max_y += 1

        return self.drawing_commands, (self.min_x, self.min_y, self.max_x, self.max_y)

    # Note: The _sim_ methods from the original file are effectively replaced by the interpret method
    # which calculates bounds directly. The separate calculate_lsystem_bounds function will be removed later. 