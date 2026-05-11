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
        Generates random non-overlapping (x, y, width, height) regions for differences.
        Overlaps detection uses AABB intersection. Results are stored in self.differences for later use in applying alterations.
        """
        height, width, _ = self.original_image.shape 
        regions = []

        for _ in range(count):
            while True:  
                region_w = np.random.randint(30, 50)
                region_h = np.random.randint(30, 50)  
                x = np.random.randint(0, width - region_w)
                y = np.random.randint(0, height - region_h) 

                # Reject regions that overlap with existing ones
                overlaps = any(x < rx + rw and rx < x + region_w and 
                               y < ry + rh and ry < y + region_h 
                               for rx, ry, rw, rh in regions)
                
                if not overlaps:
                    regions.append((x, y, region_w, region_h))
                    break 


        self.differences = regions
        return regions
    

    @staticmethod
    def _shift_hsv_channel(patch, channel, min_shift, max_shift, wrap = None):
        """
        Shifts a specific HSV channel by a random amount.
        If wrap is provided as a value (e.g. 255), the result is clipped to [0, wrap]. 
        If wrap is None, the channel wraps around at 180 (used for hue).

        """
        hsv = cv2.cvtColor(patch, cv2.COLOR_BGR2HSV)
        direction = np.random.choice([-1, 1])
        shift = np.random.randint(min_shift, max_shift)
        if wrap:
            # Clipping is used to prevent overflow
             hsv[:, :, channel] = np.clip(hsv[:, :, channel].astype(int) + direction * shift, 0, wrap)
        else:
            # Hue is circular thatswhy it needs to be wrap around at 180
            hsv[:, :, channel] = (hsv[:, :, channel].astype(int) + direction * shift) % 180 
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    

    @staticmethod
    def _apply_hue_shift(patch):
        return ImageProcessor._shift_hsv_channel(patch, channel=0, min_shift=20, max_shift=40)
    
    @staticmethod
    def _apply_saturation_shift(patch):
        return ImageProcessor._shift_hsv_channel(patch, channel=1, min_shift=30, max_shift=60, wrap=255)
    
    @staticmethod
    def _apply_brightness_shift(patch):
        return ImageProcessor._shift_hsv_channel(patch, channel=2, min_shift=30, max_shift=60, wrap=255)


    @staticmethod
    def _apply_blur(patch):
        """
        Applies a Gaussian blur with a randomly chosen kernel size.
        Returns the blurred patch.
        """
        ksize = np.random.choice([5, 7, 9])  
        return cv2.GaussianBlur(patch, (ksize, ksize), 0)
    
    @staticmethod
    def _apply_noise(patch):
        """
        Adds random Gaussian noise to the patch.
        Returns the noisy patch.
        """
        mean = 0
        stddev = np.random.randint(10, 30)  
        noise = np.random.normal(mean, stddev, patch.shape)
        # Np.normal returns float64
        noisy_patch = patch.astype(np.float64) + noise
        return np.clip(noisy_patch, 0, 255).astype(np.uint8)