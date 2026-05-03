import cv2
import numpy as np


class ImageProcessor:
    '''
    A class to process images and create differences between them.
    '''

    def __init__(self, original_image):  # Receives the original image, stores modifed image, differences and alterations as None
        self.original_image = original_image
        self.modified_image = None
        self.differences = None
        self.alterations = None




    def clone(self):  # Clones the original image and stores it in modified_image
        self.modified_image = self.original_image.copy()  



    def generate_regions(self):
        height, width, _ = self.original_image.shape  # Get the dimensions of the original image
        regions = []  # List to store the regions where differences will be created

        for i in range(5): # Generate 5 random regions for differences
            while True:  # Loop until a valid region is generated
                region_w = np.random.randint(30, 50)  # Random width for the region
                region_h = np.random.randint(30, 50)  # Random height for the region
                x = np.random.randint(0, width - region_w)  # Random x coordinate for the region
                y = np.random.randint(0, height - region_h)  # Random y coordinate for the region

                if not any(x < rx + rw and rx < x + region_w and y < ry + rh and ry < y + region_h for rx, ry, rw, rh in regions): # Check if the generated region overlaps with any existing regions
                    regions.append((x, y, region_w, region_h))  # If not, add it to the list of regions
                    break

        self.differences = regions  # Store the generated regions as differences
        return regions  # Return the list of generated regions