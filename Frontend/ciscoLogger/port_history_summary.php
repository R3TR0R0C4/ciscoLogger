<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Port History Summary</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="icon" type="image/x-icon" href="/assets/favicon.png">
    <script>
        function updatePorts() {
            const switchSelect = document.getElementById('switch');
            const portSelect = document.getElementById('port');
            const selectedSwitch = switchSelect.value;

            portSelect.innerHTML = '<option value="">Select a Port</option>';

            if (selectedSwitch) {
                fetch(`get_ports.php?switch=${encodeURIComponent(selectedSwitch)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            console.error(data.error);
                        } else {
                            data.forEach(port => {
                                const option = document.createElement('option');
                                option.value = port;
                                option.textContent = port;
                                portSelect.appendChild(option);
                            });
                        }
                    })
                    .catch(error => console.error('Error fetching ports:', error));
            }
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Port History Summary</h1>

        <form action="port_history_summary.php" method="GET">
            <div class="form-group">
                <label for="switch">Switch IP:</label>
                <select id="switch" name="switch" required onchange="updatePorts()">
                    <option value="">Select a Switch</option>
                    <?php
                    $db_host = 'localhost';
                    $db_user = 'logger';
                    $db_pass = 'logger';
                    $db_name = 'ciscoLogger';

                    $conn = new mysqli($db_host, $db_user, $db_pass, $db_name);

                    if ($conn->connect_error) {
                        die("<p class='error-message'>Database connection failed: " . $conn->connect_error . "</p>");
                    }

                    $switches = [];
                    $switch_query = "SELECT DISTINCT switch FROM interface_stats_history ORDER BY switch ASC";
                    $switch_result = $conn->query($switch_query);

                    if ($switch_result && $switch_result->num_rows > 0) {
                        while ($row = $switch_result->fetch_assoc()) {
                            $switches[] = $row['switch'];
                        }
                    }
                    foreach ($switches as $switch): ?>
                        <option value="<?php echo htmlspecialchars($switch); ?>" <?php echo (isset($_GET['switch']) && $_GET['switch'] === $switch) ? 'selected' : ''; ?>>
                            <?php echo htmlspecialchars($switch); ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="form-group">
                <label for="port">Port Name:</label>
                <select id="port" name="port" required>
                    <option value="">Select a Port</option>
                    <?php
                    if (isset($_GET['switch'])) {
                        $selectedSwitch = $_GET['switch'];
                        $selectedPort = isset($_GET['port']) ? $_GET['port'] : '';

                        $port_query = "
                            SELECT DISTINCT interface_name 
                            FROM interface_stats_history 
                            WHERE switch = ? 
                            ORDER BY 
                                CAST(REGEXP_SUBSTR(interface_name, '[0-9]+$') AS UNSIGNED), 
                                interface_name ASC
                        ";
                        $stmt = $conn->prepare($port_query);
                        $stmt->bind_param("s", $selectedSwitch);
                        $stmt->execute();
                        $port_result = $stmt->get_result();

                        if ($port_result && $port_result->num_rows > 0) {
                            while ($row = $port_result->fetch_assoc()) {
                                $port = $row['interface_name'];
                                $isSelected = ($port === $selectedPort) ? 'selected' : '';
                                echo "<option value='" . htmlspecialchars($port) . "' $isSelected>" . htmlspecialchars($port) . "</option>";
                            }
                        }
                        $stmt->close();
                    }
                    ?>
                </select>
            </div>
            <div class="form-group">
                <button type="submit">View Summary</button>
            </div>
        </form>

        <?php
        if (isset($_GET['switch']) && isset($_GET['port'])) {
            $switch = $_GET['switch'];
            $port = $_GET['port'];

            $stmt = $conn->prepare("
                SELECT interface_name, description, vlan, mac, status, archived_at
                FROM interface_stats_history
                WHERE switch = ? AND interface_name = ?
                ORDER BY archived_at DESC
            ");

            if ($stmt === false) {
                echo "<p class='error-message'>Error preparing query: " . $conn->error . "</p>";
            } else {
                $stmt->bind_param("ss", $switch, $port);
                $stmt->execute();
                $result = $stmt->get_result();

                $history = [];
                while ($row = $result->fetch_assoc()) {
                    $history[] = $row;
                }

                // Solo mostrar cambios relevantes
                $filtered = [];
                $prev = null;
                foreach ($history as $entry) {
                    if (
                        !$prev ||
                        $entry['status'] !== $prev['status'] ||
                        $entry['vlan'] !== $prev['vlan'] ||
                        $entry['description'] !== $prev['description'] ||
                        $entry['mac'] !== $prev['mac']
                    ) {
                        $filtered[] = $entry;
                    }
                    $prev = $entry;
                }

                if (count($filtered) > 0) {
                    echo "<h2>Resumen de cambios para el puerto '" . htmlspecialchars($port) . "' en el switch '" . htmlspecialchars($switch) . "'</h2>";
                    echo "<table class='results-table'>";
                    echo "<thead><tr>";
                    echo "<th>Desde</th><th>Hasta</th><th>Status</th><th>VLAN</th><th>Descripción</th><th>MAC</th>";
                    echo "</tr></thead><tbody>";

                    for ($i = 0; $i < count($filtered); $i++) {
                        $from = $filtered[$i]['archived_at'];
                        $to = $i > 0 ? $filtered[$i-1]['archived_at'] : 'Ahora';
                        echo "<tr>";
                        echo "<td>" . htmlspecialchars($from) . "</td>";
                        echo "<td>" . htmlspecialchars($to) . "</td>";
                        echo "<td>" . htmlspecialchars($filtered[$i]['status']) . "</td>";
                        echo "<td>" . htmlspecialchars($filtered[$i]['vlan']) . "</td>";
                        echo "<td>" . htmlspecialchars($filtered[$i]['description']) . "</td>";
                        echo "<td>" . htmlspecialchars($filtered[$i]['mac']) . "</td>";
                        echo "</tr>";
                    }
                    echo "</tbody></table>";
                } else {
                    echo "<p class='no-results-message'>No hay cambios relevantes para este puerto.</p>";
                }
                $stmt->close();
            }
        }
        if (isset($conn) && $conn instanceof mysqli) {
            $conn->close();
        }
        ?>

        <a href="logger.php" class="back-button">Return to Logger</a>
    </div>
</body>
</html>