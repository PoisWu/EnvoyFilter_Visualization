import sys
import urllib.request, json, graphviz
from type import Type

# Prepare graphviz graph
# Some configuration of the generated image

graph = None

# envoy config its open port with 'listener' configuration
# The format of listener_info is {address: "0.0.0.0", port_value: <int>}
# Can be fetch under [listener][address][socket_address]
listener_info = None


def download_envoyconfig(ip_address: str, port: int):
    """Dowload envoy's configuration
    Args:
        ip_address (str): The IP address of admin API endpoint
        port (int): The port of admin API endpoint
    Returns:
        config_dump
    """

    with urllib.request.urlopen(f"http://{ip_address}:{port}/config_dump") as url:
        config_dump = json.load(url)
    return config_dump


def create_diagram(ip_address: str, port: int):
    """Create a diagram of envoy's listeners
    Args:
        ip_address (str): The IP address of admin API endpoint
        port (int): The port of admin API endpoint
    """

    # Download config of envoy
    config_dump = download_envoyconfig(ip_address, port)

    # configuration of graph
    _graph_attr = {
        ("dpi", "300"),
        ("style", "rounded"),
        ("compound", "true"),
        ("rankdir", "LR"),
    }

    # Create graph
    global graph
    graph = graphviz.Digraph(comment="graph", format="png", graph_attr=_graph_attr)

    graph.node("client", label="client")
    graph.attr("node", color="#E8CEB5", style="filled")

    # Generate subgraph for envoy
    envoy_subgraph(graph, config_dump)

    if __debug__:
        print(graph.source)

    # Render the diagraph
    graph.render(directory="graph", view=True)

    return 0


def envoy_subgraph(graph, config_dump):
    """Create a diagram for envoy's listeners
    Args:
        graph: Root parant graph that diagram is put inside the diagram
        config_dump: The dump configuration of envoy proxy
    """

    # Create envoy subgraph
    g_envoy = graphviz.Digraph(name="cluster_envoy")
    g_envoy.attr(label="envoy", bgcolor="#F1F1F1")

    # Retrive ListenersConfigDump data
    config_listener_dump = config_dump["configs"][2]
    assert (
        config_listener_dump["@type"] == Type.LISTENERS_CONFIG_DUMP_T
    ), "It is not `ListenersConfigDump` type"

    # Retrive static configuration of listener
    config_static_listeners = config_listener_dump["static_listeners"]

    # Genegrate listener's diagram
    static_listeners_subgraph(g_envoy, config_static_listeners)

    # Put envoy diagram into root graph
    graph.subgraph(g_envoy)
    return 0


def static_listeners_subgraph(g_envoy, config_static_listeners):
    """Generate diagram of static listener
    Args:
        g_envoy: parent envoy graph that diagram is put inside the diagram
        config_static_listeners: The dump configuration of static listeners
    """
    # static_listeners contain multiple listener
    for config_listener_lastupdate in config_static_listeners:
        config_listener = config_listener_lastupdate["listener"]

        assert config_listener["@type"] == Type.LISTENER_T, "It is not `Listener` type"

        listener_name = config_listener["name"]

        # Create diagram for listener
        g_listener = graphviz.Digraph(name=f"cluster_{listener_name}")
        g_listener.attr(
            label=f"Listener: {listener_name}",
            bgcolor="#FFF0C5",
            fontsize="5pt",
            fontname="Hack Nerd Font Mono",
            labeljust="r",
        )

        global listener_info
        listener_info = config_listener["address"]["socket_address"]

        config_filter_chains = config_listener["filter_chains"]

        # Generate diagram for filter chains inside listener
        filter_chain_subgraph(g_listener, config_filter_chains, listener_name)

        # put diagram of listener into envoy graph
        g_envoy.subgraph(g_listener)
    return 0


def filter_chain_subgraph(g_listener, config_filter_chains, prefix_id):
    """Generate diagram of filter_chain
    Args:
        g_listener: parent listener graph that filter chain diagram is put inside the diagram
        config_filter_chains: The configuration of multiple filter chains
        prefix_id: The prefix for filters' id
    """

    for idx, config_filter_chain in enumerate(config_filter_chains):
        # Prepreing prefix for unique node ID
        filter_chain_name = "filter chain No. " + str(idx)
        prefix_id = prefix_id + filter_chain_name

        # Create filter_chain subgraph
        g_filter_chain = graphviz.Digraph(name=prefix_id)
        g_filter_chain.attr(label=filter_chain_name, bgcolor="#C7DEF1")
        pre_node_id = "client"

        # Generate filter's graph
        for config_filter in config_filter_chain["filters"]:
            pre_node_id = filter_subgraph(
                g_filter_chain, config_filter, prefix_id, pre_node_id
            )
        g_listener.subgraph(g_filter_chain)

    return 0


def filter_subgraph(g_filter_chain, config_filter, prefix_id, pre_node_id):
    """Generate diagram of filter
    Args:
        g_filter_chain : parent filter chain graph that filter diagram is put inside the diagram
        config_filter: The configuration of filter
        prefix_id: The prefix for filters' id
        pre_node_id: ID of previous filter (filter chain)
    """
    global graph
    filter_name = config_filter["name"].split(".")[-1]

    # Drawing filter subgraph
    g_filter = graphviz.Digraph(name="cluster_" + prefix_id + filter_name)
    g_filter.attr(label=filter_name)
    g_filter.attr("node", bgcolor="#E8CEB5")

    config_filter_type = config_filter["typed_config"]

    match config_filter_type["@type"]:
        # Generate diagram for Http_Connection_Manager type
        case Type.HCM_FILTER_T:
            # Drawing compone in the filter subgraph
            for http_filter in config_filter_type["http_filters"]:
                http_filter_name = http_filter["name"].split(".")[-1]
                id = prefix_id + http_filter_name

                # create node
                g_filter.node(id, http_filter_name)

                # Link up from the previous node
                if pre_node_id != "client":
                    g_filter.edge(pre_node_id, id)
                else:
                    address = listener_info["address"]
                    port = listener_info["port_value"]

                    # graph.edge(pre_node_id, id, taillabel=f"{address}:{port}" )
                    graph.edge(
                        pre_node_id,
                        id,
                        taillabel=f"{port}",
                        fontsize="7pt",
                        fontname="Hack Nerd Font Mono",
                    )

                # Update the previous node
                pre_node_id = id
        case _:
            print("The filter type isn't supported yet", file=sys.stderr)

    # Add filter into filter_chain
    g_filter_chain.subgraph(g_filter)
    return id


if __name__ == "__main__":
    # Download configuration of envoy
    create_diagram("localhost", 8001)
