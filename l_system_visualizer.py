import pygame
import math
import pygame_gui
import json # Added for potential future rule parsing, though not used yet
import random # Added import


class LSystem:
    """Represents an L-System with an axiom and production rules."""

    def __init__(self, axiom, rules):
        self.axiom = axiom
        self.rules = rules
        self.current_string = axiom

    def generate(self, iterations):
        """Generate the L-System string for a given number of iterations."""
        for _ in range(iterations):
            next_string = ""
            for char in self.current_string:
                next_string += self.rules.get(char, char)
            self.current_string = next_string
        return self.current_string


class Turtle:
    """Simulates a turtle for drawing based on L-System commands."""

    def __init__(self, x, y, angle_deg):
        self.x = x
        self.y = y
        self.angle_rad = math.radians(angle_deg)
        self.stack = []  # Stack to save turtle state (position and angle)

    def turn_left(self, angle_rad):
        """Turn the turtle left by a given angle in radians."""
        self.angle_rad -= angle_rad

    def turn_right(self, angle_rad):
        """Turn the turtle right by a given angle in radians."""
        self.angle_rad += angle_rad

    def move_forward(self, screen, length, color, thickness):
        """Move the turtle forward, drawing a line."""
        end_x = self.x + length * math.cos(self.angle_rad)
        end_y = self.y - length * math.sin(self.angle_rad)
        pygame.draw.line(screen, color, (int(self.x), int(self.y)), (int(end_x), int(end_y)), thickness)
        self.x = end_x
        self.y = end_y

    def push_state(self):
        """Save the current state (position and angle) onto the stack."""
        self.stack.append(((self.x, self.y), self.angle_rad))

    def pop_state(self):
        """Restore the state from the top of the stack."""
        if self.stack:
            (self.x, self.y), self.angle_rad = self.stack.pop()


def parse_rules(rules_string):
    """Parses a string like 'F:FF,X:F+[[X]-X]-F[-FX]+X' into a dictionary."""
    rules = {}
    try:
        pairs = rules_string.split(',')
        for pair in pairs:
            if ':' in pair:
                key, value = pair.split(':', 1)
                rules[key.strip()] = value.strip()
    except Exception as e:
        print(f"Error parsing rules: {e}. Using empty rules.")
        return {} # Return empty dict on error
    return rules

def draw_lsystem(screen, lsystem_string, start_pos, start_angle, angle_deg, length, line_color, line_thickness, background_color, angle_variation_deg, length_variation_factor):
    """Draws the L-System using the Turtle with randomized variations."""
    turtle = Turtle(start_pos[0], start_pos[1], start_angle)
    screen.fill(background_color)

    for command in lsystem_string:
        if command == 'F':
            current_length = length * random.uniform(1.0 - length_variation_factor, 1.0 + length_variation_factor)
            turtle.move_forward(screen, current_length, line_color, line_thickness)
        elif command == '+':
            turn_angle = angle_deg + random.uniform(-angle_variation_deg, angle_variation_deg)
            turtle.turn_right(math.radians(turn_angle))
        elif command == '-':
            turn_angle = angle_deg + random.uniform(-angle_variation_deg, angle_variation_deg)
            turtle.turn_left(math.radians(turn_angle))
        elif command == '[':
            turtle.push_state()
        elif command == ']':
            turtle.pop_state()
        # Other characters are ignored


# --- Pygame & Pygame GUI Setup ---
pygame.init()

# Default Settings
DEFAULT_SETTINGS = {
    "axiom": "X",
    "rules_string": "X:F+[[X]-X]-F[-FX]+X,F:FF", # String representation
    "iterations": 5,
    "angle_deg": 25.0,
    "start_angle_deg": 90.0,
    "length": 5.0,
    "start_pos": (400, 600),
    "line_thickness": 1,
    "line_color": (0, 255, 0),       # Green
    "background_color": (0, 0, 0), # Black
    "screen_width": 800,
    "screen_height": 600,
    "start_x_ratio": 0.5,           # Start X at 50% of screen width
    "start_y_ratio": 1.0,           # Start Y at 100% of screen height (bottom)
    "angle_variation_deg": 3.0,     # Added: Max random angle variation in degrees
    "length_variation_factor": 0.05 # Added: Max random length variation (e.g., 0.05 = +/- 5%)
}
current_settings = DEFAULT_SETTINGS.copy()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("L-System Plant Visualizer")

