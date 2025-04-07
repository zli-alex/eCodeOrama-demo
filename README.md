# A Simple eCodeOrama Project Demo: Graph Building and GUI

## Project Overview

eCodeOrama targets to create a interactive and educational tool to extract, 
visualize and edit the layout.
In this repo, I try to provide a simple demo of the "visualization" part of eCodeOrama
with Graph building and GUI.

## Prerequisites and dependencies
- Python 3.x
- NetworkX
- PyQt5
- json
- matplotlib

You may install the required packages using pip:
```bash
pip install networkx matplotlib pyqt5
```

## Usage
After cloning and navigating to the project directory, please make sure that 
`parsed_code.json` is in the directory. Then, you can run the demo by executing:
```bash
python demo.py
```
This will open a GUI window, showing a graph representation of the layout.

## Program Details
### Input
As a simple demo project, I skipped the parsing part and used a pre-parsed JSON file `parsed_code.json`
as a representation of the code.

### Output
Rynning the demo will create a GUI window that displays a graph of the parsed code.
- Nodes: Each node represents a script from a sprite. The label is formatted to show the sprite’s name and its event (or received message).
- Edges: An edge from one node to another indicates that a script broadcasts a message that is received by another script. The edge label shows the message name.

