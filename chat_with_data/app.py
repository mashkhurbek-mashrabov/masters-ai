import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
import logging
from dotenv import load_dotenv

from src.agent import DataAgent
from src.tools import get_sample_queries, get_database_schema

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ChatWithData.App")

st.set_page_config(
    page_title="Chat with Data",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = "data/ecommerce.db"


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def get_database_stats() -> dict:
    conn = get_db_connection()

    stats = {}

    for table in ["customers", "products", "orders", "order_items"]:
        cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
        stats[f"{table}_count"] = cursor.fetchone()[0]

    cursor = conn.execute(
        "SELECT SUM(total_amount) FROM orders WHERE status = 'delivered'"
    )
    stats["total_revenue"] = cursor.fetchone()[0] or 0

    cursor = conn.execute(
        "SELECT AVG(total_amount) FROM orders WHERE status = 'delivered'"
    )
    stats["avg_order_value"] = cursor.fetchone()[0] or 0

    cursor = conn.execute(
        "SELECT status, COUNT(*) FROM orders GROUP BY status"
    )
    stats["orders_by_status"] = dict(cursor.fetchall())

    cursor = conn.execute("""
        SELECT p.category, SUM(oi.quantity * oi.unit_price) as revenue
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        GROUP BY p.category
        ORDER BY revenue DESC
    """)
    stats["revenue_by_category"] = dict(cursor.fetchall())

    conn.close()
    return stats


def render_sidebar():
    st.sidebar.title("📊 Data Insights")

    stats = get_database_stats()

    st.sidebar.header("Database Overview")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Customers", f"{stats['customers_count']:,}")
        st.metric("Orders", f"{stats['orders_count']:,}")
    with col2:
        st.metric("Products", f"{stats['products_count']:,}")
        st.metric("Order Items", f"{stats['order_items_count']:,}")

    st.sidebar.header("Revenue Metrics")
    st.sidebar.metric(
        "Total Revenue",
        f"${stats['total_revenue']:,.2f}"
    )
    st.sidebar.metric(
        "Avg Order Value",
        f"${stats['avg_order_value']:.2f}"
    )

    st.sidebar.header("Order Status")
    status_df = pd.DataFrame(
        list(stats["orders_by_status"].items()),
        columns=["Status", "Count"]
    )
    fig = px.pie(
        status_df,
        values="Count",
        names="Status",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=250,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3)
    )
    st.sidebar.plotly_chart(fig, use_container_width=True)

    st.sidebar.header("Revenue by Category")
    category_df = pd.DataFrame(
        list(stats["revenue_by_category"].items()),
        columns=["Category", "Revenue"]
    )
    fig2 = px.bar(
        category_df,
        x="Revenue",
        y="Category",
        orientation="h",
        color="Revenue",
        color_continuous_scale="Blues"
    )
    fig2.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=250,
        showlegend=False,
        coloraxis_showscale=False
    )
    fig2.update_xaxes(title_text="Revenue ($)")
    fig2.update_yaxes(title_text="")
    st.sidebar.plotly_chart(fig2, use_container_width=True)

    st.sidebar.header("Sample Queries")
    sample_queries = get_sample_queries()
    for sq in sample_queries:
        with st.sidebar.expander(sq["description"]):
            st.code(sq["query"], language="sql")
            if st.button("Use this query", key=f"sq_{sq['description']}"):
                st.session_state.sample_query = f"Run this query: {sq['query']}"
                st.rerun()

    st.sidebar.divider()
    st.sidebar.header("Configuration")

    with st.sidebar.expander("GitHub Settings (Optional)"):
        github_owner = st.text_input(
            "Repository Owner",
            value=st.session_state.get("github_owner", ""),
            help="GitHub username or organization"
        )
        github_repo = st.text_input(
            "Repository Name",
            value=st.session_state.get("github_repo", ""),
            help="Repository for support tickets"
        )
        github_token = st.text_input(
            "GitHub Token",
            value=st.session_state.get("github_token", ""),
            type="password",
            help="Personal access token with repo scope"
        )

        if st.button("Save GitHub Settings"):
            st.session_state.github_owner = github_owner
            st.session_state.github_repo = github_repo
            st.session_state.github_token = github_token
            st.success("Settings saved!")


def initialize_agent():
    if "agent" not in st.session_state:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            st.error("Please set the OPENAI_API_KEY environment variable.")
            st.stop()

        config = {
            "db_path": DB_PATH,
            "github_owner": st.session_state.get("github_owner", ""),
            "github_repo": st.session_state.get("github_repo", ""),
            "github_token": st.session_state.get("github_token", "")
        }

        st.session_state.agent = DataAgent(
            api_key=api_key,
            model="gpt-4o-mini",
            config=config
        )
        logger.info("Agent initialized")

    return st.session_state.agent


def render_chat():
    st.title("💬 Chat with Data")
    st.markdown(
        "Ask questions about your e-commerce data. "
        "I can query the database, explain insights, and help you understand your business metrics."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []
        welcome_msg = """Welcome! I'm your data assistant. I can help you explore your e-commerce database which includes:

- **Customers**: 150 customer records
- **Products**: 50 products across 5 categories
- **Orders**: 600+ orders with various statuses
- **Order Items**: 1,700+ line items

Try asking questions like:
- "What are the top 5 best-selling products?"
- "Show me monthly revenue trends"
- "Which customers have the highest order values?"

You can also ask me to create a support ticket if you need human assistance!"""
        st.session_state.messages.append({
            "role": "assistant",
            "content": welcome_msg
        })

    if "sample_query" in st.session_state:
        query = st.session_state.sample_query
        del st.session_state.sample_query
        st.session_state.messages.append({"role": "user", "content": query})

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about your data..."):
        logger.info(f"User input: {prompt}")

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        agent = initialize_agent()

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = agent.chat_sync(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                    logger.info(f"Agent response generated")
                except Exception as e:
                    error_msg = f"An error occurred: {str(e)}"
                    st.error(error_msg)
                    logger.error(error_msg)

    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 Reset Chat"):
            st.session_state.messages = []
            if "agent" in st.session_state:
                st.session_state.agent.reset_conversation()
            logger.info("Chat reset by user")
            st.rerun()

    with col2:
        if st.button("🎫 Create Ticket"):
            ticket_prompt = "I need to create a support ticket to speak with a human representative."
            st.session_state.messages.append({"role": "user", "content": ticket_prompt})
            st.rerun()


def render_schema_explorer():
    st.header("📋 Database Schema")

    schema_result = get_database_schema(DB_PATH)

    if schema_result["success"]:
        schema = schema_result["schema"]

        for table_name, table_info in schema.items():
            with st.expander(f"**{table_name}** ({table_info['row_count']:,} rows)", expanded=True):
                columns_df = pd.DataFrame(table_info["columns"])
                st.dataframe(columns_df, use_container_width=True, hide_index=True)

                conn = get_db_connection()
                sample_df = pd.read_sql_query(
                    f"SELECT * FROM {table_name} LIMIT 5",
                    conn
                )
                conn.close()

                st.markdown("**Sample Data:**")
                st.dataframe(sample_df, use_container_width=True, hide_index=True)
    else:
        st.error(f"Error loading schema: {schema_result.get('error', 'Unknown error')}")


def main():
    logger.info("Application started")

    render_sidebar()

    tab1, tab2 = st.tabs(["💬 Chat", "📋 Schema Explorer"])

    with tab1:
        render_chat()

    with tab2:
        render_schema_explorer()

    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #888;'>
        <small>Chat with Data | Built with Streamlit and OpenAI | GenAI Course Project</small>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
