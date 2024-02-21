import pygame
import random
import math
import colorsys
import copy

WIDTH, HEIGHT = 1200, 800
SAND_SIZE = 4
GRAVITY = 0.15
SPAWN_RADIUS = 10
SPAWN_AMOUNT = 20
BACKGROUND_COLOR = (0, 0, 0)

class SandParticle:
    baseColor = 220

    def __init__(self, vel_y: float) -> None:
        self.vel_y = vel_y
        self.set_color()

    # get the next pixel color
    def set_color(self) -> None:
        hue = self.__class__.baseColor / 360
        saturation = 0.2
        value = 0.9
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        self.color = pygame.Color(int(r * 255), int(g * 255), int(b * 255))
        self.__class__.baseColor = (self.__class__.baseColor + 0.1) % 360

class Grid:
    def __init__(self, width=1200, height=800, sandSize=4, gravity=0.2, spawnRadius=10, spawnAmount=20) -> None:
        self.width = width // sandSize
        self.height = height // sandSize
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.sandSize = sandSize
        self.gravity = gravity
        self.spawnRadius = spawnRadius
        self.spawnAmount = spawnAmount
    
    def createEmptyGrid(self):
        return [[None for _ in range(self.width)] for _ in range(self.height)]
    
    # generate random coordinates in a circle
    def generateRandomPoints(self, x, y, radius, amount):
        points =  []
        for _ in range(amount):
            theta = random.uniform(0, 2*math.pi)
            r = radius * math.sqrt(random.uniform(0, 1))
            x_polar = x + r * math.cos(theta)
            y_polar = y + r * math.sin(theta)
            point = (int(x_polar), int(y_polar))
            points.append(point)
        return points
    
    # add some sand particles around (x,y)
    def add(self, x, y):
        points = self.generateRandomPoints(x, y, self.spawnRadius, self.spawnAmount)
        for point in points:
            if 0 <= point[0] < self.width and 0 <= point[1] < self.height:
                if self.grid[point[1]][point[0]] is None:
                    self.grid[point[1]][point[0]] = SandParticle(self.gravity)
    
    def update(self):
        nextGrid = self.createEmptyGrid()
        
        # just copy last row since it won't move
        for x, sandParticle in enumerate(self.grid[self.height - 1]):
            nextGrid[self.height - 1][x] = copy.deepcopy(sandParticle)
        
        # update others rows starting from the bottom
        for y in range(len(self.grid) - 2, -1, -1):
            for x, sandParticle in enumerate(self.grid[y]):
                if sandParticle is None:
                    continue
                if self.grid[y + 1][x] is None: # the sand particle can at least fall one pixel
                    next_pos = int(y + sandParticle.vel_y)
                    
                    if next_pos >= self.height:
                        next_pos = self.height - 1
                    
                    # let's find if a sand particle in on the path
                    for yy in range(next_pos, y, -1):
                        if self.grid[yy][x] is not None:
                            next_pos = yy - 1
                    
                    nextGrid[next_pos][x] = copy.deepcopy(sandParticle)
                    
                    if next_pos != int(y + sandParticle.vel_y):
                        nextGrid[next_pos][x].vel_y = self.grid[next_pos + 1][x].vel_y if next_pos + 1 < self.height else 0
                    else:
                        nextGrid[next_pos][x].vel_y += self.gravity
                else: # the sand particle is blocked
                    def isWithin(x):
                        if x >= 0 and x < self.width:
                            return True
                        return False
                    
                    directions = [delta for delta in [-1,1] if isWithin(x + delta) and self.grid[y + 1][x + delta] is None]
                    selected_direction = random.choice(directions) if directions else None
                    
                    # can the sand particle fall on the sides?
                    if not selected_direction:
                        nextGrid[y][x] = sandParticle
                    else:
                        nextGrid[y + 1][x + selected_direction] = sandParticle
        self.grid = nextGrid

    def draw(self, screen):
        buffer_surface = pygame.Surface((self.width * self.sandSize, self.height * self.sandSize))
        for y, line in enumerate(self.grid):
            for x, sand in enumerate(line):
                if sand is not None:
                    pygame.draw.rect(buffer_surface, sand.color, (x * self.sandSize, y * self.sandSize, self.sandSize, self.sandSize))
        screen.blit(buffer_surface, (0, 0))

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Sand Simulator")
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    grid = Grid(width=WIDTH, height=HEIGHT, sandSize=SAND_SIZE, gravity=GRAVITY, spawnRadius=SPAWN_RADIUS, spawnAmount=SPAWN_AMOUNT)
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
        grid.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()
