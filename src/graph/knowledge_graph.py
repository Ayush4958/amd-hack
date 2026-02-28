import pandas as pd
import networkx as nx
from pyvis.network import Network


DATA_PATH = "data/cleaned/final_enriched_dataset.csv"


def build_graph():

    df = pd.read_csv(DATA_PATH)

    # Aggregate system-level data (state-crop)
    system_df = (
        df.groupby(["state", "crop"])
        .agg({
            "agro_stress_index": "mean",
            "resilience_score": "mean",
            "intervention_priority": lambda x: x.mode()[0] if not x.mode().empty else "Unknown"
        })
        .reset_index()
    )

    # Create graph
    G = nx.Graph()

    # ------------------------------------------------------
    # Add State Nodes
    # ------------------------------------------------------
    states = system_df["state"].unique()
    for state in states:
        G.add_node(
            f"state_{state}",
            label=state,
            type="state"
        )

    # ------------------------------------------------------
    # Add Crop Nodes
    # ------------------------------------------------------
    crops = system_df["crop"].unique()
    for crop in crops:
        G.add_node(
            f"crop_{crop}",
            label=crop,
            type="crop"
        )

    # ------------------------------------------------------
    # Add System Nodes + Edges
    # ------------------------------------------------------
    for _, row in system_df.iterrows():

        system_id = f"system_{row['state']}_{row['crop']}"

        G.add_node(
            system_id,
            label=f"{row['state']} - {row['crop']}",
            type="system",
            stress=round(row["agro_stress_index"], 3),
            resilience=round(row["resilience_score"], 3),
            priority=row["intervention_priority"]
        )

        # Connect to state
        G.add_edge(
            f"state_{row['state']}",
            system_id,
            relationship="HAS_SYSTEM"
        )

        # Connect to crop
        G.add_edge(
            f"crop_{row['crop']}",
            system_id,
            relationship="SYSTEM_FOR"
        )

    return G


def visualize_graph(G):

    net = Network(
    height="700px",
    width="100%",
    bgcolor="#0B0F1A",
    font_color="white"
)
    net.set_options("""
    var options = {
    layout: {
        hierarchical: {
        enabled: true,
        levelSeparation: 180,
        nodeSpacing: 150,
        treeSpacing: 200,
        direction: "LR",
        sortMethod: "directed"
        }
    },
    physics: false,
    interaction: {
        dragView: true,
        zoomView: true
    }
    }
    """)


    for node, data in G.nodes(data=True):

        if data["type"] == "state":
            color = "#1f77b4"  # blue

        elif data["type"] == "crop":
            color = "#2ca02c"  # green

        else:
            # System node color by priority
            if data["priority"] == "High Priority":
                color = "#d62728"  # red
            elif data["priority"] == "Moderate Priority":
                color = "#ff7f0e"  # orange
            else:
                color = "#7f7f7f"  # grey

        net.add_node(
            node,
            label=data["label"],
            color=color,
            title=str(data)
        )

    for source, target, data in G.edges(data=True):
        net.add_edge(source, target)

    net.write_html("static/agro_knowledge_graph.html")


def main():

    print("Building knowledge graph...")
    G = build_graph()

    print("Visualizing graph...")
    visualize_graph(G)

    print("Graph saved as agro_knowledge_graph.html")


if __name__ == "__main__":
    main()