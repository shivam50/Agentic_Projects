-- Initialize databases for each microservice
-- This script runs once when the postgres container is first created.

CREATE DATABASE products_db;
CREATE DATABASE orders_db;
CREATE DATABASE users_db;
