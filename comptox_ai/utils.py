def execute_cypher_transaction(tx, query):
    records = []
    for record in tx.run(query):
        print(record)
        records.append(record)
    return(records)

