-- Client Registry Database Schema for KKT Master Distribution
-- Version: 1.0

DROP TABLE IF EXISTS deployment_history CASCADE;
DROP TABLE IF EXISTS deployed_instances CASCADE;
DROP TABLE IF EXISTS admin_users CASCADE;

CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'deployer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE deployed_instances (
    id SERIAL PRIMARY KEY,
    instance_name VARCHAR(100) NOT NULL,
    client_company VARCHAR(255) NOT NULL,
    vds_ip VARCHAR(45) NOT NULL,
    domain VARCHAR(255),
    deployed_version VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE deployment_history (
    id SERIAL PRIMARY KEY,
    instance_id INTEGER REFERENCES deployed_instances(id),
    action VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'in_progress',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
