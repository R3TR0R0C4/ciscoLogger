<?php
session_start();
if (!isset($_SESSION['username'])) {
    header("Location: /index.php");
    exit();
}

$db_host = 'localhost';
$db_user = 'logger';
$db_pass = 'logger';
$db_name = 'ciscoLogger';

$conn = new mysqli($db_host, $db_user, $db_pass, $db_name);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Total de puertos
$total_ports = $conn->query("SELECT COUNT(*) as total FROM interface_stats")->fetch_assoc()['total'];

// Puertos activos (Connected)
$active_ports = $conn->query("SELECT COUNT(*) as total FROM interface_stats WHERE status = 'Connected'")->fetch_assoc()['total'];

// Puertos desconectados (Not connected)
$not_connected_ports = $conn->query("SELECT COUNT(*) as total FROM interface_stats WHERE status = 'Not connected'")->fetch_assoc()['total'];

// Puertos shutdown (Shutdown)
$shutdown_ports = $conn->query("SELECT COUNT(*) as total FROM interface_stats WHERE status = 'Shutdown'")->fetch_assoc()['total'];

// Puertos por VLAN
$vlans = [];
$result = $conn->query("SELECT vlan, COUNT(*) as total FROM interface_stats GROUP BY vlan ORDER BY CAST(vlan AS UNSIGNED) ASC");
while ($row = $result->fetch_assoc()) {
    $vlans[$row['vlan']] = $row['total'];
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Port Statistics</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <h1>Estadísticas de Puertos</h1>
    <ul>
        <li><strong>Total de puertos:</strong> <?php echo $total_ports; ?></li>
        <li><strong>Puertos activos (Connected):</strong> <?php echo $active_ports; ?></li>
        <li><strong>Puertos desconectados (Not connected):</strong> <?php echo $not_connected_ports; ?></li>
        <li><strong>Puertos shutdown (Shutdown):</strong> <?php echo $shutdown_ports; ?></li>
    </ul>
    <h2>Puertos por VLAN</h2>
    <table border="1" cellpadding="5">
        <tr>
            <th>VLAN</th>
            <th>Cantidad de Puertos</th>
        </tr>
        <?php foreach ($vlans as $vlan => $count): ?>
            <?php if (trim($vlan) !== ''): // Omitir VLAN en blanco ?>
                <tr>
                    <td><?php echo htmlspecialchars($vlan); ?></td>
                    <td><?php echo $count; ?></td>
                </tr>
            <?php endif; ?>
        <?php endforeach; ?>
    </table>
    <br>
    <a href="logger.php" class="button">Volver</a>
</body>
</html>
<?php $conn->close(); ?>