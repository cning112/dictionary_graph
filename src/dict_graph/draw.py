from __future__ import annotations

from collections import ChainMap
from typing import TypeVar

import matplotlib as mpl

UID = TypeVar("UID", str, int)


def paint_tree(
    branches: dict[UID, str],
    leaves: dict[UID, str],
    edges: list[tuple[UID, UID]],
    positions: dict[UID, tuple[float, float]],
    *,
    ax=None,
    branch_size=200,
    leaf_size=200,
    branch_color="cyan",
    leaf_color="red",
    branch_shape="o",
    leaf_shape="o",
    other_node_kwargs=None,
    other_label_kwargs=None,
    arrowstyle="-|>",
    connectionstyle="arc3",
    mutation_scale=10,
    other_edge_kwargs=None,
) -> None:
    """
    Draws a graph representing a tree with the given elements.
    This function uses matplotlib to draw the graph. Specifically, it uses
        1. 'matplotlib.axes.Axes.scatter' for drawing branch and leaf nodes
        2. 'matplotlib.axes.Axes.text' for adding labels to the nodes
        3. 'matplotlib.patches.FancyArrowPatch' for adding connections between nodes

    Note that this function won't display the graph in a window or save to a file. You need to call
    `matplotlib.pyplot.show()` to display the graph in a window or `matplotlib.pyplot.savefig()` save it to a file.

    :param branches: A dict representing branch nodes where the keys are unique IDs and the values are labels.
    :param leaves: Same as the branches except that they are drawn with different properties
    :param edges: A list of two-element tuples representing directed connections between nodes
    :param positions: A dict where keys are nodes' unique IDs and values ar (x, y)-coordinates
        :param ax: An optional matplotlib axe to plot the graph in. If None
    :param branch_size: size of a branch node. By default, 200
    :param leaf_size: size of a leaf node. By default, 200
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
    """
    import matplotlib.pyplot as plt
    import numpy as np

    if ax is None:
        ax = plt.gca()

    # branches
    xy = np.array([positions[n] for n in branches])
    ax.scatter(
        xy[:, 0],
        xy[:, 1],
        s=branch_size,
        c=branch_color,
        marker=branch_shape,
        **(other_node_kwargs or {}),
    )

    # leaves
    xy = np.array([positions[n] for n in leaves])
    ax.scatter(
        xy[:, 0],
        xy[:, 1],
        s=leaf_size,
        c=leaf_color,
        marker=leaf_shape,
        **(other_node_kwargs or {}),
    )

    # labels
    for name, label in ChainMap(branches, leaves).items():
        ax.text(
            *positions[name],
            str(label),
            horizontalalignment="center",
            verticalalignment="center",
            **(other_label_kwargs or {}),
        )

    # edges
    def to_marker_edge(marker_size, marker):
        # marker_size is in point**2
        if marker in "s^>v<d":  # `large` markers need extra space
            return np.sqrt(2 * marker_size) / 2
        else:
            return np.sqrt(marker_size) / 2

    connection_style = mpl.patches.ConnectionStyle(connectionstyle)
    shrink_node = to_marker_edge(branch_size, branch_shape)
    shrink_leaf = to_marker_edge(leaf_size, leaf_shape)

    for n0, n1 in edges:
        # TODO: This may be slow.
        # Using PatchCollection doesn't help due to an known issue: https://github.com/matplotlib/matplotlib/issues/2341
        arrow = mpl.patches.FancyArrowPatch(
            positions[n0],
            positions[n1],
            animated=False,
            aa=False,
            arrowstyle=arrowstyle,
            mutation_scale=mutation_scale,
            connectionstyle=connection_style,
            shrinkA=shrink_leaf if n0 in leaves else shrink_node,
            shrinkB=shrink_leaf if n1 in leaves else shrink_node,
            zorder=1,
            **(other_edge_kwargs or {}),
        )
        ax.add_patch(arrow)

    ax.set_axis_off()
    ax.tick_params(
        axis="both",
        which="both",
        bottom=False,
        left=False,
        labelbottom=False,
        labelleft=False,
    )

    plt.autoscale()
    plt.draw_if_interactive()
