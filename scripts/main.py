import tkinter as tk
from tkinter import filedialog

import cv2

from game_state import GameState
from game_ui import GameUI
from image_processor import ImageProcessor


class SpotDifferenceApp:
    def __init__(self, root):
        self.root = root
        self.state = GameState(max_mistakes=3, click_tolerance=10)

        self.ui = GameUI(
            root,
            on_load_image=self.load_image,
            on_reveal=self.reveal_differences,
            on_image_click=self.handle_image_click,
        )

        self.refresh_labels()

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Choose an image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*"),
            ],
        )

        if not file_path:
            return

        original_image = cv2.imread(file_path)
        if original_image is None:
            self.ui.show_error("Image error", "Could not load this image.")
            return

        try:
            # use the image_processor.py part from the other group member
            processor = ImageProcessor(original_image)
            processor.clone()
            regions = processor.generate_regions(count=5)
            processor.apply_alterations()

            self.state.new_round(regions)
            self.ui.show_images(processor.original_image, processor.modified_image)
            self.ui.set_clicks_enabled(True)
            self.refresh_labels()

        except Exception as error:
            self.ui.show_error("Game error", str(error))

    def handle_image_click(self, image_x, image_y):
        result, region = self.state.check_click(image_x, image_y)

        if result == "hit" or result == "win":
            self.ui.draw_found(region)

        self.refresh_labels()

        if result == "win":
            self.ui.set_clicks_enabled(False)
            self.ui.show_win_popup()

        if result == "lose":
            self.ui.set_clicks_enabled(False)
            self.ui.show_loss_popup(self.state.found_count(), self.state.total_count())

    def reveal_differences(self):
        if self.state.total_count() == 0:
            self.ui.show_error("No image", "Please load an image first.")
            return

        hidden_regions = self.state.reveal_unfound()
        self.ui.draw_revealed(hidden_regions)
        self.ui.set_clicks_enabled(False)
        self.refresh_labels()
        self.ui.show_reveal_popup()

    def refresh_labels(self):
        self.ui.update_status(
            remaining=self.state.remaining_count(),
            mistakes=self.state.mistakes,
            max_mistakes=self.state.max_mistakes,
            score=self.state.total_score,
        )


def main():
    root = tk.Tk()
    SpotDifferenceApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
