import pygame
import math
import pygame_gui
import json # Added for potential future rule parsing, though not used yet
import random # Added import
import sys # Added for float max/min

# --- Constants ---
DRAWING_PADDING = 50
# Add slider precision constants
SLIDER_FLOAT_PRECISION = 1 # How many decimal places for float sliders


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

    def __init__(self, x, y, angle_deg, scale_factor=1.0, offset=(0, 0)):
        self.x = x
        self.y = y
        self.angle_rad = math.radians(angle_deg)
        self.stack = []  # Stack to save turtle state (position and angle)
        self.scale_factor = scale_factor
        self.offset = offset

    def turn_left(self, angle_rad):
        """Turn the turtle left by a given angle in radians."""
        self.angle_rad -= angle_rad

    def turn_right(self, angle_rad):
        """Turn the turtle right by a given angle in radians."""
        self.angle_rad += angle_rad

    def move_forward(self, screen, length, color, thickness):
        """Move the turtle forward, drawing a line (scaled and offset)."""
        end_x = self.x + length * math.cos(self.angle_rad)
        end_y = self.y - length * math.sin(self.angle_rad)

        screen_start_x = self.x * self.scale_factor + self.offset[0]
        screen_start_y = self.y * self.scale_factor + self.offset[1]
        screen_end_x = end_x * self.scale_factor + self.offset[0]
        screen_end_y = end_y * self.scale_factor + self.offset[1]

        pygame.draw.line(screen, color,
                         (int(screen_start_x), int(screen_start_y)),
                         (int(screen_end_x), int(screen_end_y)), thickness)

        self.x = end_x
        self.y = end_y

    def push_state(self):
        """Save the current state (position and angle) onto the stack."""
        self.stack.append(((self.x, self.y), self.angle_rad))

    def pop_state(self):
        """Restore the state from the top of the stack."""
        if self.stack:
            (self.x, self.y), self.angle_rad = self.stack.pop()

    def _sim_turn_left(self, angle_rad):
        self.angle_rad -= angle_rad

    def _sim_turn_right(self, angle_rad):
        self.angle_rad += angle_rad

    def _sim_move_forward(self, length):
        self.x += length * math.cos(self.angle_rad)
        self.y -= length * math.sin(self.angle_rad)


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

def calculate_lsystem_bounds(lsystem_string, start_pos, start_angle, angle_deg, length):
    """Simulates the L-System path to find its bounding box."""
    sim_turtle = Turtle(start_pos[0], start_pos[1], start_angle)
    min_x, max_x = start_pos[0], start_pos[0]
    min_y, max_y = start_pos[1], start_pos[1]

    base_angle_rad = math.radians(angle_deg)

    for command in lsystem_string:
        if command == 'F':
            sim_turtle._sim_move_forward(length)
            min_x = min(min_x, sim_turtle.x)
            max_x = max(max_x, sim_turtle.x)
            min_y = min(min_y, sim_turtle.y)
            max_y = max(max_y, sim_turtle.y)
        elif command == '+':
            sim_turtle._sim_turn_right(base_angle_rad)
        elif command == '-':
            sim_turtle._sim_turn_left(base_angle_rad)
        elif command == '[':
            sim_turtle.push_state()
        elif command == ']':
            sim_turtle.pop_state()

    if min_x == max_x: max_x += 1
    if min_y == max_y: max_y += 1

    return min_x, min_y, max_x, max_y

def draw_lsystem(screen, lsystem_string, start_pos, start_angle, angle_deg, length,
                   line_color, line_thickness, background_color,
                   angle_variation_deg, length_variation_factor,
                   scale_factor, offset):
    """Draws the L-System using the Turtle with variations, scale, and offset."""
    turtle = Turtle(start_pos[0], start_pos[1], start_angle, scale_factor, offset)

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
    "line_thickness": 1,
    "start_pos": (400, 600), # Base start pos, updated by ratio below
    "line_color": (0, 255, 0),       # Green
    "background_color": (0, 0, 0), # Black
    # Ratios for dynamic start position
    "start_x_ratio": 0.5,
    "start_y_ratio": 1.0,
    "angle_variation_deg": 3.0,
    "length_variation_factor": 0.05
}
current_settings = DEFAULT_SETTINGS.copy()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("L-System Plant Visualizer")

# === Create a separate surface for the L-System drawing ===
lsystem_surface = pygame.Surface((screen_width, screen_height))

