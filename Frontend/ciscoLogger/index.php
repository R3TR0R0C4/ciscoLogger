<?php
session_start();
if (!isset($_SESSION['username'])) {
    header("Location: /index.php");
    exit();
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/x-icon" href="/assets/favicon.png">
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
