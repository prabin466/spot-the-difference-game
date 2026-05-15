# 🔍 Spot the Difference — HIT137 Group Assignment 3

A desktop "Spot the Difference" game built with Python, Tkinter, and OpenCV.  
**Subject:** HIT137 | **Semester:** S1 2026 | **Worth:** 30%

---

## 👥 Group Members & Contributions

| Member | File | Responsibility |
|--------|------|---------------|
| 1 | `image_processor.py` | Image cloning, region generation, alteration effects |
| 2 | `game_ui.py` (display) | Tkinter window, canvases, image display, status labels |
| 3 | `game_ui.py` (interaction) + `game_state.py` + `main.py` | Click detection, game logic, integration |

---

## 📋 Overview

Two nearly identical images are displayed side by side. One is the original; the other contains **5 hidden programmatic differences**. The player clicks on the modified image to locate all differences before making 3 mistakes.

---

## 🗂️ Project Structure

```
spot_the_difference/
├── image_processor.py   # Image loading, cloning, and alteration (Person 1)
├── game_state.py        # Game logic — clicks, scoring, win/loss (Person 3)
├── game_ui.py           # Tkinter GUI — display + interaction (Person 2 & 3)
├── main.py              # Entry point — wires everything together (Person 3)
├── github_link.txt      # GitHub repository URL
└── README.md            # This file
```

---

## ⚙️ Requirements

- Python 3.9+
- opencv-python
- Pillow
- numpy
- tkinter *(built into Python)*

Install dependencies:

```bash
pip3 install opencv-python pillow numpy
```

---

## ▶️ How to Run

```bash
python3 main.py
```

---

## 🎮 How to Play

1. Click **📂 Load Image** to choose any JPG, PNG, or BMP image
2. The left panel shows the **original** image (reference only)
3. The right panel shows the **modified** image — click here to find differences
4. A **red circle** appears on both images when a difference is correctly found
5. You are allowed a maximum of **3 mistakes** per round
6. Click **👁 Reveal All** at any time to reveal unfound differences in blue
7. Load a new image to play again

---

## 🧠 OOP Design

### `ImageProcessor` — `image_processor.py`
- Loads and clones the original image
- Generates 5 random non-overlapping difference regions
- Applies one of 5 alteration types per region:
  - Hue shift
  - Saturation shift
  - Brightness shift
  - Gaussian blur
  - Random noise
- Main method: `create_difference_images()` → returns `(original, modified, regions)`

### `DifferenceRegion` — `game_state.py`
- Represents a single hidden difference region
- Tracks whether the region has been found
- Provides `is_clicked()` with proximity tolerance

### `GameState` — `game_state.py`
- Manages rounds, mistakes, score, and win/loss conditions
- `new_round(regions)` — starts a fresh round
- `check_click(x, y)` → returns `"hit"`, `"miss"`, `"win"`, or `"lose"`
- `reveal_unfound()` — marks all remaining regions as found

### `GameUI` — `game_ui.py`
- Builds the full Tkinter window with dark navy theme
- Side-by-side canvases with image scaling and offset tracking
- Coordinate conversion from canvas pixels → original image coordinates
- Draws red (found) and blue (revealed) circles on both canvases
- Custom styled popup dialogs for win, loss, and reveal events

### `SpotDifferenceApp` — `main.py`
- Top-level controller connecting all components
- Handles image loading via file dialog
- Passes callbacks into `GameUI` and delegates results to `GameState`

---