# Update initial start_pos based on ratios
current_settings["start_pos"] = (
    screen_width * current_settings["start_x_ratio"],
    screen_height * current_settings["start_y_ratio"]
)

# GUI Manager
ui_manager = pygame_gui.UIManager((screen_width, screen_height))

# GUI Elements (Main Buttons)
settings_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((10, 10), (100, 30)),
    text='Settings',
    manager=ui_manager
)
apply_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((120, 10), (100, 30)),
    text='Redraw',
    manager=ui_manager
)

# Settings Window Class (Modified for Sliders)
class SettingsWindow(pygame_gui.elements.UIWindow):
    def __init__(self, manager, initial_settings):
        # Increased width for sliders and value labels
        super().__init__(pygame.Rect(150, 50, 550, 550), manager=manager, window_display_title="L-System Settings")

        self.settings = initial_settings.copy() # Work on a copy
        self.ui_elements = {} # Store sliders, entries, and value labels

        # Layout variables
        current_y = 10
        label_width = 150
        entry_width = 350 # Adjusted width for entries
        slider_width = 250 # Width for sliders
        value_label_width = 80 # Width for slider value labels
        row_height = 40 # Increased row height for sliders
        input_height = 30
        margin = 10

        # --- Helper to create label and text entry row ---
        def create_text_entry_row(key, label_text):
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

        # --- Helper to create label, slider, and value label row ---
        def create_slider_row(key, label_text, value_range, is_float=True):
            nonlocal current_y
            start_value = self.settings.get(key, value_range[0])
            # Label
            pygame_gui.elements.UILabel(relative_rect=pygame.Rect(margin, current_y, label_width, input_height),
                                        text=label_text,
                                        manager=manager,
                                        container=self)
            # Slider
            slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect(margin + label_width + margin, current_y, slider_width, input_height),
                                                            start_value=start_value,
                                                            value_range=value_range,
                                                            manager=manager,
                                                            container=self)
            self.ui_elements[key] = slider

            # Value Label
            value_text = f"{start_value:.{SLIDER_FLOAT_PRECISION}f}" if is_float else str(int(start_value))
            value_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(margin + label_width + margin + slider_width + margin, current_y, value_label_width, input_height),
                                                     text=value_text,
                                                     manager=manager,
                                                     container=self)
            self.ui_elements[key + "_label"] = value_label # Store label for updates
            current_y += row_height
            return slider

        # --- Create UI Elements --- 
        # Text Entries
        create_text_entry_row("axiom", "Axiom:")
        create_text_entry_row("rules_string", "Rules (comma-sep):")
        iterations_entry = create_text_entry_row("iterations", "Iterations:")

        # Iteration Warning Label (Position adjusted)
        self.iteration_warning_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(margin + label_width + margin, current_y - row_height + input_height - 10, entry_width, 20), # Position below entry
            text="Warning: >10 may freeze!",
            manager=manager,
            container=self,
            object_id='#warning_label'
        )
        self.iteration_warning_label.hide()
        # current_y adjusted by helper

        # Sliders
        create_slider_row("angle_deg", "Angle (degrees):", (0.0, 180.0), is_float=True)
        create_slider_row("start_angle_deg", "Start Angle (deg):", (0.0, 360.0), is_float=True)
        create_slider_row("length", "Segment Length:", (1.0, 30.0), is_float=True)
        create_slider_row("line_thickness", "Line Thickness:", (1, 10), is_float=False) # Integer slider
        create_slider_row("angle_variation_deg", "Angle Variation (deg):", (0.0, 45.0), is_float=True)
        create_slider_row("length_variation_factor", "Length Variation (%):", (0.0, 0.5), is_float=True)

        # Adjust Y slightly before Apply button
        current_y += margin

        # Apply Button (inside the window)
        self.apply_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(margin, current_y, 100, 30),
                                                         text='Apply',
                                                         manager=manager,
                                                         container=self,
                                                         object_id='#settings_apply_button' # Keep the ID
                                                         )

    # --- Optional: Add a method to update internal settings from UI elements just before applying ---
    def update_settings_from_ui(self):
        """Reads current values from UI elements and updates internal dict. Returns True on success, False on error."""
        try:
            # Text Entries
            self.settings["axiom"] = self.ui_elements["axiom"].get_text()
            self.settings["rules_string"] = self.ui_elements["rules_string"].get_text()
            iter_val = int(self.ui_elements["iterations"].get_text())
            if iter_val < 0:
                print("Warning: Invalid negative iterations. Clamping to 0.")
                iter_val = 0
                self.ui_elements["iterations"].set_text("0") # Update UI
            self.settings["iterations"] = iter_val

            # Sliders (read their current value)
            for key, element in self.ui_elements.items():
                if isinstance(element, pygame_gui.elements.UIHorizontalSlider):
                    self.settings[key] = element.get_current_value()
            
            print("[Debug] SettingsWindow: update_settings_from_ui successful.")
            return True
        except ValueError as e:
            print(f"Error reading settings from UI (likely iterations): Invalid input - {e}")
            # Optionally show error message
            return False
        except Exception as e:
            print(f"An unexpected error occurred reading settings from UI: {e}")
            return False

    def get_applied_settings(self):
        """Returns the validated settings from the window."""
        # Assumes update_settings_from_ui was called successfully before this
        return self.settings.copy()


