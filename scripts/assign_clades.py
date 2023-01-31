#!/usr/bin/env python3
import argparse
from augur.utils import annotate_parents_for_tree, read_node_data, read_tree, write_json
import json


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--tree", required=True, help="Newick tree with named internal nodes")
    parser.add_argument("--mutations", required=True, help="Node data JSON file with amino acid mutations per node in the given tree")
    parser.add_argument("--frequencies", required=True, help="Auspice side car JSON for tip frequencies with values calculated per internal node")
    parser.add_argument("--sites", type=int, nargs="+", required=True, help="HA1 positions to consider for clade assignment (e.g., Koel sites)")
    parser.add_argument("--minimum-frequency", type=float, default=0.1, help="minimum frequency a clade must have reached at least once globally to get a clade assignment")
    parser.add_argument("--output", required=True, help="Node data JSON output file with clade assignments by amino acid mutations at the given sites")

    args = parser.parse_args()

    # Load tree.
    tree = read_tree(args.tree)
    tree = annotate_parents_for_tree(tree)

    # Load mutations.
    mutations_by_node = read_node_data(args.mutations, skip_validation=True)["nodes"]

    # Load frequencies.
    with open(args.frequencies, "r", encoding="utf-8") as fh:
        frequencies_by_node = json.load(fh)

    # Traverse tree in preorder to find nodes with mutations at the requested
    # sites above a minimum frequency.
    for node in tree.find_clades(order="preorder"):
        # Assign a default clade membership to handle early nodes that do not
        # have mutations at requested sites.
        node.clade_membership = "unassigned"

        if (node.name in mutations_by_node and
            "HA1" in mutations_by_node[node.name]["aa_muts"]):
            node_mutations = mutations_by_node[node.name]["aa_muts"]["HA1"]
            clade_mutations = {}
            for node_mutation in node_mutations:
                site = int(node_mutation[1:-1])
                mutation = node_mutation[-1]
                if site in args.sites:
                    clade_mutations[site] = mutation

            # Check whether this clade has mutations at the requested sites and
            # ever circulated above a minimum frequency threshold.
            if len(clade_mutations) > 0 and max(frequencies_by_node[node.name]["frequencies"]) >= args.minimum_frequency:
                # Store the "clade annotation" to represent the first node in
                # the tree with this clade name. Store "clade membership" for
                # all nodes that descend from that clade including this first
                # one.
                clade_name = "/".join([f"{site}{mutation}" for site, mutation in clade_mutations.items()])
                node.clade_annotation = clade_name
                node.clade_membership = clade_name
            else:
                node.clade_membership = node.parent.clade_membership

    # Save clade annotations in node data JSON format.
    node_data = {}
    for node in tree.find_clades():
        node_data[node.name] = {
            "clade_membership": node.clade_membership
        }

        if hasattr(node, "clade_annotation"):
            node_data[node.name]["clade_annotation"] = node.clade_annotation

    write_json({"nodes": node_data}, args.output)
