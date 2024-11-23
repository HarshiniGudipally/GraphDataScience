# This script provides a function to predict the fraud probability for new transactions.


from neo4j import GraphDatabase
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib

uri = "bolt://localhost:7687"
username = "neo4j"
password = "your_password"  # Replace with your actual password

driver = GraphDatabase.driver(uri, auth=(username, password))

# Load the trained model and scaler
clf = joblib.load('random_forest_model.joblib')
scaler = joblib.load('scaler.joblib')

def get_transaction_features(tx, customer_id, merchant_id, amount):
    result = tx.run("""
    MATCH (c:Customer {id: $customer_id})
    MATCH (m:Merchant {id: $merchant_id})
    RETURN c.transaction_count AS customer_transaction_count,
           c.total_amount AS customer_total_amount,
           c.avg_transaction_amount AS customer_avg_amount,
           m.transaction_count AS merchant_transaction_count,
           m.total_amount AS merchant_total_amount,
           m.avg_transaction_amount AS merchant_avg_amount
    """, customer_id=customer_id, merchant_id=merchant_id)
    
    record = result.single()
    features = [amount] + list(record.values())
    return features

def predict_fraud(customer_id, merchant_id, amount):
    with driver.session() as session:
        features = session.execute_read(get_transaction_features, customer_id, merchant_id, amount)
    
    features_scaled = scaler.transform([features])
    fraud_probability = clf.predict_proba(features_scaled)[0][1]
    return fraud_probability

# Example usage
print(predict_fraud('C001', 'M001', 100.00))

driver.close()