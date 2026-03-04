CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    plan TEXT NOT NULL DEFAULT 'FREE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'member',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    uploader_id UUID REFERENCES users(id),
    filename TEXT NOT NULL,
    document_type TEXT,
    source_hash TEXT NOT NULL,
    storage_key TEXT NOT NULL,
    confidence_score NUMERIC(5,4),
    status TEXT NOT NULL DEFAULT 'uploaded',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    transaction_date DATE,
    description TEXT,
    debit NUMERIC(14,2),
    credit NUMERIC(14,2),
    balance NUMERIC(14,2),
    currency TEXT,
    reference_id TEXT,
    account_number TEXT,
    bank_name TEXT,
    category TEXT
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    provider TEXT NOT NULL,
    provider_subscription_id TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,
    renews_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
