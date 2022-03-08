import logging
from typing import List

import click
import matplotlib.pyplot as plt

from dict_graph.draw import paint_tree
from dict_graph.layout import render_tree
from dict_graph.utils import build_tree, preprocess_word_list

logger = logging.getLogger(__name__)


def draw_dictionary_graph(
    words: List[str],
    *,
    use_raw=False,
    depth_limit=15,
    rankdir="TB",
    ax=None,
    branch_size=200,
    leaf_size=200,
    branch_color="c",
    leaf_color="r",
    branch_shape="o",
    leaf_shape="o",
    other_node_kwargs=None,
    other_label_kwargs=None,
    arrowstyle="-|>",
    connectionstyle="arc3",
    mutation_scale=10,
    other_edge_kwargs=None,
    save_file=None,
    dpi=None,
    figsize=None,
):
    """
    Plot a graph representing of Oxford dictionary for the given words.

    This function uses matplotlib to draw the graph. Specifically, it uses
        1. 'matplotlib.axes.Axes.scatter' for drawing branch and leaf nodes
        2. 'matplotlib.axes.Axes.text' for adding labels to the nodes
        3. 'matplotlib.patches.FancyArrowPatch' for adding connections between nodes

    :param words: a list of words
    :param use_raw: By default True. If True, the given words will be used directly to build the graph.
                    Otherwise, only the non-empty words will be used after transformed to upper case and sorted
    :param depth_limit: By default 15. This is the max levels in the graph
    :param rankdir: Direction of the graph layout. By default, TB, meaning from top to bottom.
                    Available options are ['TB', 'BT', 'LR', 'RL', 'RADIAL'].
    :param ax: An optional matplotlib axe to plot the graph in. If None
    :param branch_size: size of a branch node. By default, 200
    :param leaf_size: size of a leaf node. By default, 200. Note that a leaf merely means a word ends at it.
    :param branch_color: color of a branch node. By default, cyan
    :param leaf_color: color of a leaf node. By default, red
    :param branch_shape: shape of a branch node. By default, cycle
    :param leaf_shape: shape of a leaf node. By default, cycle
    :param other_node_kwargs: other attributes to apply to all nodes. It will be passed to 'matplotlib.axes.Axes.scatter'
    :param other_label_kwargs:  A dict of properties to pass to 'matplotlib.axes.Axes.text'
    :param arrowstyle: The arrow style with which the arrow in the directed egdes is drawn.
                        It will be passed to 'matplotlib.patches.FancyArrowPatch'
    :param connectionstyle: The connection style with which edges are drawn.
                        It will be passed to 'matplotlib.patches.FancyArrowPatch'
    :param mutation_scale: Value with which attribute of arrowstyle will be scaled.
                        It will be passed to 'matplotlib.patches.FancyArrowPatch'
    :param other_edge_kwargs: A dict of properties to pass to matplotlib.patches.FancyArrowPatch.
                        It will be passed to 'matplotlib.patches.FancyArrowPatch'
    :param save_file: A path or a file-like object to store the image in. If None, the image will be displayed
    :param dpi: Resolution in dots per inch. Used only when 'outfile' is specified
    :param figsize: Image width and height in inches. Used only when 'outfile' is specified
    :return: None
    """
    if not use_raw:
        words = preprocess_word_list(words)

    tree = build_tree(words)

    branches, leaves, edges, positions = render_tree(
        tree, depth_limit=depth_limit, rankdir=rankdir, keep_root=False
    )

    # transform x- and y-axes

    paint_tree(
        branches,
        leaves,
        edges,
        positions,
        ax=ax,
        branch_size=branch_size,
        leaf_size=leaf_size,
        branch_color=branch_color,
        leaf_color=leaf_color,
        branch_shape=branch_shape,
        leaf_shape=leaf_shape,
        other_node_kwargs=other_node_kwargs,
        other_label_kwargs=other_label_kwargs,
        arrowstyle=arrowstyle,
        connectionstyle=connectionstyle,
        mutation_scale=mutation_scale,
        other_edge_kwargs=other_edge_kwargs,
    )

    if save_file is not None:
        if figsize is not None:
            fig = plt.gcf()
            fig.set_size_inches(*figsize)
        plt.savefig(save_file, dpi=dpi, bbox_inches="tight")
    else:
        plt.show()


@click.command()
@click.option(
    "--infile",
    type=click.File("r"),
    nargs=1,
    help="File to read the words from. Words are read line-by-line",
)
@click.option(
    "--use_raw",
    type=bool,
    default=True,
    help="Whether to use the given words directly to draw the graph. If False, only non-empty words will be used after being transformed to upper case and sorted",
)
@click.option(
    "--rankdir",
    type=click.Choice(["TB", "BT", "LR", "RL", "RADIAL"], case_sensitive=False),
    default="TB",
    help="Graph layout direction. For example 'TB' means from top to bottom, 'LR' means from left to right",
)
@click.option(
    "--outfile",
    type=click.File("wb"),
    help="Optional path to save the graph using 'matplotlib.pyplot.savefig'",
)
@click.option(
    "--dpi",
    type=float,
    help="Resolution in dots per inch. Used only when 'outfile' is specified",
)
@click.option(
    "--figsize",
    type=float,
    nargs=2,
    help="Image width and height in inches. Used only when 'outfile' is specified",
)
def cli(infile, use_raw, rankdir, outfile, dpi, figsize):
    """
    Reads words from a file and converts to a graph representing the Oxford dictionary.
    Finer control of the graph is available by using `draw_dict.draw_dictionary_graph` function
    """
    words = infile.read().splitlines()
    click.echo(f"words: {words}")
    click.echo(f"rankdir: {rankdir}")
    click.echo(f"save to {outfile}")
    draw_dictionary_graph(
        words,
        use_raw=use_raw,
        rankdir=rankdir,
        save_file=outfile,
        dpi=dpi,
        figsize=figsize,
    )
