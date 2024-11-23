# Run this script to ingest the data into Neo4j.

from neo4j import GraphDatabase
import pandas as pd

uri = "bolt://localhost:7687"
username = "neo4j"
password = "your_password"  # Replace with your actual password

driver = GraphDatabase.driver(uri, auth=(username, password))

def create_graph(tx, row):
    tx.run("""
    MERGE (c:Customer {id: $customer_id})
    MERGE (m:Merchant {id: $merchant_id})
    CREATE (t:Transaction {
        id: $transaction_id,
        date: date($date),
        amount: $amount,
        is_fraud: $is_fraud
    })
    CREATE (c)-[:MADE]->(t)
    CREATE (t)-[:AT]->(m)
    """, row.to_dict())

df = pd.read_csv('transactions.csv')

with driver.session() as session:
    for _, row in df.iterrows():
        session.execute_write(create_graph, row)

driver.close()