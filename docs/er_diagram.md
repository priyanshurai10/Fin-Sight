# Entity-Relationship (ER) Diagram — FinSight AI

The relational schema is optimized for high-throughput transaction indexing, customer RFM tracking, and real-time fraud alert triage.

---

## 1. Mermaid ER Diagram

```mermaid
erDiagram
    USERS ||--o{ AUDIT_LOGS : performs
    CUSTOMERS ||--o{ TRANSACTIONS : executes
    CUSTOMERS ||--|| CUSTOMER_SEGMENTS : categorized_as
    TRANSACTIONS ||--o| FRAUD_ALERTS : triggers

    USERS {
        int id PK
        string username
        string email
        string hashed_password
        string role
        boolean is_active
        datetime created_at
    }

    TRANSACTIONS {
        int id PK
        string transaction_id UK
        string customer_id FK
        datetime timestamp
        float amount
        string merchant_category
        string card_type
        string entry_mode
        string channel
        string location_country
        float distance_from_home_km
        int velocity_1h
        int velocity_24h
        boolean is_fraud_actual
        float fraud_risk_score
        string risk_level
        string status
    }

    FRAUD_ALERTS {
        int id PK
        string transaction_id FK
        datetime alert_time
        float risk_score
        string trigger_reason
        string status
        string assigned_to
    }

    CUSTOMER_SEGMENTS {
        int id PK
        string customer_id UK
        int recency_days
        int frequency_cnt
        float monetary_val
        int segment_cluster
        string segment_label
        datetime last_updated
    }

    AUDIT_LOGS {
        int id PK
        datetime timestamp
        string user_id
        string action
        text details
    }
```

---

## 2. Table Field Specifications

- **`transactions`**: Primary ledger table. B-Tree indexed on `transaction_id`, `customer_id`, `timestamp`, and `is_fraud_actual`.
- **`fraud_alerts`**: High-risk transaction queue for human analyst triage.
- **`customer_segments`**: Stores K-Means RFM clustering outputs updated via daily batch jobs.
