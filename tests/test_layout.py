import numpy as np
import pytest

from dict_graph.layout import LayoutTree, extract_tree_layout, render_tree
from dict_graph.utils import build_tree


def key_of_tree(tree: LayoutTree):
    if tree.parent is None:
        return str(tree.sibling_index)

    return f"{key_of_tree(tree.parent)}{tree.sibling_index}"


@pytest.mark.parametrize(
    "inputs, expected",
    [
        (
            {
                "words": ["ab", "ac", "abcd", "abce"],
                "depth_limit": 10,
                "keep_root": False,
                "rankdir": "TB",
            },
            {
                "branches": {"00": "a", "0000": "c",},
                "leaves": {"000": "b", "001": "c", "00000": "d", "00001": "e"},
                "edges": [
                    ("00", "000"),
                    ("00", "001"),
                    ("000", "0000"),
                    ("0000", "00000"),
                    ("0000", "00001"),
                ],
                "positions": {
                    "00": (1.0, 0.0),
                    "000": (0.5, -1.0),
                    "001": (1.5, -1.0),
                    "0000": (0.5, -2.0),
                    "00000": (0.0, -3.0),
                    "00001": (1.0, -3.0),
                },
            },
        ),
        (
            {
                "words": ["ab", "ac", "abcd", "abce"],
                "depth_limit": 10,
                "keep_root": False,
                "rankdir": "LR",
            },
            {
                "branches": {"00": "a", "0000": "c",},
                "leaves": {"000": "b", "001": "c", "00000": "d", "00001": "e"},
                "edges": [
                    ("00", "000"),
                    ("00", "001"),
                    ("000", "0000"),
                    ("0000", "00000"),
                    ("0000", "00001"),
                ],
                "positions": {
                    "00": (0.0, -1.0),
                    "000": (1.0, -0.5),
                    "001": (1.0, -1.5),
                    "0000": (2.0, -0.5),
                    "00000": (3.0, -0.0),
                    "00001": (3.0, -1.0),
                },
            },
        ),
        (
            {
                "words": ["ab", "ac", "abcd", "abce"],
                "depth_limit": 10,
                "keep_root": False,
                "rankdir": "RL",
            },
            {
                "branches": {"00": "a", "0000": "c",},
                "leaves": {"000": "b", "001": "c", "00000": "d", "00001": "e"},
                "edges": [
                    ("00", "000"),
                    ("00", "001"),
                    ("000", "0000"),
                    ("0000", "00000"),
                    ("0000", "00001"),
                ],
                "positions": {
                    "00": (0.0, -1.0),
                    "000": (-1.0, -0.5),
                    "001": (-1.0, -1.5),
                    "0000": (-2.0, -0.5),
                    "00000": (-3.0, -0.0),
                    "00001": (-3.0, -1.0),
                },
            },
        ),
        (
            {
                "words": ["aba", "abb", "abc", "aca", "acb", "acc"],
                "depth_limit": 10,
                "keep_root": False,
                "rankdir": "RADIAL",
            },
            {
                "branches": {"00": "a", "000": "b", "001": "c"},
                "leaves": {
                    "0000": "a",
                    "0001": "b",
                    "0002": "c",
                    "0010": "a",
                    "0011": "b",
                    "0012": "c",
                },
                "edges": [
                    ("00", "000"),
                    ("00", "001"),
                    ("000", "0000"),
                    ("000", "0001"),
                    ("000", "0002"),
                    ("001", "0010"),
                    ("001", "0011"),
                    ("001", "0012"),
                ],
                "positions": {
                    "00": (-0.346, 0.2),
                    "000": (0.7, 1.212),
                    "0000": (2.4, 0.0),
                    "0001": (1.2, 2.0785),
                    "0002": (-1.2, 2.0785),
                    "001": (-0.70, -1.212),
                    "0010": (-2.4, 0),
                    "0011": (-1.20, -2.078),
                    "0012": (1.20, -2.078),
                },
            },
        ),
        (
            {
                "words": ["ab", "ac", "abcd", "abce"],
                "depth_limit": 10,
                "keep_root": False,
                "rankdir": "BT",
            },
            {
                "branches": {"00": "a", "0000": "c",},
                "leaves": {"000": "b", "001": "c", "00000": "d", "00001": "e"},
                "edges": [
                    ("00", "000"),
                    ("00", "001"),
                    ("000", "0000"),
                    ("0000", "00000"),
                    ("0000", "00001"),
                ],
                "positions": {
                    "00": (1.0, 0.0),
                    "000": (0.5, 1.0),
                    "001": (1.5, 1.0),
                    "0000": (0.5, 2.0),
                    "00000": (0.0, 3.0),
                    "00001": (1.0, 3.0),
                },
            },
        ),
        (
            {
                "words": ["ab", "ac", "abcd", "abce"],
                "depth_limit": 3,
                "keep_root": True,
                "rankdir": "BT",
            },
            {
                "branches": {"0": "", "00": "a"},
                "leaves": {"000": "b", "001": "c"},
                "edges": [("0", "00"), ("00", "000"), ("00", "001")],
                "positions": {
                    "0": (0.5, 0.0),
                    "00": (0.5, 1.0),
                    "000": (0.0, 2.0),
                    "001": (1.0, 2.0),
                },
            },
        ),
        (
            {
                "words": [
                    "ab",
                    "ac",
                    "bd",
                    "be",
                    "bf",
                    "bg",
                    "bfa",
                    "bfb",
                    "bfc",
                    "bfd",
                    "bfe",
                    "c",
                    "dxa",
                    "dxb",
                    "dxc",
                    "dxd",
                ],
                "depth_limit": 10,
                "keep_root": False,
                "rankdir": "BT",
            },
            {
                "branches": {"00": "a", "01": "b", "03": "d", "030": "x"},
                "leaves": {
                    "000": "b",
                    "001": "c",
                    "010": "d",
                    "011": "e",
                    "012": "f",
                    "013": "g",
                    "0120": "a",
                    "0121": "b",
                    "0122": "c",
                    "0123": "d",
                    "0124": "e",
                    "02": "c",
                    "0300": "a",
                    "0301": "b",
                    "0302": "c",
                    "0303": "d",
                },
                "edges": [
                    ("00", "000"),
                    ("00", "001"),
                    ("01", "010"),
                    ("01", "011"),
                    ("01", "012"),
                    ("01", "013"),
                    ("03", "030"),
                    ("012", "0120"),
                    ("012", "0121"),
                    ("012", "0122"),
                    ("012", "0123"),
                    ("012", "0124"),
                    ("030", "0300"),
                    ("030", "0301"),
                    ("030", "0302"),
                    ("030", "0303"),
                ],
                "positions": {
                    "00": (0.5, 0.0),
                    "000": (0.0, 1.0),
                    "001": (1.0, 1.0),
                    "01": (3.5, 0.0),
                    "010": (2.0, 1.0),
                    "011": (3.0, 1.0),
                    "012": (4.0, 1.0),
                    "013": (5.0, 1.0),
                    "0120": (2.0, 2.0),
                    "0121": (3.0, 2.0),
                    "0122": (4.0, 2.0),
                    "0123": (5.0, 2.0),
                    "0124": (6.0, 2.0),
                    "02": (6.0, 0.0),
                    "03": (8.5, 0.0),
                    "030": (8.5, 1.0),
                    "0300": (7.0, 2.0),
                    "0301": (8.0, 2.0),
                    "0302": (9.0, 2.0),
                    "0303": (10.0, 2.0),
                },
            },
        ),
    ],
)
def test_render_tree(inputs, expected):
    tree = build_tree(inputs["words"])
    branches, leaves, edges, positions = render_tree(
        tree,
        keep_root=inputs["keep_root"],
        depth_limit=inputs["depth_limit"],
        key=key_of_tree,
        rankdir=inputs["rankdir"],
    )

    assert branches == expected["branches"]
    assert leaves == expected["leaves"]
    assert edges == expected["edges"]
    assert positions.keys() == expected["positions"].keys()

    positions = np.array([positions[k] for k in sorted(positions)])
    expected_positions = np.array(
        [expected["positions"][k] for k in sorted(expected["positions"])]
    )
    assert np.allclose(positions, expected_positions, rtol=1e-5, atol=1e-3)
