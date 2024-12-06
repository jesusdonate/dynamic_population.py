import argparse
import networkx as nx
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import random


# Function to read a .gml graph file
def read_graph(input_file) -> nx.Graph:
    print(f"Loading graph from {input_file}...")
    try:
        G = nx.read_gml(input_file)
        print(f"Returning {G}")
        return G
    except nx.NetworkXError as e:
        # Handle error if the file cannot be read as a .gml
        print(f"Could not read .gml file from {input_file}...")
        print(e)
    except FileNotFoundError as e:
        # Handle error if the file is not found
        print(f"Could not read .gml file from {input_file}...")
        print(e)


def simulate_cascade(graph, initiators, threshold, interactive=False, plot=False):
    """Simulate cascading effect through the network."""
    graph: nx.DiGraph = graph.to_undirected()  # Ensures graph is undirected

    state = {node: 0 for node in graph.nodes}  # 0 = inactive, 1 = active
    for node in initiators:
        state[str(node)] = 1

    if interactive:
        show_graph_cascade(graph, state, f'Initial Graph')  # Shows initial graph before cascade

    activations_per_round = []
    rounds = 0
    while True:
        rounds += 1
        new_activations = []
        for node in graph.nodes:
            if state[str(node)] == 0:  # Inactive
                active_neighbors = sum(state[str(neighbor)] for neighbor in graph.neighbors(node))
                p = active_neighbors / len(list(graph.neighbors(node)))
                if p >= threshold:
                    print(f'For node {node}, p:{p:.3f} >= threshold:{threshold}, so {node} becomes active\n')
                    new_activations.append(str(node))
                else:
                    print(f'For node {node}, p:{p:.3f} < threshold:{threshold}, so {node} remains inactive.\n')
                    active_neighbors / len(list(graph.neighbors(node)))

        print(f'*** Round {rounds} finished. Newly activated nodes: {new_activations}', end='\n\n\n')
        for node in new_activations:
            state[node] = 1
        activations_per_round.append(new_activations)

        if interactive:
            show_graph_cascade(graph, state, f'Round {rounds}')  # Show graph after each round

        if not new_activations:  # Stop loop when cascade has ended
            break

    print(f"Cascade simulation completed in {rounds} rounds since no new nodes were activated.")
    if plot:
        plot_activations_over_time(activations_per_round)


def show_graph_cascade(graph, state, title=''):
    plt.figure()
    plt.title(title)

    # Define color map for nodes
    color_map = ['red' if state[node] == 1 else 'blue' for node in graph.nodes]

    # Draw the graph
    nx.draw(graph, node_color=color_map, with_labels=True)

    # Create legend entries
    legend_elements = [
        mpatches.Patch(color='red', label='Active'),
        mpatches.Patch(color='blue', label='Inactive')
    ]

    # Add legend to the plot
    plt.legend(handles=legend_elements, loc='upper right', title="Node States")

    # Show the plot
    plt.show()


def plot_activations_over_time(activations_per_round):
    rounds = list(range(1, len(activations_per_round) + 1))

    # Compute the cumulative number of activated nodes over time
    cumulative_activations = [0]  # Start with 0 active nodes
    for activations in activations_per_round:
        cumulative_activations.append(cumulative_activations[-1] + len(activations))
    cumulative_activations = cumulative_activations[1:]  # Remove the initial 0

    # Plot the cumulative activations
    plt.figure(figsize=(8, 6))
    plt.plot(rounds, cumulative_activations, marker='o', linestyle='-', color='b', label="Cumulative Active Users")
    plt.title("Cascading Activations Over Time (Excluding Initiators)")
    plt.xlabel("Round")
    plt.ylabel("Total Number of Activated Users")
    plt.xticks(rounds)  # Display all rounds on x-axis
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()


