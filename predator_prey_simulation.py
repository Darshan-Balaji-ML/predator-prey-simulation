"""
DS3500
Homework 5
An animated Artificial Life Simulation modeling predator-prey ecosystem dynamics.
Simulates the interactions between rabbits, foxes, and grass on a 2D grid,
demonstrating population cycles driven by hunger, reproduction, and resource availability.

Neil Keltcher
Darshan Balaji
"""

import random as rnd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors
import numpy as np
import copy

ARRSIZE = 100       # The dimensions of the square grid field (ARRSIZE x ARRSIZE)
FIGSIZE = 8         # Figure size in inches for the animation window
INIT_RABBITS = 15   # Number of rabbits at the start of the simulation
INIT_FOXES = 5      # Number of foxes at the start of the simulation
GRASS_RATE = 0.15   # Probability that grass regrows at any given cell per generation
OFFSPRING = 3       # Maximum number of offspring an animal can produce per generation
SPEED = 10          # Number of generations computed per animation frame


class Animal:
    """
    Represents a generic animal (rabbit or fox) roaming a 2D grid field.

    Animals move randomly each generation, eat based on their type,
    reproduce when sufficiently fed, and die if they go too long without eating.
    The same class is used for both rabbits and foxes, with behavior
    differentiated via constructor parameters.
    """

    def __init__(self, max_offspring=1, starvation_level=1, reproduction_level=1):
        """
        Initialize an animal at a random position on the field.

        Args:
            max_offspring (int): Maximum number of offspring produced per reproduction event.
            starvation_level (int): Number of consecutive generations without food before death.
            reproduction_level (int): Amount of food consumed required to trigger reproduction.
        """
        self.x = rnd.randrange(0, ARRSIZE)
        self.y = rnd.randrange(0, ARRSIZE)
        self.eaten = 0  # Cumulative food consumed (used to trigger reproduction)
        self.max_offspring = max_offspring
        self.starvation_level = starvation_level
        self.reproduction_level = reproduction_level
        self.hunger = 0  # Consecutive generations without food (used to trigger death)
        self.alive = True

    def reproduce(self):
        """
        Produce a single offspring at the same grid location as the parent.

        Reproduction resets the parent's eaten counter to zero,
        representing the energy cost of reproducing.

        Returns:
            Animal: A deep copy of the parent animal placed at the same location.
        """
        self.eaten = 0
        return copy.deepcopy(self)

    def eat(self, amount):
        """
        Feed the animal, increasing its consumed food count.

        Args:
            amount (int): Amount of food consumed (1 for grass, 1 for a rabbit).
        """
        self.eaten += amount

    def move(self):
        """
        Move the animal one step in a random direction (up, down, left, right, or stay).
        Movement wraps around the edges of the grid toroidally.
        Hunger increases by 1 each move regardless of whether food is found.
        """
        # Wrap around grid edges using modulo to create a toroidal field
        self.x = (self.x + rnd.choice([-1, 0, 1])) % ARRSIZE
        self.y = (self.y + rnd.choice([-1, 0, 1])) % ARRSIZE
        self.hunger += 1


