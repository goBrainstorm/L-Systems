# L-System Plant Visualizer

This project visualizes plant-like structures generated using L-Systems (Lindenmayer systems).

## Features

*   Generates L-System strings based on an axiom, rules, and number of iterations.
*   Visualizes the generated string using a simple turtle graphics implementation with Pygame.
*   Supports basic L-System commands: F (draw forward), + (turn right), - (turn left), [ (push state), ] (pop state).

## Requirements

*   Python 3.x
*   Pygame

## Installation

1.  Clone the repository (or download the files).
2.  Install the required library:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Configure the L-System parameters (axiom, rules, angle, iterations) in `l_system_visualizer.py`.
2.  Run the script:
    ```bash
    python l_system_visualizer.py
    ```

A Pygame window will open displaying the generated L-System plant.

## Customization

*   Modify the `axiom`, `rules`, `angle_deg`, and `iterations` variables in the `if __name__ == "__main__":` block to generate different structures.
*   Adjust screen dimensions, colors, line thickness, and draw length in the configuration section.
*   Extend the `LSystem` and `Turtle` classes or the `draw_lsystem` function to support more complex L-System commands or drawing features. 