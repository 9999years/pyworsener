#!/usr/bin/env python3.7
from typing import Callable, Optional
import token

from bowler import Query, LN, Capture, Filename, TOKEN, SYMBOL

from fissix.pygram import python_symbols
from fissix.pytree import Node, Leaf
from fissix.fixer_util import Call, Name, String, Comma, LParen, RParen, ArgList, Attr

ModifyFn = Callable[[LN, Capture, Filename], Optional[LN]]


def LBrace():
    return Leaf(token.LBRACE, "[")


def RBrace():
    return Leaf(token.RBRACE, "]")


def Plus():
    return Leaf(token.PLUS, "+")


def TupleNode(*args):
    parts = []
    for arg in args:
        parts.append(arg)
        parts.append(Comma())
    return Node(SYMBOL.atom, [LParen(), *parts, RParen()])


def ListNode(*args):
    parts = []
    for arg in args:
        parts.append(arg)
        parts.append(Comma())
    return Node(SYMBOL.atom, [LBrace(), *parts, RBrace()])


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


def filter_dict_literal(node: LN, capture: Capture, filename: Filename) -> bool:
    return not any(it.type == SYMBOL.comp_for for it in capture.get("body"))


def modify_dict_literal(node: LN, capture: Capture, filename: Filename) -> Optional[LN]:
    toks = iter(capture.get("body"))
    items = []
    while True:
        try:
            tok = next(toks)
            if tok.type == TOKEN.DOUBLESTAR:
                body = next(toks)
                items.append(body.clone())
            else:
                next(toks)  # colon
                value = next(toks)
                if items and isinstance(items[-1], list):
                    items[-1].append(TupleNode(tok.clone(), value.clone()))
                else:
                    items.append([TupleNode(tok.clone(), value.clone())])
            next(toks)  # comma
        except StopIteration:
            break
    listitems = []
    for item in items:
        if listitems:
            listitems.append(Plus())
        if isinstance(item, list):
            listitems.append(ListNode(*item))
        else:
            call = Node(SYMBOL.test, [*Attr(item, Name("items")), ArgList([])])
            listitems.append(call)
    args = listitems
    if len(listitems) > 1:
        args = [Node(SYMBOL.arith_expr, args)]
    return Call(Name("dict"), args, prefix=node.prefix)


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
        .select("""atom< "{" dictsetmaker< body=any* > "}" >""")
        .filter(filter_dict_literal)
        .modify(modify_dict_literal)
        .idiff()
    )


if __name__ == "__main__":
    main()
