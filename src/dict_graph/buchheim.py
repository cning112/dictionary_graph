from __future__ import annotations

from .layout import LayoutTree


def buchheim(layout_tree: LayoutTree) -> tuple[float, float, float, float]:
    """
    Use Buchheim algorithm to compute the layout of the given tree structure.
    Adjustment to x- and y-coordinates are made to each LayoutTree node in-place.

    :param layout_tree: A LayoutTree instance which is the root of the tree
    :return: Boundary box of the computed layout: (x_min, x_max, y_min, y_max)
    """
    _first_walk(layout_tree)
    _second_walk(layout_tree)
    return layout_tree.boundary_box()


def _first_walk(root: LayoutTree, *, dx=1.0):
    """
    Transverse bottom-top the tree rooted at 'root'
    """
    if root.is_leaf:
        if root.is_leftmost_sibling:
            root.x = 0.0  # this is why a second walk is needed
        else:
            root.x = root.left_sibling.x + dx

    else:

        # see Page 8 about what default_ancestor is used for
        default_ancestor = root.children[0]
        for w in root.children:
            _first_walk(w)
            default_ancestor = _apportion(w, default_ancestor, dx)
        _shift_tree(root)

        midpoint = (root.children[0].x + root.children[-1].x) * 0.5

        w = root.left_sibling
        if w:
            root.x = w.x + dx
            root.mod = root.x - midpoint
        else:
            root.x = midpoint

    return root


def _apportion(v: LayoutTree, default_ancestor: LayoutTree, dx: float):
    v_ = v.left_sibling
    if v_ is not None:
        # in buchheim notation:
        # i == inner; o == outer; r == right; l == left; r = +; l = -
        vir = vor = v
        vil = v_
        vol = v.leftmost_sibling
        sir = sor = v.mod
        sil = vil.mod
        sol = vol.mod

        # transverse right contour of the left subtree, and left contour of the right subtree
        while vil.next_right and vir.next_left:
            vil = vil.next_right
            vir = vir.next_left
            vol = vol.next_left
            vor = vor.next_right
            vor.ancestor = v
            shift = (vil.x + sil) - (vir.x + sir) + dx

            if shift > 0.0:  # conflicts
                ancestor_ = _ancestor(vil, v, default_ancestor)
                _shift_subtrees(ancestor_, v, shift)
                sir = sir + shift
                sor = sor + shift
            sil += vil.mod
            sir += vir.mod
            sol += vol.mod
            sor += vor.mod
        if vil.next_right and not vor.next_right:
            vor.thread = vil.next_right
            vor.mod += sil - sor
        else:
            if vir.next_left and not vol.next_left:
                vol.thread = vir.next_left
                vol.mod += sir - sol
            default_ancestor = v
    return default_ancestor


def _shift_subtrees(wl: LayoutTree, wr: LayoutTree, shift_amount: float) -> None:
    """
    Shift subtree rooted at wr to the right by shift_amount to avoid conflict with a subtree rooted at wl
    Note that any smaller subtrees between wl and wr is ignored here and will be adjusted in the final `shift_tree`

    :param wl: root of the subtree that the current subtree has a conflict with
    :param wr: root of the current subtree, i.e. the subtree to be moved to the right
    :param shift_amount: distance to move the subtree rooted at wr to the right
    :return: None, as we adjust wr.x and wr.mod in-place
    """
    # Buchheim notation: wl = w_, wr = w+
    # Page 5: Let subtrees be the number of children of the current root between w_ and w+ plus 1
    # meaning there are (subtrees-1) smaller subtrees between wl and wr
    subtrees = wr.sibling_index - wl.sibling_index
    # Page 9: Walker's idea: the i-th subtree to be moved by i*shift/subtrees
    # Improved by Buchheim et al.:
    #   * inc wr.shift by shift
    #   * dec wr.change by shift/subtrees
    #   * inc wl.change by shift/subtrees
    wr.shift += shift_amount
    wr.change -= shift_amount / subtrees
    wl.change += shift_amount / subtrees
    wr.x += shift_amount
    wr.mod += shift_amount


def _shift_tree(root: LayoutTree) -> None:
    """
    Execute all shift in a single traversal of all the children of root, from right to left
    See Page 10
    :param root: the parent of children whose subtrees were added and shifted individually
    :return: None, as we adjust children's x and mod attributes in-place
    """
    shift = change = 0.0
    for w in root.children[::-1]:
        w.x += shift
        w.mod += shift
        change += w.change
        shift += w.shift + change


def _ancestor(vil: LayoutTree, v: LayoutTree, default_ancestor: LayoutTree):
    # property for all nodes v_ on the right contour of the left subforest after each subtree addition:
    # if v_.ancestor is up-to-date, i.e., is a child of root, then it points the correct ancestor;
    # otherwise, the correct ancestor is defaultAncestor
    if vil.ancestor in v.parent.children:
        return vil.ancestor
    else:
        return default_ancestor


def _second_walk(
    root: LayoutTree, *, shift=0, start_y=None, dy=1.0, min_x=None
) -> float:
    """
    Second walk to adjust nodes to avoid any conflicts
    :param root: the root of the tree to adjust
    :param shift: the amount of distance to move to the right
    :param start_y: y-position of the root
    :param dy: increase in y-position per level
    :param min_x: the min x-position of subtrees rooted at root's left siblings
    :return: the min x-position of the trees rooted at root and its left siblings
    """
    root.x += shift

    if start_y is not None:
        root.y = start_y
    else:
        start_y = root.y

    if min_x is None or root.x < min_x:
        min_x = root.x

    for w in root.children:
        min_x = _second_walk(
            w, shift=shift + root.mod, start_y=start_y + dy, dy=dy, min_x=min_x
        )
    return min_x


# def _third_walk(root: LayoutTree, shift: float) -> None:
#     # Shifts every single node in the tree to the right by shift
#     root.x += shift
#     for c in root.children:
#         _third_walk(c, shift)
