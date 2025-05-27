<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cisco Switch Logging</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="icon" type="image/x-icon" href="/assets/favicon.png">
</head>
<body>
    <div class="header-container">
      <h1>Cisco Switch Interface Logs</h1>
      <a href="mac_search.php" class="button">MAC</a>
    </div>

    <div id="tabs-container">
        <?php

        session_start(); // Start the session to access session variables

        // Check if the 'username' session variable is NOT set
        if (!isset($_SESSION['username'])) {
            // If the user is not logged in, redirect them to the login page.
            header("Location: /login.php"); // Adjust path as needed
            exit(); // Important: Always exit after a header redirect
        }


        // Database configuration (replace with your actual credentials)
        $db_host = 'localhost';
        $db_user = 'user';
        $db_pass = 'password';
        $db_name = 'ciscoLogger';

        $conn = new mysqli($db_host, $db_user, $db_pass, $db_name);

        if ($conn->connect_error) {
            die("Connection failed: " . $conn->connect_error);
        }

        $switches_data = [];
        // **** MODIFIED QUERY HERE ****
        $sql_switches = "SELECT ip_address, hostname FROM network_devices ORDER BY ip_address ASC";
        $result_switches = $conn->query($sql_switches);

        if ($result_switches && $result_switches->num_rows > 0) {
            while ($row = $result_switches->fetch_assoc()) {
                $switches_data[] = [
                    'ip' => htmlspecialchars($row['ip_address']), // Use ip_address from network_devices
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
</html>

<?php
$conn->close();
?>