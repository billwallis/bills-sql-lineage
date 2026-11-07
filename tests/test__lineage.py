from sql_lineage import lineage


def test__sql_to_mermaid__can_correctly_parse_ctes_to_mermaid(
    mock_datetime,
    sql_with_ctes: str,
    mermaid_with_ctes: str,
):
    assert lineage.sql_to_mermaid(sql_with_ctes) == mermaid_with_ctes
