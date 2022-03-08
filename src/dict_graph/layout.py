"""
References:
1. Buchheim, Christoph & Jünger, Michael & Leipert, Sebastian. (2002). Improving Walker's Algorithm to Run in
    Linear Time. 2528. 10.1007/3-540-36151-0_32.
2.
"""
from __future__ import annotations

import logging
import weakref
from typing import Optional, Union, Callable, Collection

from .draw import UID
from .utils import Tree

logger = logging.getLogger(__name__)


class LayoutTree:
    def __init__(
        self, tree, *, parent=None, sibling_index=0, level=0, level_limit=15,
    ):
        self._tree = tree
        if level < level_limit - 1:
            self.children = [
                LayoutTree(
                    c,
                    parent=self,
                    level=level + 1,
                    sibling_index=i,
                    level_limit=level_limit,
                )
                for i, c in enumerate(
                    tree.children.values()
                    if isinstance(tree.children, dict)
                    else tree.children
                )
            ]
        else:
            self.children = []

        self.sibling_index = sibling_index
        self.level = level

        self._parent = weakref.ref(parent) if parent else None
        self._thread = None

        # Page 8: this is not correct for rightmost children, but we only need the correct value when v+ is added
        self._ancestor = weakref.ref(self)

        # x- and y-coordinate
        self.x = 0.0  # preliminary position
        self.y = float(level)

        # modifier: to be added to all preliminary x in the subtree of v, except for v itself
        self.mod = 0.0

        # see Page 10
        # shift: amount to move subtree to the right to avoid conflict with left neighbour (NOT always left sibling)
        # change: decrease of shift per subtree
        self.change = self.shift = 0.0

    def __repr__(self):
        return f"{self._tree.value} id={id(self)} x={self.x:.2f} y={self.y:.2f} sibling_index={self.sibling_index}"

    @property
    def parent(self) -> Optional["LayoutTree"]:
        return self._parent and self._parent()

    @property
    def ancestor(self):
        return self._ancestor()

    @ancestor.setter
    def ancestor(self, tree: "LayoutTree") -> None:
        self._ancestor = weakref.ref(tree)

    @property
    def thread(self) -> Optional["LayoutTree"]:
        return self._thread and self._thread()

    @thread.setter
    def thread(self, tree: "LayoutTree"):
        self._thread = weakref.ref(tree)

    @property
    def left_sibling(self) -> Optional["LayoutTree"]:
        if self.parent and self.sibling_index > 0:
            return self.parent.children[self.sibling_index - 1]
        return None

    @property
    def leftmost_sibling(self) -> Optional["LayoutTree"]:
        if self.parent:
            return self.parent.children[0]
        return None

    @property
    def is_leftmost_sibling(self) -> bool:
        return self.left_sibling is None

    @property
    def is_leaf(self) -> bool:
        return not self.children

    @property
    def next_left(self) -> Optional["LayoutTree"]:
        """ node of the left contour in the next level"""
        return self.thread if self.is_leaf else self.children[0]

    @property
    def next_right(self) -> Optional["LayoutTree"]:
        """ node on the right contour in the next level"""
        return self.thread if self.is_leaf else self.children[-1]

    def boundary_box(self):
        if self.is_leaf:
            return self.x, self.x, self.y, self.y
        else:
            x0 = x1 = self.x
            y0 = y1 = self.y
            for child in self.children:
                cx0, cx1, cy0, cy1 = child.boundary_box()
                x0 = min(x0, cx0)
                x1 = max(x1, cx1)
                y0 = min(y0, cy0)
                y1 = max(y1, cy1)
            return x0, x1, y0, y1


