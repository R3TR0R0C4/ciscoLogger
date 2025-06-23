<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Buscar MAC</title>
    <link rel="stylesheet" href="../css/style.css">
    <link rel="icon" type="image/x-icon" href="../assets/favicon.png">
    </head>
<body>
    <div class="container">
        <h1>MAC lookup</h1>

        <form action="mac_search.php" method="GET">
            <div class="form-group">
                <label for="mac_address">Input MAC:</label>
                <input type="text" id="mac_address" name="mac_address" placeholder="Ex: 28:C5:C8:E0:E9:B7 or 28:C5" value="<?php echo isset($_GET['mac_address']) ? htmlspecialchars($_GET['mac_address']) : ''; ?>">
            </div>
            <div class="form-group">
                <button type="submit">Search</button>
            </div>
        </form>

        <?php
        ini_set('display_errors', 1);
        ini_set('display_startup_errors', 1);
        error_reporting(E_ALL);

        header('Content-Type: text/html');      
        $db_host = 'localhost';
        $db_user = 'logger';
        $db_pass = 'logger';
        $db_name = 'ciscoLogger';

        $conn = new mysqli($db_host, $db_user, $db_pass, $db_name);

        if ($conn->connect_error) {
            die("<p class='error-message'>Error de conexión a la base de datos: " . $conn->connect_error . "</p>");
        }

        if (isset($_GET['mac_address']) && !empty($_GET['mac_address'])) {
            $clean_search_mac = str_replace(['.', ':', '-', ' '], '', $_GET['mac_address']);
            $search_mac_pattern = '%' . $clean_search_mac . '%';
            $stmt = $conn->prepare("
                SELECT *
                FROM interface_stats
                WHERE REPLACE(REPLACE(REPLACE(REPLACE(mac, '.', ''), ':', ''), '-', ''), ' ', '') LIKE ?
            ");
            
            if ($stmt === false) {
                echo "<p class='error-message'>Error al preparar la consulta: " . $conn->error . "</p>";
            } else {
                $stmt->bind_param("s", $search_mac_pattern);
                $stmt->execute();
                $result = $stmt->get_result();

                if ($result->num_rows > 0) {
                    echo "<h2>Results for '" . htmlspecialchars($_GET['mac_address']) . "'</h2>";
                    echo "<table class='results-table'>";
                    echo "<thead><tr>";
                    echo "<th>Switch IP</th><th>Interface</th><th>Description</th><th>MAC Address</th><th>VLAN</th>";
                    echo "</tr></thead><tbody>";
                    while ($row = $result->fetch_assoc()) {
                        echo "<tr>";
                        echo "<td>" . htmlspecialchars($row['switch']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['interface_name']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['description']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['mac']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['vlan']) . "</td>";
                        echo "</tr>";
                    }
                    echo "</tbody></table>";
                } else {
                    echo "<p class='no-results-message'>MAC '" . htmlspecialchars($_GET['mac_address']) . "' Not found on Database.</p>";
                }
                $stmt->close();
            }
        } else if (isset($_GET['mac_address']) && empty($_GET['mac_address'])) {
            echo "<p class='no-results-message'>Please, enter a MAC to lookup.</p>";
        }
        ?>

        <a href="../logger.php" class="back-button">Return to Index</a>
    </div>
</body>
</html>

<?php
$conn->close();
?>