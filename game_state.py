class DifferenceRegion:
    def __init__(self, region):
        self.x = int(region[0])
        self.y = int(region[1])
        self.width = int(region[2])
        self.height = int(region[3])
        self.found = False

    def center(self):
        return self.x + self.width // 2, self.y + self.height // 2

    def radius(self):
        return max(self.width, self.height) // 2 + 8

    def is_clicked(self, click_x, click_y, tolerance):
        # give the player a bit of extra space around the region
        left = self.x - tolerance
        right = self.x + self.width + tolerance
        top = self.y - tolerance
        bottom = self.y + self.height + tolerance

        return left <= click_x <= right and top <= click_y <= bottom


class GameState:
    def __init__(self, max_mistakes=3, click_tolerance=10):
        self.max_mistakes = max_mistakes
        self.click_tolerance = click_tolerance
        self.regions = []
        self.mistakes = 0
        self.total_score = 0
        self.game_over = True

    def new_round(self, regions):
        self.regions = [DifferenceRegion(region) for region in regions]
        self.mistakes = 0
        self.game_over = False

    def check_click(self, click_x, click_y):
        if self.game_over:
            return "finished", None

        for region in self.regions:
            if not region.found and region.is_clicked(click_x, click_y, self.click_tolerance):
                region.found = True
                self.total_score += 1

                if self.remaining_count() == 0:
                    self.game_over = True
                    return "win", region

                return "hit", region

        self.mistakes += 1

        if self.mistakes >= self.max_mistakes:
            self.game_over = True
            return "lose", None

        return "miss", None

    def reveal_unfound(self):
        hidden_regions = []

        for region in self.regions:
            if not region.found:
                region.found = True
                hidden_regions.append(region)

        self.game_over = True
        return hidden_regions

    def found_count(self):
        count = 0
        for region in self.regions:
            if region.found:
                count += 1
        return count

    def remaining_count(self):
        return len(self.regions) - self.found_count()

    def total_count(self):
        return len(self.regions)