class Field:
    """
    Represents the 2D simulation environment containing grass, rabbits, and foxes.

    The field is a grid where each cell can contain grass or dirt.
    Animals move, eat, reproduce, and die each generation based on
    the predator-prey dynamics of the ecosystem.
    """

    def __init__(self):
        """
        Initialize a fully grass-covered field with no animals.
        Grid values: 0 = dirt, 1 = grass, 2 = rabbit, 3 = fox.
        """
        self.field = np.ones(shape=(ARRSIZE, ARRSIZE), dtype=int)
        self.rabbits = []
        self.foxes = []

    def add_rabbit(self, rabbit):
        """
        Add a rabbit to the field.

        Args:
            rabbit (Animal): The rabbit to add.
        """
        self.rabbits.append(rabbit)

    def add_fox(self, fox):
        """
        Add a fox to the field.

        Args:
            fox (Animal): The fox to add.
        """
        self.foxes.append(fox)

    def rabbit_move(self):
        """
        Move all rabbits one step in a random direction.

        Returns:
            dict: A mapping of rabbit ID strings to their [x, y] positions,
                  used by fox_eat() to detect predation events.
        """
        rab_dct = {}
        rab_count = 0
        for r in self.rabbits:
            r.move()
            rab_count += 1
            rab_dct[f"r{rab_count}"] = [r.x, r.y]
        return rab_dct

    def fox_move(self):
        """ Move all foxes one step in a random direction. """
        for f in self.foxes:
            f.move()

    def rabbit_eat(self):
        """
        Allow all rabbits to eat grass at their current position.
        If grass is present, the rabbit eats it and the cell becomes dirt.
        If no grass is present, the rabbit's hunger increases.
        """
        for r in self.rabbits:
            if self.field[r.x, r.y] == 1:
                r.eat(self.field[r.x, r.y])
                self.field[r.x, r.y] = 0  # Grass is consumed, cell becomes dirt
                r.hunger = 0
            else:
                r.hunger += 1

    def fox_eat(self, rab_dct):
        """
        Allow all foxes to eat rabbits at their current position.
        Any rabbit sharing a cell with a fox is removed from the simulation.

        Args:
            rab_dct (dict): Dictionary of rabbit positions from rabbit_move(),
                            used to detect fox-rabbit collisions.
        """
        for f in self.foxes:
            fox_pos = [f.x, f.y]
            if fox_pos in rab_dct.values():
                # Remove all rabbits at the fox's current position
                self.rabbits = [r for r in self.rabbits if [r.x, r.y] != fox_pos]
                f.hunger = 0
                f.eaten += 1
            else:
                f.hunger += 1

    def survive(self):
        """
        Remove any animals that have exceeded their starvation threshold.
        Both rabbits and foxes are filtered based on their individual starvation levels.
        """
        self.rabbits = [r for r in self.rabbits if r.hunger < r.starvation_level]
        self.foxes = [f for f in self.foxes if f.hunger < f.starvation_level]

    def rabbit_reproduce(self):
        """
        Allow rabbits that have eaten enough to reproduce.
        Each qualifying rabbit produces a random number of offspring (0 to OFFSPRING).
        Newborns are added to the field at the end of the generation.
        """
        born = []
        for r in self.rabbits:
            if r.eaten >= r.reproduction_level:
                for _ in range(rnd.randint(0, OFFSPRING)):
                    born.append(r.reproduce())
        self.rabbits += born

    def fox_reproduce(self):
        """
        Allow foxes that have eaten enough to reproduce.
        Each qualifying fox produces a random number of offspring (0 to OFFSPRING).
        Newborns are added to the field at the end of the generation.
        """
        born = []
        for f in self.foxes:
            if f.eaten >= f.reproduction_level:
                for _ in range(rnd.randint(0, OFFSPRING)):
                    born.append(f.reproduce())
        self.foxes += born

    def grow(self):
        """
        Regrow grass randomly across the field.
        Each dirt cell has a GRASS_RATE probability of becoming grass again.
        """
        growloc = (np.random.rand(ARRSIZE, ARRSIZE) < GRASS_RATE) * 1
        self.field = np.maximum(self.field, growloc)

    def array(self):
        """
        Generate a 2D array representing the current state of the field for visualization.
        Layers animal positions on top of the grass/dirt base layer.

        Returns:
            np.ndarray: Grid with values 0 (dirt), 1 (grass), 2 (rabbit), or 3 (fox).
        """
        overlay = self.field.copy()
        for r in self.rabbits:
            overlay[r.x, r.y] = 2  # Rabbit
        for f in self.foxes:
            overlay[f.x, f.y] = 3  # Fox
        return overlay

    def generation(self):
        """
        Advance the simulation by one generation.
        Executes the full cycle: move → eat → survive → reproduce → grow.

        Returns:
            np.ndarray: The updated field array after this generation.
        """
        rab_dct = self.rabbit_move()
        self.fox_move()
        self.rabbit_eat()
        self.fox_eat(rab_dct)
        self.survive()
        self.rabbit_reproduce()
        self.fox_reproduce()
        self.grow()
        return self.array()


def animate(i, field, im):
    """
    Animation callback function called each frame by FuncAnimation.
    Advances the simulation by SPEED generations and updates the display.

    Args:
        i (int): Current frame index (provided automatically by FuncAnimation).
        field (Field): The simulation field object.
        im (AxesImage): The matplotlib image object to update.

    Returns:
        tuple: Updated image object for the animation.
    """
    for _ in range(SPEED):
        field_arr = field.generation()

    im.set_array(field_arr)
    plt.title(f"Generation: {i * SPEED}  Foxes: {len(field.foxes)}  Rabbits: {len(field.rabbits)}")
    return im,


def run_simulation(num_generations):
    """
    Run the simulation headlessly for a given number of generations and collect population data.
    Useful for analysis and plotting population trends without rendering the animation.

    Args:
        num_generations (int): Number of generations to simulate.

    Returns:
        tuple: Three lists — generations, rabbit_pops, fox_pops —
               each of length num_generations.
    """
    field = Field()

    for _ in range(INIT_RABBITS):
        field.add_rabbit(Animal(max_offspring=OFFSPRING))

    for _ in range(INIT_FOXES):
        field.add_fox(Animal(starvation_level=65, reproduction_level=10, max_offspring=OFFSPRING))

    generations, rabbit_pops, fox_pops = [], [], []

    for gen in range(num_generations):
        field.generation()
        generations.append(gen)
        rabbit_pops.append(len(field.rabbits))
        fox_pops.append(len(field.foxes))

    return generations, rabbit_pops, fox_pops


def main():
    """
    Entry point for the animated simulation.
    Initializes the field with rabbits and foxes, then launches the matplotlib animation.
    """
    field = Field()

    for _ in range(INIT_RABBITS):
        field.add_rabbit(Animal(max_offspring=OFFSPRING))

    for _ in range(INIT_FOXES):
        field.add_fox(Animal(starvation_level=65, reproduction_level=10, max_offspring=OFFSPRING))

    # Color map: black=dirt, green=grass, white=rabbit, red=fox
    my_cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "", ["black", "green", "white", "red"])

    array = np.ones(shape=(ARRSIZE, ARRSIZE))
    fig = plt.figure(figsize=(FIGSIZE, FIGSIZE))
    im = plt.imshow(array, cmap=my_cmap, vmin=0, vmax=3)
    anim = animation.FuncAnimation(fig, animate, fargs=(field, im), frames=10 ** 100, interval=100)
    plt.show()


main()