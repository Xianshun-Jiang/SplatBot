from neo4j import GraphDatabase
import pandas as pd



driver  = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'CoolPassword'))

def import_weapons():
    # Load the CSV
    df = pd.read_csv("./all.csv")
    
    with driver.session() as session:
        # Create nodes for each weapon
        for index, row in df.iterrows():
            session.write_transaction(create_weapon_node, row)

def create_weapon_node(tx, row):
    # Cypher query to create a node for each weapon. Adjust properties as needed.
    query = (
        "CREATE (w:Weapon {name: $name, sub: $sub, special: $special, class: $class, range: $range, ran: $ran})"
    )
    parameters = {
        "name": row["Name"],
        "sub": row["Sub"],
        "special": row["Special"],
        "class": row["Class"],
        "range": row["Range"],
        "ran": row["ran"],
    }
    tx.run(query, parameters)

import_weapons()
driver.close()

# result = neo.run("MATCH (n) RETURN n")

# def read_all_records(session):
#     query = "MATCH (n) RETURN n"
#     result = session.run(query)
#     return [record["n"] for record in result]

# records = read_all_records(neo)
# for record in records:
#     print(record)