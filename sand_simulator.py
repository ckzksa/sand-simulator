import pygame
import random
import math
import colorsys

WIDTH, HEIGHT = 1200, 800
SAND_SIZE = 4
GRAVITY = 1
SAND_COLOR = (194, 178, 128)
BACKGROUND_COLOR = (0, 0, 0)
SPAWN_RADIUS = 10
SPAWN_AMOUNT = 20

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sand Simulator")

class Sand:
    color = 220
    def __init__(self) -> None:
        self.vel_x = 0
        self.vel_y = GRAVITY
        r, g, b = colorsys.hsv_to_rgb(self.__class__.color/360, 1, 1)
        self.color = pygame.Color(int(r * 255), int(g * 255), int(b * 255))
        self.__class__.color = (self.__class__.color + 0.1) if self.__class__.color < 360 else 0

class Grid:
    def __init__(self, width, height) -> None:
        self.width = width // SAND_SIZE
        self.height = height // SAND_SIZE
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
    
    def getAll(self):
        return [element for row in self.grid for element in row if element is not None]
    
    def add(self, x, y):
        points = self.generatePoints(x, y, SPAWN_RADIUS, SPAWN_AMOUNT, unique=True)
        for point in points:
            if 0 <= point[0] < self.width and 0 <= point[1] < self.height:
                if self.grid[point[1]][point[0]] is None:
                    self.grid[point[1]][point[0]] = Sand()
    
    def update(self):
        nextGrid = self.createEmptyGrid()
        for y, line in enumerate(self.grid):
            for x, sand in enumerate(line):
                if sand is None:
                    continue
                if y + sand.vel_y >= self.height:
                    nextGrid[y][x] = sand
                elif self.grid[y + sand.vel_y][x] is None:
                    nextGrid[y + sand.vel_y][x] = sand
                elif self.grid[y + sand.vel_y][x] is not None:
                    self.handleCollision(nextGrid, y, x, sand)
        self.grid = nextGrid
        
    def generatePoints(self, x, y, radius, amount, unique=False):
        points = set() if unique else []
        for _ in range(amount):
            theta = random.uniform(0, 2*math.pi)
            r = radius * math.sqrt(random.uniform(0, 1))
            x_polar = x + r * math.cos(theta)
            y_polar = y + r * math.sin(theta)
            point = (int(x_polar), int(y_polar))
            if unique:
                points.add(point)
            else:
                points.append(point)
        return list(points) if unique else points
    
    def draw(self):
        buffer_surface = pygame.Surface((self.width * SAND_SIZE, self.height * SAND_SIZE))
        for y, line in enumerate(self.grid):
            for x, sand in enumerate(line):
                if sand is not None:
                    pygame.draw.rect(buffer_surface, sand.color, (x * SAND_SIZE, y * SAND_SIZE, SAND_SIZE, SAND_SIZE))
        screen.blit(buffer_surface, (0, 0))
    
    def createEmptyGrid(self):
        return [[None for _ in range(self.width)] for _ in range(self.height)]

    def handleCollision(self, nextGrid, y, x, sand):
        fall_appart = []
        if x - 1 > 0 and self.grid[y + sand.vel_y][x - 1] is None:
            fall_appart.append(x - 1)
        if x + 1 < self.width and self.grid[y + sand.vel_y][x + 1] is None:
            fall_appart.append(x + 1)
        
        if not fall_appart:
            nextGrid[y][x] = sand
        else:
            nextGrid[y + sand.vel_y][random.choice(fall_appart)] = sand

if __name__ == "__main__":
    grid = Grid(WIDTH, HEIGHT)
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        if pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            grid.add(x // SAND_SIZE, y // SAND_SIZE)
        
        screen.fill(BACKGROUND_COLOR)
        grid.update()
        grid.draw()
        
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()
