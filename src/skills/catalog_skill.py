import json
import os
from typing import Any, Dict, List, Optional
import duckdb
from langchain_core.tools import tool
from src.config import get_settings


def _get_connection() -> duckdb.DuckDBPyConnection:
    settings = get_settings()
    csv_path = settings.CATALOG_CSV_PATH
    if not os.path.isabs(csv_path):
        # Resolve relative to current working directory or project root
        csv_path = os.path.abspath(csv_path)

    # Normalize backslashes for DuckDB SQL
    normalized_path = csv_path.replace("\\", "/")
    conn = duckdb.connect(database=":memory:")
    conn.execute(f"CREATE OR REPLACE VIEW catalog AS SELECT * FROM read_csv('{normalized_path}', delim=',', header=True, auto_detect=True)")
    return conn


def query_catalog_sql(sql_query: str) -> List[Dict[str, Any]]:
    """Execute a read-only SQL query against the master catalog dataset."""
    conn = _get_connection()
    try:
        rel = conn.execute(sql_query)
        if rel.description is None:
            return []
        columns = [desc[0] for desc in rel.description]
        rows = rel.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()


def get_catalog_stats(filter_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get count and aggregate stats from the catalog given filters."""
    where_clauses = []
    if filter_dict:
        for k, v in filter_dict.items():
            if isinstance(v, (int, float)):
                where_clauses.append(f"{k} = {v}")
            elif isinstance(v, str):
                escaped = v.replace("'", "''")
                where_clauses.append(f"lower({k}) LIKE lower('%{escaped}%')")

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    sql = f"SELECT COUNT(*) as total_matching FROM catalog {where_sql}"
    res = query_catalog_sql(sql)
    total = res[0]["total_matching"] if res else 0
    return {"total_matching": int(total), "filters": filter_dict or {}}


@tool("catalog_query")
def catalog_tool(query: str) -> str:
    """Execute a SQL query against the master catalog dataset (view name: 'catalog').
    
    Columns available in 'catalog':
    - document_name (e.g. 'IRP 5', 'IRP 11')
    - title (e.g. 'Challenges of Realizing Maqasid al-Shariah...')
    - author (e.g. 'Said Bouheraoua; Sherin Kunhibava')
    - year (INTEGER, e.g. 2020)
    - publisher (e.g. 'INCEIF')
    - document_type (e.g. 'Research Paper', 'Book', 'Bulletin')
    - source_url (verbatim URL on ifikr.my)

    Always use SELECT queries. For counting, use SELECT COUNT(*) as count FROM catalog WHERE ...
    Always include source_url when referencing publications.
    """
    try:
        results = query_catalog_sql(query)
        if not results:
            return "No matching records found in catalog."
        return json.dumps(results, indent=2, default=str)
    except Exception as e:
        return f"Error executing catalog query: {e}"
