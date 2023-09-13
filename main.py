import urllib.request, json, graphviz

l = [1, 3, 4, 3]
# Support static config
LISTENERS_CONFIG_DUMP_T = "type.googleapis.com/envoy.admin.v3.ListenersConfigDump"

with urllib.request.urlopen("http://localhost:8001/config_dump") as url:
    config_dump = json.load(url)

_graph_attr = {("dpi", "300"), ("style", "rounded")}
graph = graphviz.Digraph(comment="graph", format="png", graph_attr=_graph_attr)

envoy = graphviz.Digraph(name="cluster_envoy")
envoy.attr(label="envoy")

listener_config_dump = config_dump["config"][2]

assert (
    listener_config_dump["@type"] == LISTENERS_CONFIG_DUMP_T
), "listener type isn't right"

static_listeners = listener_ocnfig_dump["static_listeners"]

nb_static_listeners = len(static_listeners)
for i in range(nb_static_listeners):
    print("hello")


graph.subgraph(envoy)
graph.render(directory="graph", view=True)