# GUI Manager
ui_manager = pygame_gui.UIManager((screen_width, screen_height))

# GUI Elements (Keep main buttons)
settings_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((10, 10), (100, 30)),
    text='Settings',
    manager=ui_manager
)
apply_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((120, 10), (100, 30)),
    text='Redraw', # Changed text
    manager=ui_manager
)

# Settings Window Class
class SettingsWindow(pygame_gui.elements.UIWindow):
    def __init__(self, manager, initial_settings):
        super().__init__(pygame.Rect(150, 50, 400, 550), manager=manager, window_display_title="L-System Settings") # Increased height slightly

        self.settings = initial_settings.copy() # Work on a copy
        self.ui_elements = {}

        # Layout variables
        current_y = 10
        label_width = 150
        entry_width = 200
        row_height = 30
        input_height = 25
        margin = 10

        # Helper to create label and entry row
        def create_setting_row(key, label_text):
            nonlocal current_y
            # Label
            pygame_gui.elements.UILabel(relative_rect=pygame.Rect(margin, current_y, label_width, input_height),
                                        text=label_text,
                                        manager=manager,
                                        container=self)
            # Entry Line
            entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(margin + label_width + margin, current_y, entry_width, input_height),
                                                         manager=manager,
                                                         container=self)
            entry.set_text(str(self.settings.get(key, "")))
            self.ui_elements[key] = entry
            current_y += row_height
            return entry # Return the entry element

        # Create UI Elements for each setting
        create_setting_row("axiom", "Axiom:")
        create_setting_row("rules_string", "Rules (comma-sep):")
        iterations_entry = create_setting_row("iterations", "Iterations:") # Get the entry element

        # Add warning label below iterations
        self.iteration_warning_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(margin + label_width + margin, current_y, entry_width, input_height),
            text="Warning: >10 may freeze!",
            manager=manager,
            container=self,
            object_id='#warning_label' # Optional: for styling later
        )
        self.iteration_warning_label.hide() # Initially hidden
        current_y += row_height # Increment Y position after adding the label


        create_setting_row("angle_deg", "Angle (degrees):")
        create_setting_row("start_angle_deg", "Start Angle (deg):")
        create_setting_row("length", "Segment Length:")
        create_setting_row("line_thickness", "Line Thickness:")
        create_setting_row("angle_variation_deg", "Angle Variation (deg):")
        create_setting_row("length_variation_factor", "Length Variation (%):")

        current_y += margin # Add space before button

        # Apply Button (inside the window)
        self.apply_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(margin, current_y, 100, 30),
                                                         text='Apply',
                                                         manager=manager,
                                                         container=self)

    def process_event(self, event):
        # Handle text entry changes to show/hide warning
        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED and event.ui_element == self.ui_elements["iterations"]:
            try:
                iter_val = int(event.text)
                if iter_val > 10:
                    self.iteration_warning_label.show()
                else:
                    self.iteration_warning_label.hide()
            except ValueError:
                self.iteration_warning_label.hide() # Hide if not a valid int

        # Handle internal apply button press
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.apply_button:
                print("Settings Apply button clicked (inside window)")
                # Update the internal settings dictionary from UI elements
                try:
                    self.settings["axiom"] = self.ui_elements["axiom"].get_text()
                    self.settings["rules_string"] = self.ui_elements["rules_string"].get_text()
                    # Use helper for numeric conversions
                    self.settings["iterations"] = self._get_int_from_entry("iterations")
                    self.settings["angle_deg"] = self._get_float_from_entry("angle_deg")
                    self.settings["start_angle_deg"] = self._get_float_from_entry("start_angle_deg")
                    self.settings["length"] = self._get_float_from_entry("length")
                    self.settings["line_thickness"] = self._get_int_from_entry("line_thickness")
                    self.settings["angle_variation_deg"] = self._get_float_from_entry("angle_variation_deg")
                    self.settings["length_variation_factor"] = self._get_float_from_entry("length_variation_factor")

                    print("Settings applied:", self.settings)
                    return True # Indicate settings were applied
                except ValueError as e:
                    print(f"Error applying settings: Invalid input - {e}")
                    # Optionally show an error message to the user here
                    return False # Indicate settings were NOT applied successfully
        return False # No settings applied from this event

    # Helper methods for safe type conversion
    def _get_int_from_entry(self, key):
        try:
            return int(self.ui_elements[key].get_text())
        except ValueError:
            print(f"Warning: Invalid integer input for '{key}'. Using default.")
            return DEFAULT_SETTINGS[key] # Fallback to default

    def _get_float_from_entry(self, key):
        try:
            return float(self.ui_elements[key].get_text())
        except ValueError:
            print(f"Warning: Invalid float input for '{key}'. Using default.")
            return DEFAULT_SETTINGS[key] # Fallback to default

    def get_applied_settings(self):
        """Returns the validated settings from the window."""
        # This assumes process_event was called and returned True
        return self.settings.copy()


