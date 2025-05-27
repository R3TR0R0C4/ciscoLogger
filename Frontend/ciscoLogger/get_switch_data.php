<?php

header('Content-Type: application/json');

// Database configuration (replace with your actual credentials)
$db_host = 'localhost';
$db_user = 'logger';
$db_pass = 'logger';
$db_name = 'ciscoLogger';

$switch_ip = isset($_GET['switch_ip']) ? $_GET['switch_ip'] : '';

if (empty($switch_ip)) {
    echo json_encode(["error" => "Switch IP not provided."]);
    exit();
}

$conn = new mysqli($db_host, $db_user, $db_pass, $db_name);

if ($conn->connect_error) {
    echo json_encode(["error" => "Database connection failed: " . $conn->connect_error]);
    exit();
}

// This query remains the same, as it pulls from 'interface_stats'
// and filters by the 'switch' column (which holds the IP).
$stmt = $conn->prepare("SELECT * FROM interface_stats WHERE switch = ?");
if ($stmt === false) {
    echo json_encode(["error" => "Failed to prepare statement: " . $conn->error]);
    $conn->close();
    exit();
}

$stmt->bind_param("s", $switch_ip);
$stmt->execute();
$result = $stmt->get_result();

$data = [];
if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        $data[] = $row;
    }
}

echo json_encode($data);

$stmt->close();
$conn->close();
?>