import pygame
import pygame_gui
import math # For rounding slider values

# Assuming settings module provides SLIDER_FLOAT_PRECISION and parse_rules
from settings import SLIDER_FLOAT_PRECISION, parse_rules

# Custom event for signaling settings applied
# SETTINGS_APPLIED_EVENT = pygame.USEREVENT + 1

class SettingsWindow(pygame_gui.elements.UIWindow):
    """UI Window for adjusting L-System parameters."""
    def __init__(self, manager, initial_settings):
        # Define reasonable default window size and position
        window_width = 550
        window_height = 580 # Increased height slightly for apply button
        super().__init__(pygame.Rect(150, 50, window_width, window_height), # Position and size
                         manager=manager,
                         window_display_title="L-System Settings")

        self.settings = initial_settings.copy() # Work on a copy
        self.ui_elements = {} # Store UI elements (entries, sliders, labels)
        self.apply_button = None # Reference to the apply button
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

        # Add a warning label for high iterations
        self.iteration_warning_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(margin, current_y, window_width - 2 * margin, input_height),
            text="Warning: High iterations can be slow!",
            manager=manager,
            container=self,
            visible=False # Initially hidden
        )
        self.ui_elements['iteration_warning'] = self.iteration_warning_label
        current_y += row_height

        # --- Add Apply Button ---
        button_width = 100
        button_height = 35
        apply_button_x = window_width - button_width - margin
        self.apply_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(apply_button_x, current_y, button_width, button_height),
            text='Apply',
            manager=manager,
            container=self
        )

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
                        try:
                            new_settings["rules"] = parse_rules(new_val_str)
                        except ValueError as e:
                            print(f"Error parsing rules: {e}") # Handle potential parse errors
                            # Optionally provide user feedback here (e.g., change border color)
            elif isinstance(element, tuple): # Slider, ValueLabel, is_float
                slider, value_label, is_float = element
                new_val_float = slider.get_current_value()
                # Round floats to precision for comparison and storage
                if is_float:
                    new_val = round(new_val_float, SLIDER_FLOAT_PRECISION)
                    # Use a tolerance for float comparison
                    current_float = float(current_value) if current_value is not None else 0.0
                    if abs(current_float - new_val) > 10**-(SLIDER_FLOAT_PRECISION + 1):
                         new_settings[key] = new_val
                         value_label.set_text(f"{new_val:.{SLIDER_FLOAT_PRECISION}f}")
                         changed = True
                else:
                    new_val = int(new_val_float)
                    current_int = int(current_value) if current_value is not None else 0
                    if current_int != new_val:
                        new_settings[key] = new_val
                        value_label.set_text(str(new_val))
                        changed = True
                        if key == 'iterations': # Show/hide warning for high iterations
                           if new_val > 7:
                               self.iteration_warning_label.show()
                           else:
                               self.iteration_warning_label.hide()

        if changed:
            self.settings = new_settings
            self.has_changes = True
            # print("Settings updated from UI, has_changes=True") # Debugging

        return changed

    def get_applied_settings(self):
        """Return the last settings that were explicitly applied."""
        # Ensure rules are parsed based on the applied rules_string
        # This is important if rules_string was edited but not applied before closing
        try:
            self.applied_settings["rules"] = parse_rules(self.applied_settings["rules_string"])
        except ValueError as e:
            print(f"Error parsing applied rules string: {e}")
            # Keep the old rules if parsing fails

        return self.applied_settings

    def apply_changes(self):
        """Mark the current settings as applied."""
        # Ensure current settings (from UI) are captured before applying
        self.update_settings_from_ui()
        # Parse rules from the potentially updated rules_string before applying
        try:
             self.settings["rules"] = parse_rules(self.settings["rules_string"])
        except ValueError as e:
             print(f"Error parsing rules before applying: {e}")
             # Decide how to handle invalid rules - maybe prevent apply?
             # For now, we proceed but the rules might be invalid/old

        self.applied_settings = self.settings.copy()
        self.has_changes = False
        print("Changes applied. has_changes=False") # Debugging

    def process_event(self, event):
        """Handle events relevant to the settings window, like slider changes or Apply button."""
        # Update internal settings immediately when UI changes
        # This allows slider value labels to update in real-time
        settings_changed = False
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            settings_changed = self.update_settings_from_ui()
        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
             settings_changed = self.update_settings_from_ui()

        # Handle Apply button press
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.apply_button:
            print("Apply button pressed inside SettingsWindow")
            self.apply_changes() # Mark changes as applied internally

        # Let the UIWindow handle its own events too (like dragging, closing)
        super().process_event(event)

        # return settings_changed # Return value might be useful elsewhere

    # Override kill method to handle applying changes on close if desired
    def kill(self):
        # Example: Automatically apply changes when the window is closed via 'X'
        # if self.has_changes:
        #     print("Applying settings on close")
        #     self.apply_changes()
        # Add logic here if you want to prompt user (Requires more UI elements)
        super().kill() 