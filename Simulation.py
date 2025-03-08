import pygame
import json

pygame.init()

screen_width = 1300
screen_height = 850
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Traffic Simulation\U0001F6A6")

image = pygame.image.load("Images/Grid.jpg")  
image = pygame.transform.scale(image, (screen_width, screen_height))

class Traffic:
    def __init__(self):
        try:
            with open("traffic_timings.json", "r") as f:
                timings = json.load(f)
                self.green_duration = timings["green_duration"]
                self.red_duration = timings["red_duration"]
        except:
            self.green_duration = 35
            self.red_duration = 40

        self.yellow_duration = 5
        self.state = "NS_green"
        self.timer_value = self.green_duration
        self.font = pygame.font.Font(None, 36)

        self.red = pygame.image.load("Images/Red.jpg")
        self.green = pygame.image.load("Images/Green.jpg")
        self.yellow = pygame.image.load("Images/Yellow.jpg")

        self.lights = {
            "N": (625, 200),  # North
            "S": (625, 500),  # South
            "E": (750, 350),  # East
            "W": (500, 350)   # West
        }

    def update_state(self, dt):
        self.timer_value -= dt / 1000.0

        if self.timer_value <= 0:
            if self.state == "NS_green":
                self.state = "NS_yellow"
                self.timer_value = self.yellow_duration
            elif self.state == "NS_yellow":
                self.state = "EW_green"
                self.timer_value = self.red_duration  # EW turns green
            elif self.state == "EW_green":
                self.state = "EW_yellow"
                self.timer_value = self.yellow_duration
            elif self.state == "EW_yellow":
                self.state = "NS_green"
                self.timer_value = self.green_duration  # NS turns green

    def draw_lights(self):
        colors = {dir: self.red for dir in self.lights}

        if self.state == "NS_green":
            colors["N"], colors["S"] = self.green, self.green
        elif self.state == "NS_yellow":
            colors["N"], colors["S"] = self.yellow, self.yellow
        elif self.state == "EW_green":
            colors["E"], colors["W"] = self.green, self.green
        elif self.state == "EW_yellow":
            colors["E"], colors["W"] = self.yellow, self.yellow

        for direction, pos in self.lights.items():
            screen.blit(colors[direction], pos)

        ns_timer = max(0, int(self.timer_value)) if self.state.startswith("NS") else max(0, int(self.timer_value) + 5)
        ew_timer = max(0, int(self.timer_value)) if self.state.startswith("EW") else max(0, int(self.timer_value) + 5)

        self.display_timer(600, 150, ns_timer)  # North
        self.display_timer(600, 550, ns_timer)  # South
        self.display_timer(750, 300, ew_timer)  # East
        self.display_timer(450, 300, ew_timer)  # West

    def display_timer(self, x, y, time_value):
        timer_text = self.font.render(str(time_value), True, (255, 255, 255))
        screen.blit(timer_text, (x, y))

class Simulation:
    def __init__(self):
        self.traffic_light = Traffic()
        self.last_time = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()
        dt = current_time - self.last_time
        self.last_time = current_time
        self.traffic_light.update_state(dt)

    def draw(self):
        screen.blit(image, (0, 0))
        self.traffic_light.draw_lights()

def main():
    clock = pygame.time.Clock()
    simulation = Simulation()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        simulation.update()
        simulation.draw()
        
        pygame.display.update()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()