#!/usr/bin/env python3.7
from typing import Callable, Optional
import token

from bowler import Query, LN, Capture, Filename

from fissix.pygram import python_symbols
from fissix.pytree import Node, Leaf
from fissix.fixer_util import Call, Name, String, Comma

ModifyFn = Callable[[LN, Capture, Filename], Optional[LN]]


def modify_attr(node: LN, capture: Capture, filename: Filename) -> Optional[LN]:
    node.replace(
        Call(
            Name("getattr"),
            args=[
                capture["obj"].clone(),
                Comma(),
                String(" "),
                String('"' + capture["attr"].value + '"'),
            ],
        )
    )


def main():
    (
        Query("fake.py")
        .select(
            """
            power<
                obj=NAME
                trailer<
                    '.' attr=NAME
                >
            >
            """
        )
        .modify(modify_attr)
        .diff()
    )


if __name__ == "__main__":
    main()