def extract_tree_layout(
    layout_tree: Union[LayoutTree, list[LayoutTree]],
    *,
    key: Callable[[LayoutTree], UID] = None,
) -> tuple[
    dict[UID, str],
    dict[UID, str],
    list[tuple[UID, UID]],
    dict[UID, tuple[float, float]],
]:
    """
    Extract branch and leaf nodes' information, as well as the edges and positions, from the given layout tree(s)
    The given `layout_tree` can be a list to handle scenarios where the trees don't have a shared root.

    :param layout_tree: A instance of LayoutTree, or a list of LayoutTree instances
    :param key: An optional function to calculate the unique ID of a tree node. By default, the 'hash' is used
    :return: branch and leaf nodes as {UID: label}, edges as [(UID_0, UID_1), ...], and positions as {UID: (x, y)}
    """
    branches = {}
    leaves = {}
    positions = {}
    edges = []

    if key is not None:
        if not callable(key):
            raise TypeError(f"'key' is expected to be a callable, but got {type(key)}")
    else:
        key = hash

    if isinstance(layout_tree, LayoutTree):
        q = [layout_tree]
    elif isinstance(layout_tree, Collection):
        q = layout_tree
    else:
        raise TypeError(
            f"Expect 'layout_tree' to be a instance or a collection of instances of 'LayoutTree', but got {type(layout_tree)}"
        )

    while q:
        next_q = []
        for l_tree in q:
            curr_key = key(l_tree)
            branch_or_leave = leaves if l_tree._tree.is_leaf else branches
            branch_or_leave[curr_key] = l_tree._tree.value
            positions[curr_key] = l_tree.x, l_tree.y

            for child in l_tree.children:
                edges.append((curr_key, key(child)))
                next_q.append(child)

        q = next_q
    return branches, leaves, edges, positions


def render_tree(
    tree: Tree,
    *,
    keep_root=True,
    depth_limit=15,
    rankdir="TB",
    key: Callable[[LayoutTree], UID] = None,
):
    """
    Computes elements, edges and their positions to draw. The layout is hierarchical from top to bottom.

    :param tree: a tree structure. The value of each tree node will be used as its label
    :param keep_root: By default, True. If False, the root node will be ignored. This is useful for scenarios where
                    having the root node is merely for the purpose of structural integrity and thus should be ignored.
    :param depth_limit: maximum depth of the graph. By default, 15
    :param rankdir: Direction of the graph layout. By default, TB, meaning from top to bottom.
                    Available options are ['TB', 'BT', 'LR', 'RL', 'RADIAL']
    :param key: An optional function to calculate the unique ID of a tree node. By default, the 'hash' is used
    :return: branch and leaf nodes as {UID: label}, edges as [(UID_0, UID_1), ...], and positions as {UID: (x, y)}
    """
    from .buchheim import buchheim

    layout_tree = LayoutTree(
        tree, level_limit=depth_limit, level=0 if keep_root else -1
    )

    # use Buchheim algorithm to compute the layout
    bbox = buchheim(layout_tree)
    logger.debug(
        f"Boundary box computed using Buchheim algorithm: (x_min={bbox[0]:.2f}, x_max={bbox[1]:.2f}, y_min={bbox[2]:.2f}, y_max={bbox[3]:.2f}"
    )

    branches, leaves, edges, positions = extract_tree_layout(
        layout_tree if keep_root else layout_tree.children, key=key
    )

    if rankdir != "BT":
        positions = _transform_axes(positions, rankdir)

    return branches, leaves, edges, positions


def _transform_axes(
    positions: dict[UID, tuple[float, float]], rankdir: str
) -> dict[UID, tuple[float, float]]:
    """
    Transform axes of the given positions according to 'rankdir'.
    The given positions are assumed to have layout of from top to bottom.

    :param positions: x- and y-coordinates of nodes
    :param rankdir: graph layout direction.
    :return: transformed x- and y-coordinates of nodes
    """
    import numpy as np

    xy = np.array([v for v in positions.values()])

    if rankdir == "TB":
        xy[:, 1] *= -1.0
    elif rankdir == "LR":
        xy = np.dot(xy, np.array([[0, -1], [1, 0]]))
    elif rankdir == "RL":
        xy = np.dot(xy, np.array([[0, -1], [-1, 0]]))
    elif rankdir == "RADIAL":
        x0, y0 = np.min(xy, axis=0)
        x1, y1 = np.max(xy, axis=0)
        r0 = 0.2 * (
            y1 - y0
        )  # minimum radius to avoid placing two nodes at the same position
        theta_unit = (
            2 * np.pi / (np.ptp(xy[:, 0]) + 1.0)
        )  # plus 1 to avoid placing two nodes at the same position

        def radial(r):
            x, y = r
            r = y - y0 + r0
            theta = (x - x0) * theta_unit
            return r * np.cos(theta), r * np.sin(theta)

        xy = np.apply_along_axis(radial, axis=1, arr=xy)

    return {k: tuple(xy[i, :]) for i, k in enumerate(positions)}