settings_window = None # Variable to hold the window instance

# --- L-System Generation & Drawing Function (Modified for Scaling) ---
# === Modify to draw onto a target surface ===
def generate_and_draw(target_surface, settings):
    """Generates the L-System string, calculates scale/offset, and draws it onto the target_surface."""
    print("Generating with settings:", settings) # Debug print

    # --- Console Warning ---
    if settings["iterations"] > 10:
        print(f"WARNING: Generating with {settings['iterations']} iterations...")
    # --- Generate String ---
    rules_dict = parse_rules(settings["rules_string"])
    lsystem = LSystem(settings["axiom"], rules_dict)
    lsystem_string = lsystem.generate(settings["iterations"])
    print(f"Generated string length: {len(lsystem_string)}")

    # --- Calculate Bounds (using deterministic parameters) ---
    print("Calculating bounds...")
    min_x, min_y, max_x, max_y = calculate_lsystem_bounds(
        lsystem_string=lsystem_string,
        start_pos=settings["start_pos"], # Use the logical start pos
        start_angle=settings["start_angle_deg"],
        angle_deg=settings["angle_deg"],
        length=settings["length"]
    )
    bounds_width = max_x - min_x
    bounds_height = max_y - min_y
    print(f"Bounds: X({min_x:.1f}, {max_x:.1f}), Y({min_y:.1f}, {max_y:.1f}), W={bounds_width:.1f}, H={bounds_height:.1f}")

    # --- Calculate Scale Factor & Offset ---
    drawable_width = screen_width - 2 * DRAWING_PADDING
    drawable_height = screen_height - 2 * DRAWING_PADDING

    scale_factor = 1.0
    if bounds_width > 0 and bounds_height > 0:
        scale_x = drawable_width / bounds_width
        scale_y = drawable_height / bounds_height
        scale_factor = min(scale_x, scale_y)
    elif bounds_width > 0: # Height is 0 (horizontal line)
        scale_factor = drawable_width / bounds_width
    elif bounds_height > 0: # Width is 0 (vertical line)
        scale_factor = drawable_height / bounds_height
    # Optional: Prevent scaling up if it's already small
    # scale_factor = min(scale_factor, 1.0)
    print(f"Scale factor: {scale_factor:.3f}")

    # Center the scaled drawing
    scaled_width = bounds_width * scale_factor
    scaled_height = bounds_height * scale_factor
    offset_x = DRAWING_PADDING + (drawable_width - scaled_width) / 2 - (min_x * scale_factor)
    offset_y = DRAWING_PADDING + (drawable_height - scaled_height) / 2 - (min_y * scale_factor)
    offset = (offset_x, offset_y)
    print(f"Offset: ({offset_x:.1f}, {offset_y:.1f})")

    # === Clear the target surface ===
    target_surface.fill(settings["background_color"])

    # --- Draw L-System onto the target surface ---
    print("Drawing L-System...")
    start_time = pygame.time.get_ticks()
    draw_lsystem(
        screen=target_surface, # Draw onto the dedicated surface
        lsystem_string=lsystem_string,
        start_pos=settings["start_pos"],
        start_angle=settings["start_angle_deg"],
        angle_deg=settings["angle_deg"],
        length=settings["length"],
        line_color=settings["line_color"],
        line_thickness=settings["line_thickness"],
        background_color=settings["background_color"],
        angle_variation_deg=settings["angle_variation_deg"],
        length_variation_factor=settings["length_variation_factor"],
        scale_factor=scale_factor,
        offset=offset
    )
    end_time = pygame.time.get_ticks()
    draw_duration_ms = end_time - start_time
    print(f"Drawing took {draw_duration_ms} ms.")
    if draw_duration_ms > 3000:
         print("WARNING: Drawing took a long time...")

    # === No display flip here ===