def simulate_covid(graph, initiators, p_infection=0, lifespan=5, shelter=0.0, vaccination=0,
                   interactive=False, plot=False):
    """Simulate pandemic spread through the network."""
    graph: nx.DiGraph = graph.to_directed()  # Ensures graph is directed

    state = {node: 0 for node in graph.nodes}  # 0 = susceptible, 1 = infected, 2 = recovered, 3 = sheltered
    infected_days = []  # Contains a tuple (node_id, days_infected)
    recovery_days = []  # Contains a tuple (node_id, days_recovering)
    for node in initiators:
        state[str(node)] = 1
        infected_days.append((str(node), 0))
    infection_lifespan = 3  # Nodes infect other node for this many days before recovering
    recovery_lifespan = 3  # Nodes recover for this many days before becoming susceptible again

    # Gives vaccination to random nodes
    vaccinated_nodes = set(random.sample(list(graph.nodes), int(vaccination * len(graph))))
    print("Vaccinated Nodes:", vaccinated_nodes)
    vaccine_effect = 0.70

    # Give shelter to random nodes if shelter is a proportion
    if isinstance(shelter, float):
        sheltered_nodes = random.sample(list(graph.nodes), int(shelter * len(graph)))
        for node in sheltered_nodes:
            state[str(node)] = 3
    else:
        sheltered_nodes = shelter
        for node in sheltered_nodes:
            try:
                state[str(node)] = 3
            except KeyError as e:
                print(f"Error: Node {e.args[0]} does not exist in the graph.")
    print("Sheltered Nodes:", sheltered_nodes)

    if interactive:
        plot_graph(graph, state, 'Initial Graph')

    infections_per_day = []  # This list is to keep track of which nodes got infected on which day
    for day in range(lifespan):
        # Updates days infected and remove recovered nodes
        for node, infected_day in infected_days[:]:  # Use a copy of the list to modify it safely
            if node in sheltered_nodes:
                state[node] = 3
                continue
            if infected_day + 1 > infection_lifespan:
                state[node] = 2  # Set node as recovered
                infected_days.remove((node, infected_day))  # Remove the node from the infected list
                recovery_days.append((node, 0))  # Add to recovery_days
                print(f"Node {node} has recovered.")
            else:
                # Increment days infected
                index = infected_days.index((node, infected_day))
                infected_days[index] = (node, infected_day + 1)

        # Updates days recovering and make nodes susceptible again
        for node, days_recovering in recovery_days[:]:  # Use a copy of the list to modify it safely
            if days_recovering + 1 > recovery_lifespan:
                state[node] = 0  # Set node as susceptible
                recovery_days.remove((node, days_recovering))  # Remove from recovery_days
                print(f"Node {node} has become susceptible again.")
            else:
                # Increment days recovering
                index = recovery_days.index((node, days_recovering))
                recovery_days[index] = (node, days_recovering + 1)

        # Spread the infection
        new_infections = set()  # Using a set to avoid duplicates
        for node in graph.nodes:
            # print('node:', node, ", state[node]:", state[str(node)])
            if state[str(node)] == 1:  # Infected
                for neighbor in graph.neighbors(node):
                    # print('neighbor:', neighbor, ", state[neighbor]:", state[str(neighbor)])
                    if state[str(neighbor)] == 0 and str(neighbor) not in sheltered_nodes:
                        # print("Neighbor not in shelter")
                        if str(neighbor) in vaccinated_nodes:
                            if random.random() < p_infection * (1 - vaccine_effect):
                                new_infections.add(str(neighbor))
                                # print('vaccinated neighbor is infected')
                        elif random.random() < p_infection:
                            new_infections.add(str(neighbor))
                            # print('neighbor is infected')

        # Updates the state of newly infected nodes
        for node in new_infections:
            state[str(node)] = 1
            infected_days.append((str(node), 0))  # Add the new infection with 0 days infected

        print('New infections: ', new_infections)

        # Keep track of infections per day
        infections_per_day.append(len(new_infections))

        print(f"Day {day + 1}: {len(new_infections)} new infections.\n")

        if interactive:
            plot_graph(graph, state, f'Day {day + 1}: {len(new_infections)} new infections.', vaccinated_nodes)

    if plot:
        plt.figure(figsize=(8, 6))
        plt.plot(range(len(infections_per_day)), infections_per_day, marker='o', label="New Infections")
        plt.title("Number of New Infections Per Day")
        plt.xlabel("Day")
        plt.ylabel("New Infections")
        plt.legend()
        plt.grid(True)
        plt.show()

    print(f"COVID simulation completed over {day + 1} days.")


