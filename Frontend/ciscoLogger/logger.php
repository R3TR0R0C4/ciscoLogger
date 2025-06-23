<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cisco Switch Logging</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="icon" type="image/x-icon" href="/assets/favicon.png">
</head>
<script>
    function startScript() {
        const statusEl = document.getElementById('script-status');
        statusEl.textContent = '⏳ Running interface collection info...';

        fetch('/ciscoLogger/run_script.php')
            .then(() => {
                const checkInterval = setInterval(() => {
                    fetch('/ciscoLogger/check_status.php')
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'done') {
                                statusEl.textContent = '✅ Completed';
                                clearInterval(checkInterval);
                            } else if (data.status === 'error') {
                                statusEl.textContent = '❌ Error: See log';
                                console.error(data.message);
                                clearInterval(checkInterval);
                            }
                        });
                }, 1000);
            })
            .catch(err => {
                statusEl.textContent = '❌ Failed to start script';
                console.error(err);
            });
    }
</script>
<body>
    <?php
        session_start();

        // Check if the 'username' session variable is NOT set
        if (!isset($_SESSION['username'])) {
            header("Location: /index.php");
            exit();
        }

        // Database configuration
        $db_host = 'localhost';
        $db_user = 'logger';
        $db_pass = 'logger';
        $db_name = 'ciscoLogger';

        $conn = new mysqli($db_host, $db_user, $db_pass, $db_name);

        if ($conn->connect_error) {
            die("Connection failed: " . $conn->connect_error);
        }

        // Obtener la última actualización
        $last_update = '';
        $sql_last_update = "SELECT log_time FROM interface_stats ORDER BY log_time DESC LIMIT 1";
        $result_last_update = $conn->query($sql_last_update);
        if ($result_last_update && $row = $result_last_update->fetch_assoc()) {
            $last_update = htmlspecialchars($row['log_time']);
        }
    ?>
    <div class="header-container">
      <h1 style="display:inline-block; margin-right:20px;">Cisco Switch Interface Logs</h1>
        <?php
        if ($last_update) {
            echo '<span class="last-update" style="margin-right:20px;">Last update:<br>' . $last_update . '</span>';
        } else {
            echo '<span class="last-update" style="margin-right:20px;">Unknown last update.</span>';
        }
        ?>

        <a href="lookups/mac_search.php" class="button">MAC</a>
        <a href="lookups/description_search.php" class="button">Description</a>
        <a href="port_history.php" class="button">Historics</a>
        <a href="port_history_summary.php" class="button">Historics Summary</a>
        <a href="/logout.php" class="logout-button">Logout</a>
    </div>
    <div id="tabs-container">
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

        $switches_data = [];
        $sql_switches = "SELECT ip_address, hostname FROM network_devices ORDER BY ip_address ASC";
        $result_switches = $conn->query($sql_switches);

        if ($result_switches && $result_switches->num_rows > 0) {
            while ($row = $result_switches->fetch_assoc()) {
                $switches_data[] = [
                    'ip' => htmlspecialchars($row['ip_address']),
                    'hostname' => htmlspecialchars($row['hostname'])
                ];
            }
        } else {
            echo "<p>No switches found in the network_devices table. Please ensure the table exists and is populated.</p>";
        }

        // Render tab buttons
        foreach ($switches_data as $switch) {
            echo '<button class="tab-button" data-switch-ip="' . $switch['ip'] . '">';
            echo '<span>' . $switch['ip'] . '</span>';
            echo '<span class="tab-hostname">' . $switch['hostname'] . '</span>';
            echo '</button>';
        }
        ?>
    </div>

    <div id="content-area">
        <p>Select a switch tab above to view its interface statistics.</p>
    </div>

    <script src="js/jquery.min.js"></script>
    <script src="js/script.js"></script>
</body>
<!--
    ____  ___________  ______ ____________
   / __ \/ ____// __ \/ ____// ___// ____/\
  / / / / __/ // / / /\__ \ / __/ / /\ ___\/
 / /_/ / /___// /_/ /___/ // /___/ /_/__
/_____/_____//_____//____//_____/\_____/\
\ _____\\____\\\____\\____\\_____\_\____\/

       -- Who else is listening? --
-->
</html>

<?php
$conn->close();
?>