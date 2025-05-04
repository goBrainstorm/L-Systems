# L-System Plant Visualizer

This project visualizes plant-like structures generated using L-Systems (Lindenmayer systems) with Pygame and Pygame GUI.

## Features

*   Generates L-System strings based on an axiom, rules, and number of iterations.
*   Visualizes the generated string using Pygame.
*   Interactive GUI (`pygame_gui`) for adjusting settings:
    *   Axiom, Rules, Iterations (Text Input)
    *   Angle, Start Angle, Length, Line Thickness, Angle Variation, Length Variation (Sliders)
    *   Real-time value display for sliders.
    *   Settings window Apply/Close ('X') functionality.
    *   Warning for high iteration counts.
*   Supports basic L-System commands: F (draw forward), + (turn right), - (turn left), [ (push state), ] (pop state).
*   **Randomization:** Adds slight random variations to angle and length during drawing for more organic looks.
*   **Auto-Scaling:** Automatically calculates drawing bounds and scales/centers the L-system to fit the window.
*   **Redraw Button:** Manually trigger a redraw with current settings (useful for seeing randomization effects).

## Requirements

*   Python 3.x
*   Pygame
*   Pygame GUI

## Installation

1.  Clone the repository (or download the files).
2.  Create and activate a virtual environment (recommended):
    ```bash
    python -m venv .venv
    # On Windows (cmd/powershell)
    .\.venv\Scripts\activate
    # On Linux/macOS (bash/zsh)
    source .venv/bin/activate
    ```
3.  Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Run the script (ensure your virtual environment is active):
    ```bash
    # On Windows
    .\.venv\Scripts\python.exe l_system_visualizer.py
    # On Linux/macOS
    python l_system_visualizer.py
    ```
2.  A Pygame window will open displaying the initial L-System plant.
3.  Click the **"Settings"** button to open the configuration window.
4.  Adjust parameters using the text fields and sliders.
5.  Click **"Apply"** in the settings window to see changes.
6.  Click the main **"Redraw"** button to regenerate the plant with the *current* settings (useful after changing randomization or just to see a new random variation).

## Customization

*   Modify the `DEFAULT_SETTINGS` dictionary in `l_system_visualizer.py` for different initial plant configurations.
*   Experiment with different L-System `axiom` and `rules` strings in the Settings UI.
*   Adjust the `SLIDER_FLOAT_PRECISION` and slider ranges in the `SettingsWindow` class.
*   Change colors (`line_color`, `background_color`) in `DEFAULT_SETTINGS`.
*   Modify `DRAWING_PADDING` to control the margin around the auto-scaled drawing.

*   Extend the `LSystem` and `Turtle`

## TODO / Future Enhancements

*   [ ] **Memory System:** Implement saving/loading plant configurations (axiom, rules, settings) to/from JSON files.
*   [ ] **Random Plant Generation:** Add functionality to generate random L-system rules or select from presets.
*   [ ] **Leaves & Pollen:** Integrate drawing routines for leaves and pollen particles at specific points in the L-system.
*   [ ] **Branch Variation:** Allow branch thickness and color to vary based on recursion depth or other factors.
*   [ ] **Zoom Functionality:** Implement zoom in/out controls for the visualization.
*   [ ] **Animations:** Animate the growth of the L-system step-by-step.
*   [ ] **(Later) 3D Rendering:** Explore migrating the visualization to a 3D library (e.g., PyOpenGL, Ursina).
*   [ ] **(Later) Textures:** Add textures to branches and leaves (especially relevant for 3D).