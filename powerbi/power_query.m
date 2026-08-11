// Power Query (M) Script for FinSight AI Data Ingestion via REST API

let
    // 1. Fetch REST API Endpoint
    Source = Json.Document(Web.Contents("http://localhost:8000/api/v1/transactions?limit=5000")),
    
    // 2. Extract Transactions Array
    transactions = Source[transactions],
    
    // 3. Convert List to Table
    #"Converted to Table" = Table.FromList(transactions, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
    
    // 4. Expand Record Columns
    #"Expanded Column1" = Table.ExpandRecordColumn(#"Converted to Table", "Column1", {
        "transaction_id", "customer_id", "timestamp", "amount", "merchant_category", 
        "card_type", "entry_mode", "channel", "location_country", "distance_from_home_km", 
        "velocity_1h", "velocity_24h", "is_fraud_actual", "fraud_risk_score", "risk_level", "status"
    }),
    
    // 5. Set Explicit Column Data Types
    #"Changed Type" = Table.TransformColumnTypes(#"Expanded Column1",{
        {"transaction_id", type text}, 
        {"customer_id", type text}, 
        {"timestamp", type datetime}, 
        {"amount", Currency.Type}, 
        {"merchant_category", type text}, 
        {"card_type", type text}, 
        {"entry_mode", type text}, 
        {"channel", type text}, 
        {"location_country", type text}, 
        {"distance_from_home_km", type number}, 
        {"velocity_1h", Int64.Type}, 
        {"velocity_24h", Int64.Type}, 
        {"is_fraud_actual", type logical}, 
        {"fraud_risk_score", type number}, 
        {"risk_level", type text}, 
        {"status", type text}
    })
in
    #"Changed Type"