def plot_graph(graph, state, title="", vaccinated_nodes=[]):
    # Define color map for nodes
    color_map = [
        'purple' if state[node] == 3 else
        'green' if state[node] == 2 else
        'red' if state[node] == 1 else
        'blue' if node in vaccinated_nodes else
        'gray' for node in graph.nodes
    ]

    plt.figure(figsize=(8, 6))
    ax = plt.gca()
    nx.draw(graph, node_color=color_map, with_labels=True, ax=ax)

    # Create legend
    legend_elements = [
        mpatches.Patch(color='gray', label='Susceptible'),
        mpatches.Patch(color='red', label='Infected'),
        mpatches.Patch(color='green', label='Recovered'),
        mpatches.Patch(color='purple', label='Sheltered'),
        mpatches.Patch(color='blue', label='Vaccinated')
    ]
    ax.legend(handles=legend_elements, loc='upper right', title="Node States")
    ax.set_title(title)
    plt.show()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="Path to the graph file (GML format).")
    parser.add_argument("--action", choices=['cascade', 'covid'], required=True, help="Action to simulate.")
    parser.add_argument("--initiator", type=str, required=True, help="Comma-separated list of initiator nodes.")
    parser.add_argument("--threshold", type=float, help="Threshold for cascade effect.")
    parser.add_argument("--probability_of_infection", type=float, help="Probability of infection for COVID simulation.")
    parser.add_argument("--lifespan", type=int, help="Number of time steps for the simulation.")
    parser.add_argument("--shelter", type=str, help="Proportion of nodes to shelter.")
    parser.add_argument("--vaccination", type=float, help="Proportion of vaccinated nodes.")
    parser.add_argument("--interactive", action="store_true", help="Plot the graph at each step.")
    parser.add_argument("--plot", action="store_true", help="Plot final results.")

    args = parser.parse_args()

    # Load graph
    graph = read_graph(args.file_path)
    if not graph:
        print("Graph is None. Enter a valid .gml file path.")
        return

    try:
        initiators = list(map(int, args.initiator.split(',')))
        threshold = 0
        p_infection = args.probability_of_infection
        lifespan = 5
        shelter = 0.0
        vaccination = 0

        if args.shelter:
            if args.shelter.startswith('[') and args.shelter.endswith(']'):
                # Shelter is a list of nodes
                shelter = args.shelter.strip('[').strip(']')
                shelter = list(map(int, shelter.split(',')))

            else:
                # Try to interpret shelter as a float (proportion)
                try:
                    shelter_list = args.shelter.split(',')
                    if len(shelter_list) == 1:
                        shelter = float(shelter_list[0])  # Single float value
                    else:
                        raise ValueError(
                            "Shelter parameter must be a number between 0 and 1 OR a list of nodes with brackets (ex. --shelter [1,2,5]).")
                except ValueError:
                    raise ValueError(
                        "Shelter parameter must be a number between 0 and 1 OR a list of nodes with brackets (ex. --shelter [1,2,5]).")

        if args.threshold:
            if args.threshold < 0 or args.threshold > 1:
                raise ValueError("Threshold parameter must be between 0 and 1.")
            threshold = args.threshold

        if args.vaccination:
            if args.vaccination < 0 or args.vaccination > 1:
                raise ValueError("Vaccination parameter must be between 0 and 1.")
            vaccination = args.vaccination

        if args.lifespan:
            lifespan = args.lifespan

    except ValueError as e:
        if e.args[0].startswith("invalid literal for int()"):
            print('All values inside initiators or shelter must be integers.')
        else:
            print(e)
        return

    # Perform the action
    if args.action == 'cascade':
        if args.threshold is None:
            raise ValueError("Threshold is required for cascade simulation.")
        simulate_cascade(graph, initiators, threshold, args.interactive, args.plot)
    elif args.action == 'covid':
        simulate_covid(graph, initiators, p_infection, lifespan, shelter, vaccination, args.interactive, args.plot)


if __name__ == "__main__":
    main()
