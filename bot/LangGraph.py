from typing_extensions import TypedDict
from typing import List, TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langgraph.graph import START, StateGraph
from langchain_openai import ChatOpenAI
from langfuse.langchain import CallbackHandler
from langfuse import Langfuse
import os

langfuse = Langfuse()
PROMPT_NAME = os.environ["PROMPT_NAME"]

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from langgraph.prebuilt import ToolNode, tools_condition

class State(TypedDict):
    database: str
    user_input: str
    database_schema: str
    messages: Annotated[list[AnyMessage], add_messages]

langfuse_handler = CallbackHandler()

############ DATABASE

DATABASE_URL = os.environ["DATABASE_URL"]

# default_transaction_read_only is a defense-in-depth belt on top of the
# read-only Postgres role the DATABASE_URL is expected to authenticate as.
engine = create_engine(
    DATABASE_URL,
    connect_args={"options": "-c default_transaction_read_only=on"},
    pool_pre_ping=True,
    future=True,
)
DB_NAME = engine.url.database
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

############ TOOLS

def db_query(sql_query: str, database_name: str) -> list:
    """
    Execute query in SQL syntax against the Postgres database called database_name.

    Args:
        sql_query: SQL query
        database_name: name of database from which to execute

    Returns:
        A list of rows with answer
"""
    session = SessionLocal()
    try:
        result = session.execute(text(sql_query))
        rows = result.fetchall()
        columns = result.keys()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        return f"Ошибка запроса: {e}"
    finally:
        session.close()

# Equip the butler with tools
tools = [
    db_query
    ]



########### NODES



def get_schema_db(state: State):
    with engine.connect() as conn:
        tables = conn.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' "
            "ORDER BY table_name"
        )).fetchall()

        schema_parts = []
        for (table_name,) in tables:
            columns = conn.execute(
                text(
                    "SELECT column_name, data_type, is_nullable "
                    "FROM information_schema.columns "
                    "WHERE table_schema = 'public' AND table_name = :name "
                    "ORDER BY ordinal_position"
                ),
                {"name": table_name},
            ).fetchall()
            cols_sql = ",\n  ".join(
                f"{col} {dtype}" + ("" if nullable == "YES" else " NOT NULL")
                for col, dtype, nullable in columns
            )
            schema_parts.append(f"CREATE TABLE {table_name} (\n  {cols_sql}\n);")

    return {
            "database": DB_NAME,
            "database_schema": "\n\n".join(schema_parts),
            "user_input": state["user_input"]
            }

def assistant(state: State):
    prompt = langfuse.get_prompt(PROMPT_NAME)
    llm = ChatOpenAI(    model='openai/'+prompt.config["model"],
    max_tokens=prompt.config["max_tokens"],
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"])
    llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

    user_query = state["user_input"]
    db_schema = state["database_schema"]
    database_name = state["database"]

    system_message = prompt.compile(user_query=user_query,
                                    database_name=database_name,
                                    db_schema=db_schema)
    sys_msg = SystemMessage(content=system_message)

    return {
        "messages": [llm_with_tools.invoke([sys_msg] + state["messages"])],
    }


################### Graph itself

builder = StateGraph(State)

# Define nodes: these do the work
builder.add_node("get_schema_db", get_schema_db)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define edges: these determine how the control flow moves
builder.add_edge(START, "get_schema_db")
builder.add_edge("get_schema_db", "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message requires a tool, route to tools
    # Otherwise, provide a direct response
    tools_condition,
)
builder.add_edge("tools", "assistant")
react_graph = builder.compile()