settings_window = None # Variable to hold the window instance

# --- L-System Generation & Drawing Function ---
def generate_and_draw(screen, settings):
    """Generates the L-System string and draws it."""
    print("Generating with settings:", settings) # Debug print

    # --- Add Console Warning ---
    if settings["iterations"] > 10:
        print(f"WARNING: Generating with {settings['iterations']} iterations. This may take a long time or freeze.")
    # -------------------------

    rules_dict = parse_rules(settings["rules_string"])
    lsystem = LSystem(settings["axiom"], rules_dict)
    lsystem_string = lsystem.generate(settings["iterations"])

    print(f"Generated string length: {len(lsystem_string)}") # Info

    screen.fill(settings["background_color"]) # Clear screen before drawing

    # --- Add Drawing Time Warning (Start) ---
    start_time = pygame.time.get_ticks()
    # ---------------------------------------

    draw_lsystem(
        screen=screen,
        lsystem_string=lsystem_string,
        start_pos=settings["start_pos"],
        start_angle=settings["start_angle_deg"],
        angle_deg=settings["angle_deg"],
        length=settings["length"],
        line_color=settings["line_color"],
        line_thickness=settings["line_thickness"],
        background_color=settings["background_color"],
        angle_variation_deg=settings["angle_variation_deg"],
        length_variation_factor=settings["length_variation_factor"]
    )

    # --- Add Drawing Time Warning (End) ---
    end_time = pygame.time.get_ticks()
    draw_duration_ms = end_time - start_time
    print(f"Drawing took {draw_duration_ms} ms.")
    if draw_duration_ms > 3000: # If drawing takes > 3 seconds
         print("WARNING: Drawing took a long time. Consider reducing iterations or complexity.")
    # ------------------------------------

    pygame.display.flip() # Update the full display


# --- Main Loop ---
clock = pygame.time.Clock()
running = True
needs_redraw = True # Flag to draw initially

while running:
    time_delta = clock.tick(60) / 1000.0

    # --- Event Handling ---
    settings_applied = False # Flag to check if settings window applied changes
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle events for the settings window if it exists
        if settings_window:
             if settings_window.process_event(event):
                 settings_applied = True # Settings were applied by the window
                 needs_redraw = True     # Trigger redraw
                 current_settings = settings_window.get_applied_settings()
                 settings_window.kill()  # Close window after applying
                 settings_window = None
                 print("Settings applied from window, window closed.")

        # Handle events for the main UI manager
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == settings_button:
                # Create window only if it doesn't exist
                if not settings_window:
                    settings_window = SettingsWindow(ui_manager, current_settings)
                    print("Settings button clicked - window opened")
                else:
                    # If window exists, maybe bring it to front (optional)
                    # settings_window.show() # Or some other focus mechanism if available
                    print("Settings button clicked - window already open")

            elif event.ui_element == apply_button:
                print("Redraw button clicked")
                needs_redraw = True # Trigger redraw with current settings

        ui_manager.process_events(event)

    # --- Update ---
    ui_manager.update(time_delta)

    # --- Drawing ---
    if needs_redraw:
        generate_and_draw(screen, current_settings)
        needs_redraw = False # Reset flag

    # Draw UI elements on top
    ui_manager.draw_ui(screen)

    pygame.display.flip() # Flip only once at the end?

pygame.quit() 