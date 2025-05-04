import pygame
import math
import pygame_gui
import json # Added for potential future rule parsing, though not used yet


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

    def turn_left(self, angle_deg):
        self.angle_rad += math.radians(angle_deg)

    def turn_right(self, angle_deg):
        self.angle_rad -= math.radians(angle_deg)

    def move_forward(self, distance, screen, color, thickness):
        """Move forward, drawing a line."""
        end_x = self.x + distance * math.cos(self.angle_rad)
        end_y = self.y + distance * math.sin(self.angle_rad)
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

def draw_lsystem(screen, lsystem_string, start_pos, start_angle, angle_deg, length, line_color, line_thickness, background_color):
    """Draws the L-System using the Turtle."""
    turtle = Turtle(start_pos[0], start_pos[1], start_angle)
    screen.fill(background_color)

    for command in lsystem_string:
        if command == 'F':
            turtle.move_forward(length, screen, line_color, line_thickness)
        elif command == '+':
            turtle.turn_right(angle_deg) # Turn right
        elif command == '-':
            turtle.turn_left(angle_deg)  # Turn left
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
    "angle": 25.0,
    "length": 10.0,
    "start_pos": (400, 600),
    "start_angle": -90, # Pointing upwards
    "line_thickness": 1,
    "line_color": (0, 200, 0),
    "background_color": (10, 10, 40)
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
    def __init__(self, manager, current_settings_ref):
        super().__init__(pygame.Rect((100, 50), (450, 350)), manager=manager,
                         window_display_title='L-System Settings', object_id='#settings_window')

        self.current_settings_ref = current_settings_ref
        self.manager = manager

        # --- UI Elements for Settings ---
        y_pos = 10
        label_width = 100
        entry_width = 280
        input_height = 30
        padding = 5

        # Iterations
        pygame_gui.elements.UILabel(pygame.Rect((10, y_pos), (label_width, input_height)),
                                    'Iterations:', manager=self.manager, container=self)
        self.iterations_entry = pygame_gui.elements.UITextEntryLine(pygame.Rect((label_width + 15, y_pos), (entry_width, input_height)),
                                                                      manager=self.manager, container=self, object_id='#iterations_entry')
        self.iterations_entry.set_text(str(self.current_settings_ref['iterations']))
        y_pos += input_height + padding

        # Angle
        pygame_gui.elements.UILabel(pygame.Rect((10, y_pos), (label_width, input_height)),
                                    'Angle (°):', manager=self.manager, container=self)
        self.angle_entry = pygame_gui.elements.UITextEntryLine(pygame.Rect((label_width + 15, y_pos), (entry_width, input_height)),
                                                                 manager=self.manager, container=self, object_id='#angle_entry')
        self.angle_entry.set_text(str(self.current_settings_ref['angle']))
        y_pos += input_height + padding

        # Length
        pygame_gui.elements.UILabel(pygame.Rect((10, y_pos), (label_width, input_height)),
                                    'Length:', manager=self.manager, container=self)
        self.length_entry = pygame_gui.elements.UITextEntryLine(pygame.Rect((label_width + 15, y_pos), (entry_width, input_height)),
                                                                  manager=self.manager, container=self, object_id='#length_entry')
        self.length_entry.set_text(str(self.current_settings_ref['length']))
        y_pos += input_height + padding

        # Axiom
        pygame_gui.elements.UILabel(pygame.Rect((10, y_pos), (label_width, input_height)),
                                    'Axiom:', manager=self.manager, container=self)
        self.axiom_entry = pygame_gui.elements.UITextEntryLine(pygame.Rect((label_width + 15, y_pos), (entry_width, input_height)),
                                                                 manager=self.manager, container=self, object_id='#axiom_entry')
        self.axiom_entry.set_text(self.current_settings_ref['axiom'])
        y_pos += input_height + padding

        # Rules (using a simple text line for now)
        pygame_gui.elements.UILabel(pygame.Rect((10, y_pos), (label_width, input_height)),
                                    'Rules:', manager=self.manager, container=self)
        self.rules_entry = pygame_gui.elements.UITextEntryLine(pygame.Rect((label_width + 15, y_pos), (entry_width, input_height*2)), # Taller entry
                                                                 manager=self.manager, container=self, object_id='#rules_entry')
        self.rules_entry.set_text(self.current_settings_ref['rules_string'])
        y_pos += input_height*2 + padding * 5 # More padding before button


        # Apply & Close Button
        self.apply_close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.rect.width - 160, y_pos), (150, 35)),
            text='Apply & Close',
            manager=self.manager,
            container=self,
            object_id='#apply_close_button'
        )

    def process_event(self, event):
        super().process_event(event) # Important for window interaction

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.apply_close_button:
                try:
                    # Validate and update settings
                    new_iterations = int(self.iterations_entry.get_text())
                    new_angle = float(self.angle_entry.get_text())
                    new_length = float(self.length_entry.get_text())
                    new_axiom = self.axiom_entry.get_text()
                    new_rules_string = self.rules_entry.get_text()

                    if new_iterations <= 0 or new_length <= 0:
                        raise ValueError("Iterations and Length must be positive.")

                    self.current_settings_ref['iterations'] = new_iterations
                    self.current_settings_ref['angle'] = new_angle
                    self.current_settings_ref['length'] = new_length
                    self.current_settings_ref['axiom'] = new_axiom
                    self.current_settings_ref['rules_string'] = new_rules_string

                    print("Settings Applied:", self.current_settings_ref)
                    self.kill() # Close the window
                    # Signal that settings were applied (optional, could use custom events)
                    return True # Indicate settings applied

                except ValueError as e:
                    print(f"Invalid input: {e}")
                    # Optional: Show an error message window
                    pygame_gui.windows.UIMessageWindow(
                        rect=pygame.Rect((200, 150), (300, 150)),
                        html_message=f"Invalid input: {e}. Please check values.",
                        manager=self.manager
                    )
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                    pygame_gui.windows.UIMessageWindow(
                        rect=pygame.Rect((200, 150), (300, 150)),
                        html_message=f"Error: {e}",
                        manager=self.manager
                    )
        return False # Indicate settings not applied or no relevant event


settings_window = None # Variable to hold the window instance

# --- L-System Generation & Drawing Function ---
def generate_and_draw(screen, settings):
    """Generates the L-System string and draws it."""
    print("Generating with settings:", settings) # Debug print
    rules_dict = parse_rules(settings["rules_string"])
    lsystem = LSystem(settings["axiom"], rules_dict)
    lsystem_string = lsystem.generate(settings["iterations"])

    screen.fill(settings["background_color"]) # Clear screen before drawing

    draw_lsystem(
        screen=screen,
        lsystem_string=lsystem_string,
        start_pos=settings["start_pos"],
        start_angle=settings["start_angle"],
        angle_deg=settings["angle"],
        length=settings["length"],
        line_color=settings["line_color"],
        line_thickness=settings["line_thickness"],
        background_color=settings["background_color"] # Pass background color
    )
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

        # Handle events for the main UI manager
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == settings_button:
                # Close existing window if open, before creating a new one
                if settings_window:
                    settings_window.kill()
                settings_window = SettingsWindow(ui_manager, current_settings)
                print("Settings button clicked - window opened")

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