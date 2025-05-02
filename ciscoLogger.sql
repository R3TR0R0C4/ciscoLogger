CREATE DATABASE ciscoLogger;

CREATE TABLE switch_interface_log_180_238 (
    log_id INT AUTO_INCREMENT PRIMARY KEY, -- Unique identifier for each log entry
    switch_ip VARCHAR(15) NOT NULL,       -- IP address of the switch (e.g., '192.168.1.1')
    interface_name VARCHAR(20) NOT NULL,   -- Interface name (e.g., 'GigabitEthernet1/0/1')
    last_input VARCHAR(255),             -- Last input data/statistics (e.g., '0 packets, 0 bytes')
    last_output VARCHAR(255),            -- Last output data/statistics
    mac_address VARCHAR(17),             -- MAC address of the interface (e.g., '00:1A:2B:3C:4D:5E')
    log_time DATETIME NOT NULL,           -- Timestamp of the log entry
    description VARCHAR(255),           -- Interface description
    duplex_status VARCHAR(10),          -- Duplex status (e.g., 'Full', 'Half')
    speed VARCHAR(20),                  -- Interface speed (e.g., '1000 Mbps', '100 Mbps')
    UNIQUE KEY (switch_ip, interface_name, log_time) -- Added to prevent duplicate entries for the same interface and timestamp.
);


CREATE DATABASE ciscoLogger;
CREATE TABLE ciscoLogger.interface_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interface_name VARCHAR(255) NOT NULL,
    last_input DATETIME,
    last_output DATETIME,
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(255),
    duplex_status VARCHAR(50),
    speed VARCHAR(50),
    vlan VARCHAR(50),
    mac VARCHAR(50),
    status VARCHAR(50),
    switchport BOOLEAN,
    admin_status VARCHAR(50),
    port_mode VARCHAR(50),
    INDEX (interface_name, log_time),
    INDEX (status, log_time),
    INDEX (vlan)
);


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
    INDEX (interface_name, log_time),
    INDEX (status, log_time),
    INDEX (vlan)
);
