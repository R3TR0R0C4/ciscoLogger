<?php
session_start(); // Start the session to access session variables

// Check if the 'username' session variable is NOT set
if (!isset($_SESSION['username'])) {
    // If the user is not logged in, redirect them to the login page.
    // Adjust the path to your index.php file if it's not in the root directory.
    header("Location: /index.php"); // Example: if index.php is in the root
    // header("Location: ../index.php"); // Example: if index.php is one level up
    exit(); // Important: Always exit after a header redirect to prevent further script execution
}

// If the user IS logged in, the script will continue past this point,
// allowing the rest of the content in this file (or included files) to be displayed.

// --- Your ciscoLogger content goes here ---
// For example, you might have:
// echo "Welcome to the Cisco Logger area, " . htmlspecialchars($_SESSION['username']) . "!";
// include 'display_logs.php'; // Include other files specific to ciscoLogger functionality
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cisco Logger</title>
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #e9ecef;
            padding: 20px;
            color: #343a40;
        }
        .container {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 15px rgba(0, 0, 0, 0.08);
            max-width: 800px;
            margin: 20px auto;
        }
        h1 {
            color: #0056b3;
            margin-bottom: 20px;
        }
        p {
            line-height: 1.6;
        }
        .logout-button {
            display: inline-block;
            padding: 10px 20px;
            background-color:rgb(220, 53, 69);
            color: white;
            border: none;
            border-radius: 5px;
            text-decoration: none;
            margin-top: 20px;
            transition: background-color 0.3s ease;
        }
        .logout-button:hover {
            background-color:rgb(200, 35, 51);
        }
        .logger {
            display: inline-block;
            padding: 10px 20px;
            background-color:rgb(53, 111, 220);
            color: white;
            border: none;
            border-radius: 5px;
            text-decoration: none;
            margin-top: 20px;
            margin-right: 20px;
            transition: background-color 0.3s ease;
        }
        .logger:hover {
            background-color:rgb(34, 91, 198);
        }
        .user-management {
            display: inline-block;
            padding: 10px 20px;
            background-color:rgb(53, 111, 220);
            color: white;
            border: none;
            border-radius: 5px;
            text-decoration: none;
            margin-top: 20px;
            margin-right: 20px;
            transition: background-color 0.3s ease;
        }
        .user-management:hover {
            background-color:rgb(34, 91, 198);
        }
    </style>
</head>
<body>
    <div class="container">
        <p>Hello, <?php echo htmlspecialchars($_SESSION['username']); ?></p>
        <table>
            <tr>
                <a href="/ciscoLogger/logger.php" class="logger">Logger</a>
            </tr>
            <tr>
                <a href="/ciscoLogger/user-management.php" class="user-management">Users</a>
            </tr>
            <tr>
                <a href="/logout.php" class="logout-button">Logout</a>
            </tr>

    </div>
</body>
</html>
