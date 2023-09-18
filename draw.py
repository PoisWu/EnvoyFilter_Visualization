import sys
import urllib.request, json, graphviz
from type import Type

# Prepare graphviz graph
# Some configuration of the generated image


def download_envoyconfig(ip_address: str, port: int):
    with urllib.request.urlopen(f"http://{ip_address}:{port}/config_dump") as url:
        config_dump = json.load(url)
    return config_dump


def create_diagram(ip_address: str, port: int):
    config_dump = download_envoyconfig(ip_address, port)

    # Create graph
    _graph_attr = {("dpi", "300"), ("style", "rounded")}
    graph = graphviz.Digraph(comment="graph", format="png", graph_attr=_graph_attr)

    envoy_subgraph(graph, config_dump)

    print(graph.source)
    graph.render(directory="graph", view=True)
    return 0


def envoy_subgraph(graph, config_dump):
    g_envoy = graphviz.Digraph(name="cluster_envoy")
    g_envoy.attr(label="envoy")

    # Retrive ListenersConfigDump data
    config_listener_dump = config_dump["configs"][2]
    assert (
        config_listener_dump["@type"] == Type.LISTENERS_CONFIG_DUMP_T
    ), "It is not `ListenersConfigDump` type"

    # Retrive static configuration of listener
    config_static_listeners = config_listener_dump["static_listeners"]
    static_listeners_subgraph(g_envoy, config_static_listeners)

    graph.subgraph(g_envoy)
    return 0


def static_listeners_subgraph(g_envoy, config_static_listeners):
    for config_listener_lastupdate in config_static_listeners:
        config_listener = config_listener_lastupdate["listener"]

        assert config_listener["@type"] == Type.LISTENER_T, "It is not `Listener` type"

        listener_name = config_listener["name"]
        g_listener = graphviz.Digraph(name="cluster_" + listener_name)
        g_listener.attr(label=listener_name)
        config_filter_chains = config_listener["filter_chains"]
        filter_chain_subgraph(g_listener, config_filter_chains, listener_name)

        g_envoy.subgraph(g_listener)

    return 0


def filter_chain_subgraph(g_listener, config_filter_chains, prefix_id):
    for idx, config_filter_chain in enumerate(config_filter_chains):
        # Prepreing prefix for unique node ID
        filter_chain_name = "filter chain No. " + str(idx)
        prefix_id = prefix_id + filter_chain_name

        # Drawing filter_chain subgraph
        g_filter_chain = graphviz.Digraph(name="cluster_" + str(idx))
        g_filter_chain.attr(label=filter_chain_name)
        pre_node_id = None
        for config_filter in config_filter_chain["filters"]:
            pre_node_id = filter_subgraph(
                g_filter_chain, config_filter, prefix_id, pre_node_id
            )
        g_listener.subgraph(g_filter_chain)

    return 0


def filter_subgraph(g_filter_chain, config_filter, prefix_id, pre_node_id):
    filter_name = config_filter["name"].split(".")[-1]
    # Drawing filter subgraph

    g_filter = graphviz.Digraph(name="cluster_" + filter_name)
    g_filter.attr(label=filter_name)

    config_filter_type = config_filter["typed_config"]

    # prefix_filter = f"{listener_name}_{filter_chain_name}_{filter_name}"

    match config_filter_type["@type"]:
        # Http_Connection_Manager type
        case Type.HCM_FILTER_T:
            # Drawing compone in the filter subgraph
            for http_filter in config_filter_type["http_filters"]:
                http_filter_name = http_filter["name"].split(".")[-1]
                id = prefix_id + http_filter_name

                # create node
                g_filter.node(id, http_filter_name)

                # Link up from the previous node
                if pre_node_id:
                    g_filter.edge(pre_node_id, id)

                # Update the previous node
                pre_node_id = id
        case _:
            print("The filter type isn't supported yet", file=sys.stderr)

    g_filter_chain.subgraph(g_filter)
    return id


if __name__ == "__main__":
    # Download configuration of envoy
    create_diagram("localhost", 8001)
    config_dump = download_envoyconfig("localhost", 8001)
