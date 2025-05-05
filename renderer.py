import pygame
import math

class Renderer:
    """Handles rendering the L-system drawing commands onto a Pygame surface."""

    def __init__(self, screen_width, screen_height, padding):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.padding = padding

    def _calculate_scale_offset(self, bounds):
        """Calculate scale factor and offset to fit bounds within the screen + padding."""
        min_x, min_y, max_x, max_y = bounds
        lsystem_width = max_x - min_x
        lsystem_height = max_y - min_y

        # Available drawing area
        draw_area_width = self.screen_width - 2 * self.padding
        draw_area_height = self.screen_height - 2 * self.padding

        # Calculate scale factor (fit both width and height)
        scale_x = draw_area_width / lsystem_width if lsystem_width > 0 else 1
        scale_y = draw_area_height / lsystem_height if lsystem_height > 0 else 1
        scale_factor = min(scale_x, scale_y)

        # Calculate offset to center the drawing
        scaled_width = lsystem_width * scale_factor
        scaled_height = lsystem_height * scale_factor

        offset_x = self.padding + (draw_area_width - scaled_width) / 2 - (min_x * scale_factor)
        offset_y = self.padding + (draw_area_height - scaled_height) / 2 - (min_y * scale_factor)

        return scale_factor, (offset_x, offset_y)

    def draw(self, surface, drawing_commands, bounds, line_color, line_thickness, background_color):
        """Draws the L-system onto the provided surface."""
        surface.fill(background_color)

        if not drawing_commands:
            return # Nothing to draw

        scale_factor, offset = self._calculate_scale_offset(bounds)

        for start_pos, end_pos in drawing_commands:
            # Apply scaling and offset
            screen_start_x = start_pos[0] * scale_factor + offset[0]
            screen_start_y = start_pos[1] * scale_factor + offset[1]
            screen_end_x = end_pos[0] * scale_factor + offset[0]
            screen_end_y = end_pos[1] * scale_factor + offset[1]

            # Draw the line
            pygame.draw.line(surface, line_color,
                             (int(screen_start_x), int(screen_start_y)),
                             (int(screen_end_x), int(screen_end_y)), line_thickness) 