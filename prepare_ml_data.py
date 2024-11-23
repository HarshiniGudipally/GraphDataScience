# Run this script to prepare the data for machine learning.

from neo4j import GraphDatabase
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

uri = "bolt://localhost:7687"
username = "neo4j"
password = "your_password"  # Replace with your actual password

driver = GraphDatabase.driver(uri, auth=(username, password))

def get_ml_data(tx):
    result = tx.run("""
    MATCH (c:Customer)-[:MADE]->(t:Transaction)-[:AT]->(m:Merchant)
    RETURN t.id AS transaction_id,
           t.amount AS amount,
           c.transaction_count AS customer_transaction_count,
           c.total_amount AS customer_total_amount,
           c.avg_transaction_amount AS customer_avg_amount,
           m.transaction_count AS merchant_transaction_count,
           m.total_amount AS merchant_total_amount,
           m.avg_transaction_amount AS merchant_avg_amount,
           t.is_fraud AS is_fraud
    """)
    return pd.DataFrame([dict(record) for record in result])

with driver.session() as session:
    df = session.execute_read(get_ml_data)

X = df.drop(['transaction_id', 'is_fraud'], axis=1)
y = df['is_fraud']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Save the prepared data
pd.DataFrame(X_train_scaled, columns=X.columns).to_csv('X_train.csv', index=False)
pd.DataFrame(X_test_scaled, columns=X.columns).to_csv('X_test.csv', index=False)
y_train.to_csv('y_train.csv', index=False)
y_test.to_csv('y_test.csv', index=False)

driver.close()