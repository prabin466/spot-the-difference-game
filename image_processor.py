import cv2
import numpy as np


class ImageProcessor:
    """
    Handles image cloning, generation of random non-overlapping regions for differences, and 
    application of alterations to create the modified image.
    """

    def __init__(self, original_image):
        """
        Initializes the ImageProcessor with the original image.
        """
        self.original_image = original_image
        self.modified_image = None
        self.differences = None
        self.alterations = None


    def clone(self):  
        """
        Clones the original image and stores it in modified_image, so that the original source
        is never mutated.
        """
        self.modified_image = self.original_image.copy()  


    def generate_regions(self, count: int = 5) -> list[tuple]:
        """
        Generates random non-overlapping regions within the image bounds.
        Overlaps detection uses AABB intersection. Results are stored in self.differences for later use in applying alterations.

        Args:
            count (int): Number of non-overlapping regions to generate, default is 5.

        Returns:
            list[tuple]: A list of tuples, each containing (x, y, width, height) for the generated regions.
        """
        height, width, _ = self.original_image.shape 
        regions = []

        for _ in range(count):
            while True:  
                region_w = np.random.randint(30, 50)
                region_h = np.random.randint(30, 50)  
                x = np.random.randint(0, width - region_w)
                y = np.random.randint(0, height - region_h) 

                # AABB collision detection to ensure no overlap with existing regions
                overlaps = any(x < rx + rw and rx < x + region_w and 
                               y < ry + rh and ry < y + region_h 
                               for rx, ry, rw, rh in regions)
                
                if not overlaps:
                    regions.append((x, y, region_w, region_h))
                    break 


        self.differences = regions
        return regions