<?php
header('Content-Type: application/json');

$db_host = 'localhost';
$db_user = 'logger';
$db_pass = 'logger';
$db_name = 'ciscoLogger';

$conn = new mysqli($db_host, $db_user, $db_pass, $db_name);

if ($conn->connect_error) {
    echo json_encode(['error' => 'Database connection failed: ' . $conn->connect_error]);
    exit;
}

if (isset($_GET['switch'])) {
    $switch = $_GET['switch'];
    $query = "
        SELECT DISTINCT interface_name
        FROM interface_stats_history
        WHERE switch = ?
        ORDER BY CAST(REGEXP_SUBSTR(interface_name, '[0-9]+$') AS UNSIGNED), interface_name ASC
    ";
    $stmt = $conn->prepare($query);
    $stmt->bind_param("s", $switch);
    $stmt->execute();
    $result = $stmt->get_result();

    $ports = [];
    while ($row = $result->fetch_assoc()) {
        $ports[] = $row['interface_name'];
    }

    echo json_encode($ports);
    $stmt->close();
} else {
    echo json_encode(['error' => 'No switch specified']);
}

$conn->close();
?>