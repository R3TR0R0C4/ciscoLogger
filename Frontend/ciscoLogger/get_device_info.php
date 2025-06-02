<?php
header('Content-Type: application/json');

// Database configuration (replace with your actual credentials)
$db_host = 'localhost';
$db_user = 'logger';
$db_pass = 'logger';
$db_name = 'ciscoLogger';

// Get IP address from GET request
$ip_address = isset($_GET['ip_address']) ? $_GET['ip_address'] : '';

// Validate input
if (empty($ip_address)) {
    echo json_encode(["error" => "IP address not provided."]);
    exit();
}

// Establish database connection
$conn = new mysqli($db_host, $db_user, $db_pass, $db_name);

// Check connection
if ($conn->connect_error) {
    echo json_encode(["error" => "Database connection failed: " . $conn->connect_error]);
    exit();
}

// Prepare SQL statement to prevent SQL injection
// Select all relevant fields from network_devices table
$stmt = $conn->prepare("SELECT ip_address, hostname, location, model FROM network_devices WHERE ip_address = ? LIMIT 1");
if ($stmt === false) {
    echo json_encode(["error" => "Failed to prepare statement: " . $conn->error]);
    $conn->close();
    exit();
}

// Bind the parameter and execute the statement
$stmt->bind_param("s", $ip_address); // "s" denotes a string parameter
$stmt->execute();

// Get the result set
$result = $stmt->get_result();

$device_info = [];
if ($result->num_rows > 0) {
    $device_info = $result->fetch_assoc(); // Fetch single row as associative array
}

// Return data as JSON
echo json_encode($device_info);

// Close connections
$stmt->close();
$conn->close();
?>