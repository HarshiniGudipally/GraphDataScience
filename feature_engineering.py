# Run this script to add features to the graph.

from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "your_password"  # Replace with your actual password

driver = GraphDatabase.driver(uri, auth=(username, password))

def add_features(tx):
    tx.run("""
    MATCH (c:Customer)-[:MADE]->(t:Transaction)
    WITH c, count(t) AS transaction_count, sum(t.amount) AS total_amount
    SET c.transaction_count = transaction_count,
        c.total_amount = total_amount,
        c.avg_transaction_amount = total_amount / transaction_count
    """)

    tx.run("""
    MATCH (m:Merchant)<-[:AT]-(t:Transaction)
    WITH m, count(t) AS transaction_count, sum(t.amount) AS total_amount
    SET m.transaction_count = transaction_count,
        m.total_amount = total_amount,
        m.avg_transaction_amount = total_amount / transaction_count
    """)

with driver.session() as session:
    session.execute_write(add_features)

driver.close()