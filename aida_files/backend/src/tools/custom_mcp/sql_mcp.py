import ast
import json
import os
import re
import time
import requests
from datetime import datetime
from typing import List, Dict, Any
import uuid

from sqlglot import parse_one, exp
from sqlglot.optimizer import optimize
from sqlglot import transpile
from sqlglot import parse_one, expressions
from sqlparse import parse
from sqlparse.sql import Where
import sqlparse
from typing import List, Dict
from langchain_community.tools import DuckDuckGoSearchResults

from dotenv import find_dotenv, load_dotenv
from mcp.server.fastmcp import FastMCP
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


load_dotenv(find_dotenv(), verbose=True, override=True)
mcp = FastMCP("MCP Tools Server", "0.1.0")

@mcp.tool()
def QueryOptimizerTool(sql_query: str, dialect: str = "bigquery") -> Dict:
    """
    Analyzes and optimizes SQL queries for various dialects including BigQuery and Snowflake using SQLGlot and SQLParse.

    Description:
    This tool inspects a SQL query for common and dialect-specific anti-patterns that may impact performance or readability.
    It uses SQLGlot to parse the query and applies heuristics to detect issues such as SELECT *, unnecessary DISTINCT,
    correlated subqueries, redundant GROUP BY clauses, inefficient CTEs, and dialect-specific inefficiencies.
    It also suggests indexing strategies, structural improvements, and provides a complexity score and optimization summary.

    Arguments:
    - sql_query (str): The SQL query string to be analyzed.
    - dialect (str): The SQL dialect to be considered for optimization (e.g., 'bigquery', 'snowflake', 'postgres', 'mysql', 'sqlite', 'oracle', 'tsql').

    Returns:
    - Dict: A dictionary containing the original query, formatted query, optimized query, complexity score,
            recommendations, and a summary of improvements.
    """
    try:
        dialect_lower = dialect.lower()
        supported_dialects = ["bigquery", "snowflake", "postgres", "mysql", "sqlite", "oracle", "tsql"]
        if dialect_lower not in supported_dialects:
            return {
                "success": False,
                "error": f"Unsupported SQL dialect: {dialect}. Supported dialects: {', '.join(supported_dialects)}"
            }

        sql_expr = parse_one(sql_query, read=dialect_lower)
        formatted_sql = sqlparse.format(sql_query, reindent=True, keyword_case='upper', identifier_case='lower')

        def check_anti_patterns(sql_expr: exp.Expression, dialect: str) -> List[str]:
            anti_patterns = []
            if any(isinstance(c, exp.Star) for c in sql_expr.find_all(exp.Star)):
                anti_patterns.append("Avoid SELECT *; specify columns to reduce I/O and improve performance.")
            if sql_expr.args.get('distinct'):
                anti_patterns.append("DISTINCT detected; consider if GROUP BY is more efficient.")
            for subq in sql_expr.find_all(exp.Subquery):
                if any(isinstance(node, exp.Column) and not isinstance(node.table, exp.Table) for node in subq.find_all(exp.Column)):
                    anti_patterns.append("Correlated subquery detected; consider rewriting with JOINs or window functions.")
            for cte in sql_expr.find_all(exp.CTE):
                if isinstance(cte.this, exp.Select) and all(isinstance(c, exp.Star) for c in cte.this.expressions):
                    tables = list(cte.this.find_all(exp.Table))
                    if len(tables) == 1 and not cte.this.args.get('where') and not cte.this.args.get('group'):
                        anti_patterns.append("CTE may be an unnecessary wrapper; consider simplifying.")
            if sql_expr.args.get('group') and sql_expr.args.get('having'):
                having = sql_expr.args.get('having')
                if (isinstance(having, exp.GTE) and isinstance(having.left, exp.Count) and
                    isinstance(having.left.this, exp.Star) and isinstance(having.right, exp.Literal) and
                    having.right.value == 1):
                    anti_patterns.append("HAVING COUNT(*) >= 1 with GROUP BY is redundant.")
            if dialect == 'bigquery':
                extracts = sql_expr.find_all(exp.Extract)
                extract_cols = {}
                for extract_expr in extracts:
                    if hasattr(extract_expr, 'this') and extract_expr.this:
                        col_name = str(extract_expr.this)
                        extract_cols[col_name] = extract_cols.get(col_name, 0) + 1
                for col, count in extract_cols.items():
                    if count > 1:
                        anti_patterns.append(f"Multiple EXTRACTs on '{col}'; extract once and reuse.")
                order_by = sql_expr.args.get('order')
                if order_by:
                    for order_term in order_by if isinstance(order_by, list) else [order_by]:
                        if isinstance(order_term.this, exp.Subquery):
                            anti_patterns.append("ORDER BY with correlated subquery is inefficient in BigQuery.")
            elif dialect == 'snowflake':
                if any(isinstance(node, exp.Cast) for node in sql_expr.find_all(exp.Cast)):
                    anti_patterns.append("Avoid unnecessary CASTs; Snowflake supports automatic type conversion.")
            return anti_patterns

        def calculate_complexity_score(expr: exp.Expression) -> int:
            score = 0
            score += len(list(expr.find_all(exp.Table)))
            score += 2 * len(list(expr.find_all(exp.Join)))
            score += len(list(expr.find_all(exp.Subquery)))
            if expr.args.get('group'):
                score += 2
            if expr.args.get('having'):
                score += 1
            if expr.args.get('order'):
                score += 1
            if expr.args.get('distinct'):
                score += 2
            try:
                if hasattr(expr, 'expressions'):
                    score += len(list(expr.expressions))
            except TypeError:
                pass
            return score

        def generate_improvement_summary(recommendations: List[str], complexity: int, dialect: str) -> str:
            severity = "low"
            if complexity > 20:
                severity = "high"
            elif complexity > 10:
                severity = "medium"
            summary = f"Query complexity: {severity.upper()} ({complexity}/30). Found {len(recommendations)} optimization opportunities."
            if dialect == "bigquery" and any("partition" in r.lower() for r in recommendations):
                summary += " Consider partitioning for better BigQuery performance."
            elif dialect == "snowflake" and any("search optimization" in r.lower() for r in recommendations):
                summary += " Consider Snowflake search optimization."
            return summary

        anti_patterns = check_anti_patterns(sql_expr, dialect_lower)

        try:
            optimized_expr = optimize(sql_expr)
            optimized_sql = optimized_expr.sql(dialect=dialect_lower)
        except Exception as opt_err:
            optimized_sql = formatted_sql

        complexity_score = calculate_complexity_score(sql_expr)
        recommendations = sorted(set(anti_patterns), key=lambda r: (
            "correlated subquery" in r.lower(),
            "join" in r.lower(),
            "partition" in r.lower(),
            "index" in r.lower(),
            "select *" in r.lower()
        ), reverse=True)
        improvement_summary = generate_improvement_summary(recommendations, complexity_score, dialect_lower)

        return {
            "success": True,
            "dialect": dialect,
            "original_query": sql_query,
            "formatted_query": formatted_sql,
            "optimized_query": optimized_sql,
            "complexity_score": complexity_score,
            "recommendations": recommendations,
            "improvement_summary": improvement_summary
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Optimization Failed!\nError: {str(e)}"
        }
    

