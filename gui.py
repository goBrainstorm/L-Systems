import pygame
import pygame_gui
import math # For rounding slider values

# Assuming settings module provides SLIDER_FLOAT_PRECISION and parse_rules
from settings import SLIDER_FLOAT_PRECISION, parse_rules

class SettingsWindow(pygame_gui.elements.UIWindow):
    """UI Window for adjusting L-System parameters."""
    def __init__(self, manager, initial_settings):
        # Define reasonable default window size and position
        window_width = 550
        window_height = 550 # Increased height to fit all elements
        super().__init__(pygame.Rect(150, 50, window_width, window_height), # Position and size
                         manager=manager,
                         window_display_title="L-System Settings")

        self.settings = initial_settings.copy() # Work on a copy
        self.ui_elements = {} # Store UI elements (entries, sliders, labels)
        self.applied_settings = initial_settings.copy()
        self.has_changes = False # Track if settings changed since last apply

        # Layout variables
        current_y = 10
        label_width = 150
        entry_width = 350
        slider_width = 250
        value_label_width = 80
        row_height = 40
        input_height = 30
        margin = 10
        slider_x = margin + label_width + margin
        value_label_x = slider_x + slider_width + margin

        # --- Helper to create label and text entry row ---
        def create_text_entry_row(key, label_text):
            nonlocal current_y
            pygame_gui.elements.UILabel(relative_rect=pygame.Rect(margin, current_y, label_width, input_height),
                                        text=label_text,
                                        manager=manager,
                                        container=self)
            entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(slider_x, current_y, entry_width, input_height),
                                                         manager=manager,
                                                         container=self)
            entry.set_text(str(self.settings.get(key, "")))
            self.ui_elements[key] = entry
            current_y += row_height
            return entry

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
            slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect(slider_x, current_y, slider_width, input_height),
                                                             start_value=float(start_value),
                                                             value_range=value_range,
                                                             manager=manager,
                                                             container=self)
            # Value Label
            value_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(value_label_x, current_y, value_label_width, input_height),
                                                      text=f"{start_value:.{SLIDER_FLOAT_PRECISION}f}" if is_float else str(int(start_value)),
                                                      manager=manager,
                                                      container=self)
            self.ui_elements[key] = (slider, value_label, is_float)
            current_y += row_height
            return slider # Return the slider element

        # --- Create UI Elements ---
        create_text_entry_row("axiom", "Axiom:")
        create_text_entry_row("rules_string", "Rules:")
        create_slider_row("iterations", "Iterations:", (1, 10), is_float=False) # Iterations Slider

        create_slider_row("angle_deg", "Angle (°):", (0.0, 90.0))
        create_slider_row("start_angle_deg", "Start Angle (°):", (0.0, 360.0))
        create_slider_row("length", "Length:", (1.0, 50.0))
        create_slider_row("line_thickness", "Thickness:", (1, 10), is_float=False)
        create_slider_row("angle_variation_deg", "Angle Variation (°):", (0.0, 15.0))
        create_slider_row("length_variation_factor", "Length Variation (%):", (0.0, 0.5)) # Factor

        # --- Apply/Close Buttons (using standard window buttons) ---
        # We will handle apply logic based on changes and window close event

        # Add a warning label for high iterations
        self.iteration_warning_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(margin, current_y, window_width - 2 * margin, input_height),
            text="Warning: High iterations can be slow!",
            manager=manager,
            container=self,
            visible=False # Initially hidden
        )
        self.ui_elements['iteration_warning'] = self.iteration_warning_label

    def update_ui_from_settings(self):
        """Updates the UI elements to reflect the current internal settings."""
        for key, element in self.ui_elements.items():
            if key == 'iteration_warning': continue # Skip warning label

            value = self.settings.get(key)
            if isinstance(element, pygame_gui.elements.UITextEntryLine):
                element.set_text(str(value) if value is not None else "")
            elif isinstance(element, tuple): # Slider, ValueLabel, is_float
                slider, value_label, is_float = element
                if value is not None:
                    slider.set_current_value(float(value))
                    value_label.set_text(f"{value:.{SLIDER_FLOAT_PRECISION}f}" if is_float else str(int(value)))
                    if key == 'iterations': # Show warning for high iterations
                        self.iteration_warning_label.set_visible(int(value) > 7)

    def update_settings_from_ui(self):
        """Updates internal settings based on the current state of UI elements.
           Returns True if any setting was actually changed, False otherwise.
        """
        changed = False
        new_settings = self.settings.copy()

        for key, element in self.ui_elements.items():
            if key == 'iteration_warning': continue # Skip warning label
            current_value = self.settings.get(key)

            if isinstance(element, pygame_gui.elements.UITextEntryLine):
                new_val_str = element.get_text()
                if str(current_value) != new_val_str:
                    new_settings[key] = new_val_str
                    changed = True
                    if key == "rules_string": # Auto-parse rules when string changes
                        new_settings["rules"] = parse_rules(new_val_str)
            elif isinstance(element, tuple): # Slider, ValueLabel, is_float
                slider, value_label, is_float = element
                new_val_float = slider.get_current_value()
                # Round floats to precision for comparison and storage
                if is_float:
                    new_val = round(new_val_float, SLIDER_FLOAT_PRECISION)
                    if abs(float(current_value) - new_val) > 1e-9: # Compare floats carefully
                         new_settings[key] = new_val
                         value_label.set_text(f"{new_val:.{SLIDER_FLOAT_PRECISION}f}")
                         changed = True
                else:
                    new_val = int(new_val_float)
                    if int(current_value) != new_val:
                        new_settings[key] = new_val
                        value_label.set_text(str(new_val))
                        changed = True
                        if key == 'iterations': # Show warning for high iterations
                           self.iteration_warning_label.set_visible(new_val > 7)

        if changed:
            self.settings = new_settings
            self.has_changes = True

        return changed

    def get_applied_settings(self):
        """Return the last settings that were explicitly applied."""
        return self.applied_settings

    def apply_changes(self):
        """Mark the current settings as applied."""
        self.applied_settings = self.settings.copy()
        self.has_changes = False

    def process_event(self, event):
        """Handle events relevant to the settings window, like slider changes."""
        # Update internal settings immediately when UI changes
        # This allows slider value labels to update in real-time
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            self.update_settings_from_ui()
        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
             self.update_settings_from_ui()
        # Add handling for Apply button if it were inside the window
        # Or handle apply on window close

    # Override kill method to handle applying changes on close if desired
    def kill(self):
        # Example: Automatically apply changes when the window is closed via 'X'
        # if self.has_changes:
        #     print("Applying settings on close")
        #     self.apply_changes()
        # Add logic here if you want to prompt user (Requires more UI elements)
        super().kill() 