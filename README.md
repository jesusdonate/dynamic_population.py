# Dynamic Population Simulation Script

This python script, `dynamic_population.py`, provides two simulation on network graphs:
1. **Cascade Simulation:** Models the spread of influence in a network based on thresholds.
2. **COVID Simulation:** Models the spread of infection through a population considering infection probabilities, vaccinations, and shelters.

The script uses `.gml` files for graph input and offers interactive visualizations.

---

## Dependencies
Install required packages:

```bash
pip install networkx matplotlib
```

## **How to Run the Script**

Run the script from the command line as follows:

```bash
python dynamic_population.py <file_path> --action <action> [OPTIONS]
```

* <file_path>: Path to the .gml file containing the network graph.
* <action>: The simulation to perform (cascade or covid).

## **Arguments**

| Argument                        | Description                                                          | For action(s) |
|----------------------------------|----------------------------------------------------------------------|---------------|
| `file_path`                     | Path to the `.gml` file. (Required)                                  | **Both**      |
| `--action`                      | Type of simulation: `cascade` or `covid`.                            | **Both**      |
| `--initiator`                   | Comma-separated list of initiator nodes (e.g., `1,2,3`).             | **Both**      |
| `--threshold`                   | Threshold for activation in the cascade simulation (`0.0` to `1.0`). | **Cascade**   |
| `--probability_of_infection`    | Probability of infection for COVID simulation (`0.0` to `1.0`).      | **COVID**     |
| `--lifespan`                    | Number of simulation rounds (default: `5`).                          | **COVID**     |
| `--shelter`                     | Proportion (`0.0` to `1.0`) or list of nodes to shelter (`[1,2,3]`). | **COVID**     |
| `--vaccination`                 | Proportion of nodes vaccinated (`0.0` to `1.0`).                     | **COVID**     |
| `--interactive`                 | Displays the graph at each step of the simulation.                   | **Both**      |
| `--plot`                        | Plots the results of the simulation at the end.                      | **Both**      |

## **Simulations**

### 1. **Cascade Simulation**
Models the spread of influence in a network.

#### Example:
```bash
python dynamic_population.py graph.gml --action cascade --initiator 1,3 --threshold 0.5 --interactive --plot
```

#### Expected Output:
* Console: Displays the nodes activated in each round and whether they become active (become influenced) or not.
* Interactive Graphs: Shows the state of the network at each round.
* Plot: Shows the total sum of active (influenced) nodes per round, **excluding the initiators**.

### 2. **COVID Simulation**
Models the spread of infection with vaccinated and sheltered populations.

#### Example:
```bash
python dynamic_population.py graph.gml --action covid --initiator 2,4 --probability_of_infection 0.6 --lifespan 10 --shelter 0.3 --vaccination 0.5 --interactive --plot
```

#### Expected Output:
* Console: Displays newly infected nodes, recovered nodes, and nodes returning to susceptibility.
* Interactive Graphs: Shows the state of the network at each day. 
* Plot: Number of new infections per day.