# Convert SQL Query Tool
@mcp.tool()
def ConvertSQLQuery(sql_query: str, source_dialect: str, target_dialect: str) -> dict:
    """
    Converts SQL from one dialect to another using SQLGlot.

    Parameters:
    ----------
    sql_query : str
        The SQL query to convert.
    source_dialect : str
        The source SQL dialect (e.g., 'oracle').
    target_dialect : str
        The target SQL dialect (e.g., 'snowflake').

    Returns:
    -------
    dict
        {
            "converted_sql": str or None,
            "error": str or None
        }
    """
    try:
        converted_sql = transpile(sql_query, read=source_dialect, write=target_dialect.lower())
        converted_sql_str = ' '.join(converted_sql)
        return {"converted_sql": converted_sql_str, "error": None}
    except Exception as e:
        return {"converted_sql": None, "error": str(e)}

# Extract SQL Information Tool
@mcp.tool()
def extract_sql_information(sql_query: str) -> dict:
    """
    Extracts structural information from a SQL query using SQLGlot and SQLParse.

    This function analyzes the SQL query to identify:
    - Source tables
    - Target table (if present)
    - Column mappings including transformations and aliases
    - Join conditions
    - Filter conditions (WHERE clauses)

    Parameters
    ----------
    sql_query : str
        The SQL query string to analyze.

    Returns
    -------
    dict
        {
            "source_tables": list of str,
            "target_table": str or None,
            "columns_mapping": list of dict,
            "joins": list of dict,
            "filters": list of str
        }

    Required Imports
    ----------------
    from sqlglot import parse_one, expressions
    from sqlparse import parse
    from sqlparse.sql import Where
    """
    result = {
        "source_tables": [],
        "target_table": None,
        "columns_mapping": [],
        "joins": [],
        "filters": []
    }

    # SQLGlot parsing
    try:
        parsed = parse_one(sql_query)

        result["source_tables"] = [table.alias_or_name for table in parsed.find_all(expressions.Table)]

        into_expr = parsed.find(expressions.Into)
        if into_expr:
            result["target_table"] = into_expr.this.sql()

        select_expr = parsed.find(expressions.Select)
        if select_expr:
            for column in select_expr.expressions:
                source_column = column.find(expressions.Identifier)
                alias = column.alias_or_name
                transformation = column.sql() if source_column else None
                result["columns_mapping"].append({
                    "source_column": source_column.sql() if source_column else None,
                    "transformation": transformation,
                    "target_column": alias
                })

        for join_expr in parsed.find_all(expressions.Join):
            result["joins"].append({
                "type": join_expr.args.get("kind", "INNER").upper(),
                "table": join_expr.this.sql(),
                "condition": join_expr.args.get("on", "").sql()
            })

        where_expr = parsed.find(expressions.Where)
        if where_expr:
            result["filters"].append(where_expr.this.sql())

    except Exception:
        pass

    # SQLParse parsing for additional filters
    try:
        statements = parse(sql_query)
        for statement in statements:
            for token in statement.tokens:
                if isinstance(token, Where):
                    result["filters"].append(token.value)
    except Exception:
        pass

    return result

