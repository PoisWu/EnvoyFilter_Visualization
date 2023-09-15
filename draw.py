import sys
import urllib.request, json, graphviz
from type import Type

# Prepare graphviz graph
# Some configuration of the generated image
_graph_attr = {("dpi", "300"), ("style", "rounded")}
graph = graphviz.Digraph(comment="graph", format="png", graph_attr=_graph_attr)

# Addin envoy layer
g_envoy = graphviz.Digraph(name="cluster_envoy")
g_envoy.attr(label="envoy")

# Download configuration of envoy
with urllib.request.urlopen("http://localhost:8001/config_dump") as url:
    config_dump = json.load(url)

# The component that we are interested in is live in:
# config_dump["configs"][2]["static/dynamic_listeners"][...]["listener"]["filter_chains][...]["filters"][...]


# Listener_Configuration
# config_dump["configs"][2]
listener_config_dump = config_dump["configs"][2]

assert (
    listener_config_dump["@type"] == Type.LISTENERS_CONFIG_DUMP_T
), "It is not `ListenersConfigDump` type"


# config_dump["configs"][2][static_listeners]
static_listeners = listener_config_dump["static_listeners"]

# config_dump["configs"][2][static_listeners][...]
for listener_lastupdate in static_listeners:
    # config_dump["configs"][2][static_listeners][...]["listener"]
    listener = listener_lastupdate["listener"]
    listener_name = listener["name"]

    # Drawing listener subgraph
    g_listener = graphviz.Digraph(name="cluster_" + listener_name)
    g_listener.attr(label=listener_name)

    # For a simple assert
    assert listener["@type"] == Type.LISTENER_T, "It is not `Listener` type"

    # config_dump["configs"][2][static_listeners][...]["listener"][filter_chain][...]
    for idx, filter_chain in enumerate(listener["filter_chains"]):
        # Prepreing prefix for unique node ID
        filter_chain_name = "filter chain No. " + str(idx)

        # Drawing filter_chain subgraph
        g_filter_chain = graphviz.Digraph(name="cluster_" + str(idx))
        g_filter_chain.attr(label=filter_chain_name)

        # Setting previsous node
        pre_node = None

        # config_dump["configs"][2][static_listeners][...]["listener"][filter_chain][...]["filters"][...]
        for filter in filter_chain["filters"]:
            # Prepreing prefix for unique node ID
            filter_name = filter["name"].split(".")[-1]

            # Drawing filter subgraph
            g_filter = graphviz.Digraph(name="cluster_" + filter_name)
            g_filter.attr(label=filter_name)

            filter_typed_config = filter["typed_config"]

            # Create the prefix for the unique ID of node in the graph, component
            prefix_filter = f"{listener_name}_{filter_chain_name}_{filter_name}"

            # Generate node base on the different type of filter
            match filter_typed_config["@type"]:
                # Http_Connection_Manager type
                case Type.HCM_FILTER_T:
                    # Drawing compone in the filter subgraph
                    for http_filter in filter_typed_config["http_filters"]:
                        http_filter_name = http_filter["name"].split(".")[-1]

                        # create node
                        g_filter.node(
                            prefix_filter + http_filter["name"], http_filter_name
                        )

                        # Link up from the previous node
                        if pre_node:
                            g_filter.edge(pre_node, prefix_filter + http_filter["name"])

                        # Update the previous node
                        pre_node = prefix_filter + http_filter["name"]
                case _:
                    print("The filter type isn't supported yet", file=sys.stderr)

            g_filter_chain.subgraph(g_filter)
        g_listener.subgraph(g_filter_chain)
    g_envoy.subgraph(g_listener)
graph.subgraph(g_envoy)
print(graph.source)
graph.render(directory="graph", view=True)
