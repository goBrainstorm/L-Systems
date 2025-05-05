# Entry point for the L-System Visualizer application

import pygame
import pygame_gui
import sys
import copy # For deep copying settings
import math
import time # Import the time module

# Import core components
from settings import DEFAULT_SETTINGS, DRAWING_PADDING, parse_rules
from l_system import LSystem
from drawing_turtle import Turtle
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
        self.generation_time_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 50), (210, 30)), # Position below buttons
            text='Gen time: N/A',
            manager=self.ui_manager
        )
        self.drawing_time_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 80), (210, 30)), # Position below gen time
            text='Draw time: N/A',
            manager=self.ui_manager
        )
        self.total_time_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 110), (210, 30)), # Position below draw time
            text='Total time: N/A',
            manager=self.ui_manager
        )
        self.settings_window = None # Initially closed

        # --- Drawing Surface & State ---
        self.lsystem_surface = pygame.Surface((self.screen_width, self.screen_height))
        self.redraw_needed = True # Trigger initial draw
        self.last_drawing_commands = []
        self.last_bounds = (0, 0, 1, 1) # Default bounds
        self.last_generation_time = None # Store generation duration
        self.last_drawing_time = None # Store drawing duration

    def _generate_and_prepare_draw(self):
        """Generates L-System string, interprets it, and stores results."""
        print("Generating L-System...")
        # Update LSystem object with current axiom/rules before generating
        self.lsystem.axiom = self.current_settings["axiom"]
        self.lsystem.rules = self.current_settings["rules"]

        # --- Time the generation ---
        start_gen_time = time.time()
        lsystem_string = self.lsystem.generate(self.current_settings["iterations"])
        end_gen_time = time.time()
        self.last_generation_time = end_gen_time - start_gen_time
        # -------------------------

        print(f"Generated string (length {len(lsystem_string)}): {lsystem_string[:100]}...")
        print(f"Generation took: {self.last_generation_time:.4f} seconds")

        # Update the timer label
        self.generation_time_label.set_text(f"Gen time: {self.last_generation_time:.3f}s")

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
             # Reset time labels if nothing is drawn
             self.drawing_time_label.set_text('Draw time: N/A')
             if self.last_generation_time is not None:
                 self.total_time_label.set_text(f"Total time: {self.last_generation_time:.3f}s")
             else:
                 self.total_time_label.set_text('Total time: N/A')
             return

        print("Drawing L-System...")

        # --- Time the drawing ---
        start_draw_time = time.time()
        self.renderer.draw(
            self.lsystem_surface,
            self.last_drawing_commands,
            self.last_bounds,
            self.current_settings["line_color"],
            self.current_settings["line_thickness"],
            self.current_settings["background_color"]
        )
        end_draw_time = time.time()
        self.last_drawing_time = end_draw_time - start_draw_time
        # -----------------------

        print(f"Drawing took: {self.last_drawing_time:.4f} seconds")

        # Update time labels
        self.drawing_time_label.set_text(f"Draw time: {self.last_drawing_time:.3f}s")

        total_time = (self.last_generation_time or 0) + (self.last_drawing_time or 0)
        self.total_time_label.set_text(f"Total time: {total_time:.3f}s")

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
                    continue # Exit loop immediately if quitting

                # Pass all other events to the UI manager for processing.
                # The manager will generate UI_BUTTON_PRESSED, UI_WINDOW_CLOSE, etc.
                self.ui_manager.process_events(event)

                # Now check for events generated/handled by the manager
                if event.type == pygame_gui.UI_WINDOW_CLOSE:
                     # Check if the closed window was our settings window
                     if self.settings_window and event.ui_element == self.settings_window:
                         print("Settings window closed by user.")
                         self.settings_window = None # Clear our reference

                elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                    # Check which button was pressed
                    if event.ui_element == self.settings_button:
                        if self.settings_window is None or not self.settings_window.alive():
                             print("Settings button pressed - opening window.")
                             self.settings_window = SettingsWindow(self.ui_manager, self.current_settings)
                        else:
                             print("Settings button pressed - showing existing window.")
                             self.settings_window.show()
                    elif event.ui_element == self.redraw_button:
                         print("Redraw button pressed.")
                         self.redraw_needed = True
                    # Check if the Apply button inside the settings window was pressed
                    elif self.settings_window and self.settings_window.alive() and \
                         event.ui_element == self.settings_window.apply_button:
                         print("Apply button event caught in main loop.")
                         # Get the settings that were marked as 'applied' within the window
                         self.current_settings = self.settings_window.get_applied_settings()
                         self.redraw_needed = True
                         print("Main app settings updated from window, redraw triggered.")

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