@mcp.tool()
def GenerateSQLDiagram(source_tables: List[str], target_table: str, diagram_output_name: str) -> dict:
    """
    Generates a diagram connecting source tables to a target table using Matplotlib.

    Description:
        - Layout Calculation: Manually calculates positions for source and target table nodes.
        - Visual Styling: Uses Matplotlib's plotting features to style nodes and connecting lines.
        - Node & Edge Drawing: Plots nodes as text boxes and edges as arrows to show dependencies (source -> target).
        - Diagram Rendering: Generates and saves the diagram as an image file.
        - Chat Display: Also creates a temporary copy for displaying in chat interface.
        - Status Reporting: Returns success status, output file path, and temporary file path for downstream usage.

    Arguments:
        source_tables (list): A list of strings representing the names of source tables.
        target_table (str): A string representing the name of the target table.
        diagram_output_name (str): The name of the diagram image which will be saved.

    Returns:
        dict: A dictionary containing the status of the diagram generation, output file path, 
              temporary file path for chat display, and description of the diagram.
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        # --- Node Positions ---
        # Evenly space source tables on the left
        source_y_positions = np.linspace(0.1, 0.9, len(source_tables))
        source_positions = [(0.2, y) for y in source_y_positions]
        
        # Place target table on the right, centered relative to source tables
        target_y_center = np.mean(source_y_positions)  # Center based on source table positions
        target_pos = (0.8, target_y_center)

        # --- Visual Styling ---
        node_style = dict(boxstyle="round,pad=0.5", fc="lightblue", ec="black", lw=1)
        target_node_style = dict(boxstyle="round,pad=0.5", fc="lightgreen", ec="black", lw=1)
        arrow_style = dict(arrowstyle="->,head_width=0.4,head_length=0.8",
                           shrinkA=30, shrinkB=50, # Higher shrink values to ensure arrows stop at borders
                           fc="black", ec="black",
                           connectionstyle="arc3,rad=0.1") # Reduced curve for cleaner arrows

        # --- Draw Nodes ---
        # Draw target table
        ax.text(target_pos[0], target_pos[1], target_table, ha="center", va="center",
                bbox=target_node_style, fontsize=12)

        # Draw source tables and arrows
        for i, table_name in enumerate(source_tables):
            ax.text(source_positions[i][0], source_positions[i][1], table_name,
                    ha="center", va="center", bbox=node_style, fontsize=12)

            # --- Calculate Smart Arrow Connection Points ---
            # Calculate connection point on target box border based on source position
            source_y = source_positions[i][1]
            target_y = target_pos[1]
            
            # Determine which side of the target box to connect to
            if source_y > target_y + 0.05:  # Source is above target
                # Connect to top-left of target box
                connection_point = (target_pos[0] - 0.05, target_pos[1] + 0.03)
            elif source_y < target_y - 0.05:  # Source is below target
                # Connect to bottom-left of target box
                connection_point = (target_pos[0] - 0.05, target_pos[1] - 0.03)
            else:  # Source is roughly at same level
                # Connect to left side of target box
                connection_point = (target_pos[0] - 0.08, target_pos[1])

            # --- Draw Edges (Arrows) with smart connection points ---
            ax.annotate("",
                        xy=connection_point,
                        xytext=source_positions[i],
                        arrowprops=arrow_style)

        # --- Diagram Rendering ---
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off') # Hide the axes
        plt.title("SQL Table Dependencies", fontsize=16)
        
        # Save to user-specified location (permanent file)
        #plt.savefig(diagram_output_file, format='png', bbox_inches='tight')

        # Create temporary copy for chat display in project temp directory
        temp_dir = "diagrams"
        os.makedirs(temp_dir, exist_ok=True)
        #temp_filename = f"diagram_{uuid.uuid4().hex[:8]}.png"
        diagram_output = f"{diagram_output_name}.png"
        temp_path = os.path.join(temp_dir, diagram_output)
        plt.savefig(temp_path, format='png', bbox_inches='tight')
        
        plt.close(fig) # Close the figure to free memory

        # Create description of the diagram
        source_list = ", ".join(source_tables)
        description = f"Created a data flow diagram showing connections from source tables ({source_list}) to target table ({target_table}). The diagram visualizes the ETL pipeline with arrows indicating data flow direction."

        # Convert temp_path to absolute path
        temp_path_abs = os.path.abspath(temp_path)

        return {"status": "success", "output_file": temp_path_abs}

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    
    mcp.run(transport="stdio")

