from __future__ import annotations

import contextlib
import datetime
from typing import Literal

import sqlglot
from sqlglot import exp
from sqlglot.optimizer import qualify

Nodes = list[str]
Edges = list[tuple[str, str]]  # Directed edges, source --> target.
NodeType = Literal["root"] | Literal["internal vertex"] | Literal["leaf"]
SemanticNodes = list[tuple[str, NodeType]]

OUTER_QUERY_VALUE = "."
OUTER_QUERY_LABEL = "•"


def _qualify_table(table: exp.Table) -> str:
    return ".".join([p.name for p in table.parts])


def _parse_ctes(sql: str, dialect: str | None = None) -> tuple[Nodes, Edges]:
    """
    Parse an SQL query into nodes and edges based on CTEs.
    """

    nodes, edges = [], []
    parsed = sqlglot.parse_one(sql, dialect=dialect)
    with contextlib.suppress(Exception):
        # There isn't a hard requirement for the query to be valid SQL,
        # but it's better if it is
        parsed = qualify.qualify(parsed)

    # Lazy and error-prone CTE sourcing
    for cte in parsed.find_all(exp.CTE):
        nodes.append(cte.alias)
        for tbl in cte.find_all(exp.Table):
            tbl_identifier = _qualify_table(tbl)
            if tbl_identifier not in nodes:
                nodes.append(tbl_identifier)
            edges.append((tbl_identifier, cte.alias))

    parsed.args["with"] = None  # Dirty hack to remove the CTEs from the query
    nodes.append(OUTER_QUERY_VALUE)
    edges.extend(
        (_qualify_table(tbl), OUTER_QUERY_VALUE)
        for tbl in parsed.find_all(exp.Table)
    )

    return nodes, edges


def _format_node(node: str, node_type: NodeType) -> str:
    if node == OUTER_QUERY_VALUE:
        return f'{node}(("{OUTER_QUERY_LABEL}"))'
    elif node_type == "root":
        return f'{node}{{{{"{node}"}}}}'
    elif node_type == "leaf":
        return f'{node}(("{node}"))'
    else:
        return f'{node}["{node}"]'


def _to_mermaid(nodes: SemanticNodes, edges: Edges) -> str:
    """
    Convert nodes and edges into a Mermaid graph.
    """

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mermaid = f"%% Generated at {now}\nflowchart TD\n"

    for node, node_type in nodes:
        mermaid += f"    {_format_node(node, node_type)}\n"

    mermaid += f"\n"
    for edge in edges:
        mermaid += f"    {edge[0]} --> {edge[1]}\n"

    return mermaid


def _get_semantic_nodes(nodes: Nodes, edges: Edges) -> SemanticNodes:
    semantic_nodes = []
    nodes_with_parents = set()
    nodes_with_children = set()

    for parent, child in edges:
        nodes_with_parents.add(child)
        nodes_with_children.add(parent)

    for node in nodes:
        # `root` takes precedence over `leaf` for single-node trees
        if node not in nodes_with_parents:
            semantic_nodes.append((node, "root"))
        elif node not in nodes_with_children:
            semantic_nodes.append((node, "leaf"))
        else:
            semantic_nodes.append((node, "internal vertex"))

    return semantic_nodes


def sql_to_mermaid(sql: str, dialect: str | None = None) -> str:
    """
    Convert an SQL query into a Mermaid graph.
    """

    nodes, edges = _parse_ctes(sql, dialect)
    semantic_nodes = _get_semantic_nodes(nodes, edges)

    return _to_mermaid(semantic_nodes, edges)
