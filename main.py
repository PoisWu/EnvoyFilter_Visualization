import urllib.request, json, graphviz

# Support static config

# with urllib.request.urlopen("http://localhost:8001/config_dump") as url:
#     data = json.load(url)

graph = graphviz.Digraph(comment='graph', format='png')

envoy = graphviz.Digraph(name = "envoy")

envoy.edge('foo', 'bar')
graph.subgraph(envoy)

graph.render(directory='graph', view=True)

