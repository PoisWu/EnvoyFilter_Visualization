import sys
import urllib.request, json, graphviz

# Prepare graphviz graph

_graph_attr = {("dpi", "300"), ("style", "rounded")}
graph = graphviz.Digraph(comment="graph", format="png", graph_attr=_graph_attr)

g_envoy = graphviz.Digraph(name="cluster_envoy")
g_envoy.attr(label="envoy")


class Type:
    LISTENERS_CONFIG_DUMP_T = "type.googleapis.com/envoy.admin.v3.ListenersConfigDump"
    LISTENER_T = "type.googleapis.com/envoy.config.listener.v3.Listener"
    HCM_FILTER_T = "type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager"
    WASM_FILTER_T = "type.googleapis.com/envoy.extensions.filters.http.wasm.v3.Wasm"
    ROUTER_FILTER_T = (
        "type.googleapis.com/envoy.extensions.filters.http.router.v3.Router"
    )
    UDPA_T = "type.googleapis.com/udpa.type.v1.TypedStruct"


# Download configuration of envoy
with urllib.request.urlopen("http://localhost:8001/config_dump") as url:
    config_dump = json.load(url)

# Listener_Configuration
listener_config_dump = config_dump["configs"][2]

assert (
    listener_config_dump["@type"] == Type.LISTENERS_CONFIG_DUMP_T
), "It is not `ListenersConfigDump` type"

static_listeners = listener_config_dump["static_listeners"]

for listener_lastupdate in static_listeners:
    # Take the right listener
    listener = listener_lastupdate["listener"]
    # The name of listener
    listener_name = listener["name"]

    g_listener = graphviz.Digraph(name="cluster_" + listener_name)
    g_listener.attr(label=listener_name)
    # For a simple check
    assert listener["@type"] == Type.LISTENER_T, "It is not `Listener` type"
    for idx, filter_chain in enumerate(listener["filter_chains"]):
        filter_chain_name = "filter chain No. " + str(idx)
        g_filter_chain = graphviz.Digraph(name="cluster_" + str(idx))
        g_filter_chain.attr(label=filter_chain_name)
        pre_node = None
        for filter in filter_chain["filters"]:
            filter_name = filter["name"].split(".")[-1]
            g_filter = graphviz.Digraph(name="cluster_" + filter_name)
            g_filter.attr(label=filter_name)
            filter_typed_config = filter["typed_config"]
            prefix_filter = f"{listener_name}_{filter_chain_name}_{filter_name}"
            match filter_typed_config["@type"]:
                case Type.HCM_FILTER_T:
                    g_hcm = graphviz.Digraph(name="cluster_" + "HCM")
                    g_hcm.attr(label="HCM")
                    for http_filter in filter_typed_config["http_filters"]:
                        http_filter_name = http_filter["name"].split(".")[-1]
                        g_hcm.node(
                            prefix_filter + http_filter["name"], http_filter_name
                        )
                        if pre_node:
                            g_hcm.edge(pre_node, prefix_filter + http_filter["name"])
                        pre_node = prefix_filter + http_filter["name"]
                    g_filter.subgraph(g_hcm)
                case _:
                    print("The filter type isn't supported yet", file=sys.stderr)
            g_filter_chain.subgraph(g_filter)
        g_listener.subgraph(g_filter_chain)
    g_envoy.subgraph(g_listener)
graph.subgraph(g_envoy)
# print(graph.source)
graph.render(directory="graph", view=True)
