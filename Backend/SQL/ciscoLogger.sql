CREATE DATABASE ciscoLogger;

CREATE TABLE ciscoLogger.interface_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interface_name VARCHAR(255) NOT NULL,
    last_input VARCHAR(255),
    last_output VARCHAR(255),
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(255),
    duplex_status VARCHAR(50),
    speed VARCHAR(50),
    vlan VARCHAR(50),
    mac VARCHAR(50),
    status VARCHAR(50),
    switchport varchar(255),
    switch VARCHAR(255)
);


CREATE TABLE ciscoLogger.network_devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(255) UNIQUE NOT NULL,
    hostname VARCHAR(255) NOT NULL,
    location VARCHAR(255) DEFAULT NULL,
    model VARCHAR(255) DEFAULT NULL
);

