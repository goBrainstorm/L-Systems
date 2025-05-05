# Entry point for the L-System Visualizer application

import pygame
import pygame_gui
import sys
import copy # For deep copying settings
import math

# Import core components
from settings import DEFAULT_SETTINGS, DRAWING_PADDING, parse_rules
from l_system import LSystem
from turtle import Turtle
from renderer import Renderer
from gui import SettingsWindow

# --- Application Class (Optional but Recommended) ---
# Using a class can help organize state
class App:
    def __init__(self):
        pygame.init()

        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("L-System Visualizer")

        self.ui_manager = pygame_gui.UIManager((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()

        # --- Initialize Settings ---
        self.current_settings = copy.deepcopy(DEFAULT_SETTINGS)
        # Ensure rules are parsed if not already done in settings.py
        if "rules" not in self.current_settings:
             self.current_settings["rules"] = parse_rules(self.current_settings.get("rules_string", ""))

        # --- Create Core Components ---
        # Initial start position (centered at bottom) - can be adjusted
        start_x = self.screen_width / 2
        start_y = self.screen_height # Start at the bottom edge
        # LSystem doesn't need screen size, just axiom/rules
        self.lsystem = LSystem(self.current_settings["axiom"], self.current_settings["rules"])
        # Turtle starts at a logical position (e.g., 0,0) relative to its own coordinate system
        # The Renderer will handle placing it on screen
        self.turtle = Turtle(x=0, y=0, angle_deg=self.current_settings["start_angle_deg"])
        self.renderer = Renderer(self.screen_width, self.screen_height, DRAWING_PADDING)

        # --- Create UI Elements ---
        self.settings_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 10), (100, 30)),
            text='Settings',
            manager=self.ui_manager
        )
        self.redraw_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((120, 10), (100, 30)),
            text='Redraw',
            manager=self.ui_manager
        )
        self.settings_window = None # Initially closed

        # --- Drawing Surface & State ---
        self.lsystem_surface = pygame.Surface((self.screen_width, self.screen_height))
        self.redraw_needed = True # Trigger initial draw
        self.last_drawing_commands = []
        self.last_bounds = (0, 0, 1, 1) # Default bounds

    def _generate_and_prepare_draw(self):
        """Generates L-System string, interprets it, and stores results."""
        print("Generating L-System...")
        # Update LSystem object with current axiom/rules before generating
        self.lsystem.axiom = self.current_settings["axiom"]
        self.lsystem.rules = self.current_settings["rules"]
        lsystem_string = self.lsystem.generate(self.current_settings["iterations"])

        print(f"Generated string (length {len(lsystem_string)}): {lsystem_string[:100]}...")

        # Update Turtle's start angle before interpreting
        self.turtle.start_angle_rad = math.radians(self.current_settings["start_angle_deg"])

        # Interpret the string to get drawing commands and bounds
        self.last_drawing_commands, self.last_bounds = self.turtle.interpret(
            lsystem_string,
            self.current_settings["angle_deg"],
            self.current_settings["length"],
            self.current_settings["angle_variation_deg"],
            self.current_settings["length_variation_factor"]
        )
        print(f"Calculated Bounds: {self.last_bounds}")
        self.redraw_needed = True # Mark that the surface needs redrawing

    def _draw_lsystem(self):
        """Renders the prepared L-system data onto the dedicated surface."""
        if not self.last_drawing_commands:
             print("No drawing commands available.")
             self.lsystem_surface.fill(self.current_settings["background_color"])
             return

        print("Drawing L-System...")
        self.renderer.draw(
            self.lsystem_surface,
            self.last_drawing_commands,
            self.last_bounds,
            self.current_settings["line_color"],
            self.current_settings["line_thickness"],
            self.current_settings["background_color"]
        )

    def run(self):
        """Main application loop."""
        is_running = True

        while is_running:
            time_delta = self.clock.tick(60) / 1000.0

            # --- Initial Generation/Draw --- 
            if self.redraw_needed:
                 # Only regenerate the string IF settings affecting generation changed
                 # For now, regenerate if redraw is needed (simplest)
                 self._generate_and_prepare_draw()
                 self._draw_lsystem()
                 self.redraw_needed = False # Reset flag

            # --- Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False

                # Handle GUI events
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.settings_button:
                        if self.settings_window is None or not self.settings_window.alive():
                             # Pass current settings to the window
                             self.settings_window = SettingsWindow(self.ui_manager, self.current_settings)
                        else:
                             self.settings_window.show()

                    elif event.ui_element == self.redraw_button:
                         print("Redraw button pressed.")
                         # Force regeneration and redraw with current settings
                         self.redraw_needed = True

                # Handle settings window closing
                if event.type == pygame_gui.UI_WINDOW_CLOSE:
                     if event.ui_element == self.settings_window:
                         print("Settings window closed.")
                         # Check if settings changed and apply them
                         if self.settings_window and self.settings_window.has_changes:
                              print("Applying settings from closed window...")
                              self.current_settings = self.settings_window.get_applied_settings()
                              # Important: Re-parse rules string if it changed!
                              self.current_settings["rules"] = parse_rules(self.current_settings["rules_string"])
                              self.settings_window.apply_changes() # Reset has_changes flag in window
                              self.redraw_needed = True # Trigger redraw with new settings
                         self.settings_window = None # Ensure it can be reopened

                # Pass events to the UI manager and potentially the settings window
                self.ui_manager.process_events(event)
                if self.settings_window and self.settings_window.alive():
                    self.settings_window.process_event(event)

            # --- GUI Updates ---
            self.ui_manager.update(time_delta)

            # --- Drawing ---
            self.screen.blit(self.lsystem_surface, (0, 0))
            self.ui_manager.draw_ui(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

# --- Main Execution --- 
if __name__ == '__main__':
    app = App()
    app.run() 