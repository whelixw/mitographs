import networkx as nx
from Bio import SeqIO
from Bio.Seq import Seq
from collections import defaultdict
import os
import sys
import argparse

def parse_vg_gfa(gfa_file):
    graph = nx.DiGraph()
    node_sequences = {}
    paths = defaultdict(list)

    with open(gfa_file, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if parts[0] == 'S':  # Segment
                node_id = parts[1]
                sequence = parts[2]
                node_sequences[node_id] = sequence
                graph.add_node(node_id, sequence=sequence)
            elif parts[0] == 'L':  # Link
                from_node = parts[1]
                to_node = parts[3]
                graph.add_edge(from_node, to_node)
            elif parts[0] == 'P':  # Path
                path_name = parts[1]
                path_nodes = parts[2].split(',')
                paths[path_name].extend(path_nodes)

    return graph, node_sequences, paths

def find_longest_shared_node(paths, node_sequences):
    node_lengths = {node: len(seq) for node, seq in node_sequences.items()}
    # Strip orientation symbols from node identifiers in paths
    stripped_paths = {path: [node.rstrip('+-') for node in nodes] for path, nodes in paths.items()}
    shared_nodes = set.intersection(*map(set, stripped_paths.values()))

    if not shared_nodes:
        raise ValueError("No shared nodes found in all paths")

    longest_shared_node = max(shared_nodes, key=lambda node: node_lengths[node])
    return longest_shared_node, node_sequences[longest_shared_node]

def rotate_path_to_node(path, node):
    stripped_path = [n.rstrip('+-') for n in path]
    node_index = stripped_path.index(node)

    if args.orient and path[node_index].endswith('-'):
        #print("alll")
        path = path[::-1]
        #please fix this so i don't do it twice -.-
        stripped_path = [n.rstrip('+-') for n in path]
        node_index = stripped_path.index(node)
    return path[node_index:] + path[:node_index]

def rebuild_fasta(fasta_files, node_sequences, rotated_paths, orient, output_dir):
    flag = False
    os.makedirs(output_dir, exist_ok=True)

    for fasta_file in fasta_files:
        fasta_basename = os.path.basename(fasta_file)[:-6]  # Remove the last 6 characters
        if fasta_basename not in rotated_paths:
            raise KeyError(f"Path {fasta_basename} not found in GFA paths.")

        output_file = os.path.join(output_dir, f"{fasta_basename}.fasta.rotated")
        with open(fasta_file, 'r') as input_handle, open(output_file, 'w') as output_handle:
            for record in SeqIO.parse(input_handle, "fasta"):
                new_seq = ""
                #print(rotated_paths[fasta_basename][0])
                for node in rotated_paths[fasta_basename]:
                    node_id = node.rstrip('+-')
                    node_seq = node_sequences[node_id]
                    if int(node_id) % 200 == 0:
                        flag = True
                    else:
                        flag = False
                    if orient and node.endswith('-'):
                        #print("node is negative")
                        #if len(node_seq) > 10:
                            #print(node_seq)
                        #node_seq = str(Seq(node_seq).reverse_complement())
                        #node_seq = node_seq[::-1]
                        pass
                        #print(node_seq)
                    new_seq += node_seq
                record.seq = Seq(new_seq)
                SeqIO.write(record, output_handle, "fasta")

def main(gfa_file, fasta_files, orient, output_dir):
    graph, node_sequences, paths = parse_vg_gfa(gfa_file)
    longest_node, anchor_node_sequence = find_longest_shared_node(paths, node_sequences)

    # Rotate paths to start with the longest shared node
    rotated_paths = {path: rotate_path_to_node(nodes, longest_node) for path, nodes in paths.items()}

    # Build and save new FASTA sequences
    rebuild_fasta(fasta_files, node_sequences, rotated_paths, orient, output_dir)
    #rint(f"Rebuilt FASTA files using the longest shared node {longest_node} as the anchor. Files saved to 'rotated_fastas' directory.")
    print(f"Rotated FASTA files using the longest shared node {longest_node} ({anchor_node_sequence}) as the anchor.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rotate and rebuild FASTA files based on VG GFA paths.")
    parser.add_argument("gfa_file", help="The input GFA file.")
    parser.add_argument("fasta_files", nargs='+', help="The list of input FASTA files.")
    parser.add_argument("--orient", action="store_true", help="Use node orientation from paths to orient the FASTA sequences.")
    parser.add_argument("--output_dir", default="rotated_fastas", help="The output directory for the rotated FASTA files.")
    args = parser.parse_args()

    main(args.gfa_file, args.fasta_files, args.orient, args.output_dir)
