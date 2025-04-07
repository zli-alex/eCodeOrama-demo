import json
import networkx as nx
from collections import defaultdict
from PyQt5 import QtWidgets
from matplotlib.patches import FancyArrowPatch
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

def compose_label(sprite, script):
    """Compose a label for an element in the graph.

    Args:
        sprite (str): name of the sprite
        script (str): name of the script in the sprite

    Returns:
        str: label: sprite name + event
    """
    if script["event"] == "whenIReceive":
        return f"{sprite['name']}:\nreceive {script['message']}"
    else:
        return f"{sprite['name']}:\n{script['event']}"
    
def build_graph(parsed_code):
    """Build a directed graph from the parsed code.

    Args:
        parsed_code (dict): the parsed code in json format

    Returns:
        nx.DiGraph: directed graph representing the code structure
    """
    G = nx.DiGraph()

    # Creation of nodes for each script/sprite
    for sprite in parsed_code["sprites"]:
        for script in sprite["scripts"]: # label: sprite name + event 
            G.add_node(compose_label(sprite, script), sprite=sprite["name"], event=script["event"], message=script.get("message"))

    # message2receivers message -> list of labels
    message2receivers = defaultdict(list)
    for node_label, attrs in G.nodes(data=True):
        if attrs.get("event") == "whenIReceive":
            msg = attrs.get("message")
            if msg:
                message2receivers[msg].append(node_label)

    # Creation of edges
    for sprite in parsed_code["sprites"]:
        for script in sprite["scripts"]:
            sender_label = compose_label(sprite, script)

            for block in script.get("blocks", []):
                if block.get("opcode") in ["event_broadcast", "event_broadcastandwait"]:
                    msg = block.get("message")
                    if msg:
                        for receiver_label in message2receivers[msg]:
                            G.add_edge(sender_label, receiver_label, message=msg)
    
    return G

def compute_layout(G, parsed_code):
    """Compute the layout for nodes and edges in the graph.

    Args:
        G (nx.DiGraph): directed graph representing the code structure
        parsed_code (dict): the parsed code in json format

    Returns:
        dict: node label -> position (x, y)
    """
    pos = {}
    # Order the sprites by their name and order scripts vertically
    sprite_order = {sprite["name"]: i for i, sprite in enumerate(parsed_code["sprites"])}
    y_offsets = {sprite["name"]: 0 for sprite in parsed_code["sprites"]}
    for node_label, attrs in G.nodes(data=True):
        sprite = attrs["sprite"]
        x = sprite_order[sprite]
        y = -y_offsets[sprite]
        pos[node_label] = (x, y)
        y_offsets[sprite] += 1
    return pos

def draw_edges_with_arrows(G, pos, ax, shrink=25, arrowstyle="-|>", arrowsize=15, edge_color="gray"):
    for (u, v, data) in G.edges(data=True):
        arrow = FancyArrowPatch(
            posA=pos[u],
            posB=pos[v],
            arrowstyle=arrowstyle,
            mutation_scale=arrowsize,
            shrinkA=shrink,  # controls gap at the start
            shrinkB=shrink,  # controls gap at the end
            color=edge_color,
        )
        ax.add_patch(arrow)

def main():
    with open("parsed_code.json") as f:
        parsed_code = json.load(f)

    G = build_graph(parsed_code)
    pos = compute_layout(G, parsed_code)

    # Visualize with PyQt5 and Matplotlib
    # Set up PyQt5 application and main window
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("eCodeOrama Demo")
    central_widget = QtWidgets.QWidget(window)
    layout = QtWidgets.QVBoxLayout(central_widget)
    window.setCentralWidget(central_widget)
    # Set up the matplotlib figure and canvas
    figure = Figure(figsize=(8, 4))
    canvas = FigureCanvas(figure)
    layout.addWidget(canvas)
    ax = figure.add_subplot(111)
    x_values = [p[0] for p in pos.values()]
    y_values = [p[1] for p in pos.values()]
    margin = 0.5  # adjust as needed
    ax.set_xlim(min(x_values) - margin, max(x_values) + margin)
    ax.set_ylim(min(y_values) - margin, max(y_values) + margin)
    ax.set_axis_off()

    # Draw on the Axes using networkx
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color="skyblue", node_shape="s", node_size=1200) # nodes: boxes
    labels = {node: node for node in G.nodes()} # node labels
    nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=8)
    draw_edges_with_arrows(G, pos, ax) # edges: nx.draw_networkx_edges does not draw arrowhead well?
    edge_labels = {(u, v): data["message"] for u, v, data in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax, font_size=8, label_pos=0.5)

    canvas.draw()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()