# --- Main Loop (REVISED Event Handling) ---
clock = pygame.time.Clock()
running = True
needs_redraw = True # Flag to draw initially

while running:
    time_delta = clock.tick(60) / 1000.0

    # --- Event Handling --- 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # === Pass event to the UI Manager FIRST ===
        ui_manager.process_events(event)

        # === Check for specific UI Events generated by the Manager ===

        # --- Handle Window Close Button (X) ---
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == settings_window:
                print("[Debug] Main Loop: Settings window close event detected.")
                print("Settings window closed via 'X'. Discarding changes.")
                settings_window.kill()
                settings_window = None

        # --- Handle Slider Movement (Update Label) ---
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            # Check if the slider is part of the settings window
            if settings_window and event.ui_element in settings_window.ui_elements.values():
                # Find the key associated with this slider
                slider_key = None
                for key, element in settings_window.ui_elements.items():
                    if element == event.ui_element:
                        slider_key = key
                        break
                
                if slider_key:
                    value = event.ui_element.get_current_value()
                    label_key = slider_key + "_label"
                    if label_key in settings_window.ui_elements:
                        is_float = isinstance(value, float)
                        value_text = f"{value:.{SLIDER_FLOAT_PRECISION}f}" if is_float else str(int(value))
                        settings_window.ui_elements[label_key].set_text(value_text)
                    # Note: We are NOT updating current_settings here, only the label
                    # The settings are read directly from UI elements when Apply is pressed

        # --- Handle Text Entry Changes (Iterations Warning) ---
        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
             if settings_window and event.ui_element == settings_window.ui_elements.get("iterations"):
                 try:
                     iter_val = int(event.text)
                     if iter_val > 10:
                         settings_window.iteration_warning_label.show()
                     else:
                         settings_window.iteration_warning_label.hide()
                 except ValueError:
                     settings_window.iteration_warning_label.hide()

        # --- Handle Button Presses ---
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # --- Settings Window Apply Button ---
            if settings_window and event.ui_element == settings_window.apply_button:
                print("[Debug] Main Loop: Settings window Apply button pressed (checked via ui_element).")
                # Read settings from UI elements *now*
                if settings_window.update_settings_from_ui():
                    current_settings = settings_window.get_applied_settings()
                    print("Settings applied from window Apply button.")
                    # Recalculate Start Pos based on Ratio
                    current_settings["start_pos"] = (
                        screen_width * current_settings.get("start_x_ratio", DEFAULT_SETTINGS["start_x_ratio"]),
                        screen_height * current_settings.get("start_y_ratio", DEFAULT_SETTINGS["start_y_ratio"])
                    )
                    settings_window.kill()
                    settings_window = None
                    needs_redraw = True
                else:
                    print("[Debug] Main Loop: Failed to apply settings due to errors reading UI values.")
                    # Optionally flash window or show error message

            # --- Main Settings Button ---
            elif event.ui_element == settings_button:
                if not settings_window:
                    settings_window = SettingsWindow(ui_manager, current_settings)
                    print("Settings button clicked - window opened")
                else:
                    print("Settings button clicked - window already open")
                    # Try to bring existing window to front
                    try:
                        settings_window.focus()
                        print("[Debug] Called settings_window.focus()")
                    except AttributeError:
                        print("[Debug] settings_window.focus() not available?")

            # --- Main Redraw Button ---
            elif event.ui_element == apply_button:
                print("Redraw button clicked")
                # Recalculate Start Pos based on Ratio
                current_settings["start_pos"] = (
                     screen_width * current_settings.get("start_x_ratio", DEFAULT_SETTINGS["start_x_ratio"]),
                     screen_height * current_settings.get("start_y_ratio", DEFAULT_SETTINGS["start_y_ratio"])
                 )
                needs_redraw = True

    # --- Update ---
    ui_manager.update(time_delta)

    # --- Drawing ---
    # === Redraw L-System onto its surface IF needed ===
    if needs_redraw:
        generate_and_draw(lsystem_surface, current_settings) # Pass lsystem_surface
        needs_redraw = False

    # === Blit the L-System surface to the main screen ===
    screen.blit(lsystem_surface, (0, 0))

    # === Draw UI on top ===
    ui_manager.draw_ui(screen)

    # === Flip display ===
    pygame.display.flip()

pygame.quit() 