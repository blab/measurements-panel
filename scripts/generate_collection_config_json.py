#!/usr/bin/env python3
import argparse
from augur.utils import read_tree
from augur.validate import measurements_collection_config
import json
import pandas as pd


def get_y_position_by_node(tree):
    """Create a mapping of each node to its vertical position. Dict of {clade:
    y-coord}. Coordinates are negative, and integers for tips.

    We use the y position layout function from BioPython [1]. This function is
    hidden inside the top-level draw function, so we cannot reuse it.
    [1] https://github.com/biopython/biopython/blob/d1d3c0d6ab33de12057201e09eb48bdb1964521a/Bio/Phylo/_utils.py#L471-L495

    Parameters
    ----------
    tree : Bio.Phylo.BaseTree
        a tree from BioPython

    Returns
    -------
    dict
        mapping of BioPython Clade instances to y-axis coordinates

    """
    maxheight = tree.count_terminals()

    # Rows are defined by the tips
    heights = {
        tip: maxheight - i for i, tip in enumerate(reversed(tree.get_terminals()))
    }

    # Internal nodes: place at midpoint of children
    def calc_row(clade):
        for subclade in clade:
            if subclade not in heights:
                calc_row(subclade)
        # Closure over heights
        heights[clade] = (
            heights[clade.clades[0]] + heights[clade.clades[-1]]
        ) / 2.0

    if tree.root.clades:
        calc_row(tree.root)

    return heights


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--tree", required=True, help="Newick tree with named internal nodes from augur refine produced by the same build as the collection TSV. Used to order reference strains and clades by y-axis position in the phylogeny.")
    parser.add_argument("--collection", required=True, help="collection TSV that will be passed to augur measurements export")
    parser.add_argument("--groupings", nargs="+", required=True, help="grouping columns in the given TSV for which an order will be generated")
    parser.add_argument("--output", required=True, help="configuration JSON for measurements export with ordering specified for the requested grouping")

    args = parser.parse_args()

    # Read tree.
    tree = read_tree(args.tree)

    # Get y-axis positions per node in the tree and convert to positions per tip
    # name.
    y_axis_positions_per_node = get_y_position_by_node(tree)
    y_axis_positions_per_tip_name = {
        tip.name: position
        for tip, position in y_axis_positions_per_node.items()
        if tip.is_terminal()
    }

    # Read collection.
    collection_df = pd.read_csv(args.collection, sep="\t", usecols=args.groupings + ["reference_date", "clade_reference"])

    # Map y-axis positions in the phylogeny to reference strains.
    collection_df["y_axis_position_in_phylogeny"] = collection_df["reference_strain"].map(y_axis_positions_per_tip_name)

    # # Find maximum y-axis position for reference strains within each clade.
    # max_y_axis_position_by_reference_clade = collection_df.groupby("clade_reference")["y_axis_position_in_phylogeny"].max().reset_index().rename(
    #     columns={"y_axis_position_in_phylogeny": "max_y_axis_position_in_phylogeny"}
    # )

    # # Annotate max y-axis position per clade to collection.
    # collection_df = collection_df.merge(
    #     max_y_axis_position_by_reference_clade,
    #     on="clade_reference",
    #     how="left",
    # )

    # Sort collection by y-axis position.
    sorted_df = collection_df.sort_values(
        "y_axis_position_in_phylogeny",
        ascending=False,
    )

    # Extract sorted values for each grouping column.
    groupings_config = []
    for grouping in args.groupings:
        # Skip sorting of "source" values by clade, since it doesn't make sense.
        # Omitting the "order" key from its config also demonstrates how the
        # default ordering by record count works.
        if grouping == "source":
            groupings_config.append({
                "key": grouping,
            })
        else:
            sorted_grouping_values = sorted_df[grouping].drop_duplicates().tolist()
            groupings_config.append({
                "key": grouping,
                "order": sorted_grouping_values,
            })

    # Build the configuration JSON entry for the requested grouping.
    config = {
        "groupings": groupings_config,
    }

    # Save configuration JSON.
    with open(args.output, "w", encoding="utf-8") as oh:
        json.dump(config, oh)

    # Validate configuration JSON.
    measurements_collection_config(args.output)
