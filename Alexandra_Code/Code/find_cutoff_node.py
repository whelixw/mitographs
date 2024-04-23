from bdsg.bdsg import ODGI
import sys


def get_number_of_paths_per_node(x):
    node_paths_tuple.append((graph.get_id(x), graph.get_step_count(x)))
    return True

def get_path_support(graph, node_id):
    paths = []
    graph.for_each_step_on_handle(graph.get_handle(node_id), lambda x: paths.append(graph.get_path_name(graph.get_path_handle_of_step(x))) or True)
    return paths



graph = ODGI()
graph.deserialize(sys.argv[1])
number_of_paths = int(sys.argv[2])

# For each node get the number of paths
node_paths_tuple = []
graph.for_each_handle(lambda x: get_number_of_paths_per_node(x))

# Get the nodes through which all paths go through
nodes_to_consider = [t[0] for t in node_paths_tuple if t[1] == number_of_paths]

# Check that each path only traverses the node once
final_nodes = []
for node in nodes_to_consider:
    paths = get_path_support(graph, node)
    if len(set(paths)) == number_of_paths:
        final_nodes.append(node)

# Get the length of the final nodes
node_length_dict = dict()
for node in final_nodes:
    handle = graph.get_handle(node)
    node_length_dict[node] = graph.get_length(handle)

# Only print nodes with the maximum length
max_length = max(node_length_dict.values())
print("Nodes with maximum length of", max_length, "bp: ")
for item in node_length_dict.items():
    if item[1] == max_length:
        print(item[0])