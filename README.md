# Predator-Prey Ecosystem Simulation

An animated 2D simulation modeling the population dynamics of rabbits, foxes, and grass on a 100x100 grid. Built as part of DS3500 at Northeastern University.

Each generation, animals move randomly, consume resources, reproduce when sufficiently fed, and die if they go too long without eating. The result is an emergent predator-prey population cycle driven entirely by simple rules.

**Developed collaboratively with Neil Keltcher.**

---

## How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/DarshanBalaji-ML/predator-prey-simulation.git
   cd predator-prey-simulation
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the simulation:
   ```bash
   python alife.py
   ```

A matplotlib animation window will open showing the simulation in real time.

---

## Dependencies

- Python 3.x
- NumPy
- Matplotlib
