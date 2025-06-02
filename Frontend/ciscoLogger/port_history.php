<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Port History</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="icon" type="image/x-icon" href="/assets/favicon.png">
    <script>
        function updatePorts() {
            const switchSelect = document.getElementById('switch');
            const portSelect = document.getElementById('port');
            const selectedSwitch = switchSelect.value;

            // Clear existing options
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
        <h1>Port History</h1>

        <form action="port_history.php" method="GET">
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

                    // Obtener la lista de switches
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

                        // Obtener los puertos disponibles para el switch seleccionado
                        $port_query = "
                            SELECT DISTINCT interface_name 
                            FROM interface_stats_history 
                            WHERE switch = ? 
                            ORDER BY 
                                LENGTH(interface_name), 
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
                <button type="submit">View History</button>
            </div>
        </form>

        <?php
        if (isset($_GET['switch']) && isset($_GET['port'])) {
            $switch = $_GET['switch'];
            $port = $_GET['port'];

            $stmt = $conn->prepare("
                SELECT interface_name, last_input, last_output, log_time, description, duplex_status, speed, vlan, mac, status, switchport, archived_at
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

                if ($result->num_rows > 0) {
                    echo "<h2>History for Port '" . htmlspecialchars($port) . "' on Switch '" . htmlspecialchars($switch) . "'</h2>";
                    echo "<table class='results-table'>";
                    echo "<thead><tr>";
                    echo "<th>Interface</th><th>Last Input</th><th>Last Output</th><th>Log Time</th><th>Description</th><th>Duplex</th><th>Speed</th><th>VLAN</th><th>MAC</th><th>Status</th><th>Switchport</th><th>Archived At</th>";
                    echo "</tr></thead><tbody>";
                    while ($row = $result->fetch_assoc()) {
                        echo "<tr>";
                        echo "<td>" . htmlspecialchars($row['interface_name']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['last_input']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['last_output']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['log_time']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['description']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['duplex_status']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['speed']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['vlan']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['mac']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['status']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['switchport']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['archived_at']) . "</td>";
                        echo "</tr>";
                    }
                    echo "</tbody></table>";
                } else {
                    echo "<p class='no-results-message'>No history found for Port '" . htmlspecialchars($port) . "' on Switch '" . htmlspecialchars($switch) . "'.</p>";
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