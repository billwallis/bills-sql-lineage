from sql_lineage import lineage


def test__sql_to_mermaid__can_correctly_parse_ctes_to_mermaid(
    mock_datetime,
    sql_mermaid_pair: tuple[str, str],
):
    assert lineage.sql_to_mermaid(sql_mermaid_pair[0]) == sql_mermaid_pair[1]
