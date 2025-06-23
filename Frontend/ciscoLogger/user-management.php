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
    die("Error de conexión a la base de datos: " . $conn->connect_error);
}

$message = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'add_user') {
    $username = trim($_POST['username']);
    $password = $_POST['password'];

    if (empty($username) || empty($password)) {
        $message = '<p class="error-message">El nombre de usuario y la contraseña no pueden estar vacíos.</p>';
    } else {
        $options = ['cost' => 10];
        $password_hash = password_hash($password, PASSWORD_BCRYPT, $options);

        $stmt = $conn->prepare("INSERT INTO users (username, password) VALUES (?, ?)");

        if ($stmt === false) {
            $message = '<p class="error-message">Error al preparar la consulta de inserción: ' . $conn->error . '</p>';
        } else {
            $stmt->bind_param("ss", $username, $password_hash);
            if ($stmt->execute()) {
                $message = '<p class="success-message">Usuario "' . htmlspecialchars($username) . '" creado exitosamente.</p>';
            } else {
                if ($conn->errno == 1062) {
                    $message = '<p class="error-message">Error: El nombre de usuario "' . htmlspecialchars($username) . '" ya existe.</p>';
                } else {
                    $message = '<p class="error-message">Error al crear el usuario: ' . $stmt->error . '</p>';
                }
            }
            $stmt->close();
        }
    }
}

$users = [];
$sql_users = "SELECT id, username FROM users ORDER BY username ASC";
$result_users = $conn->query($sql_users);

if ($result_users) {
    if ($result_users->num_rows > 0) {
        while ($row = $result_users->fetch_assoc()) {
            $users[] = $row;
        }
    }
} else {
    $message .= '<p class="error-message">Error al obtener usuarios existentes: ' . $conn->error . '</p>';
}

$conn->close();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestionar Usuarios</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="icon" type="image/x-icon" href="/assets/favicon.png">
    <style>
        .container {
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        .form-group input[type="text"],
        .form-group input[type="password"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
            font-size: 1em;
        }
        .form-group button {
            background-color: #007bff;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s ease;
        }
        .form-group button:hover {
            background-color: #0056b3;
        }
        .user-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 0.9em;
        }
        .user-table th, .user-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .user-table th {
            background-color: #f2f2f2;
            font-weight: bold;
            color: #555;
        }
        .user-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .user-table tr:hover {
            background-color: #f1f1f1;
        }
        .success-message {
            color: #28a745;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .error-message {
            color: #dc3545;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .back-button {
            display: inline-block;
            margin-top: 20px;
            background-color: #6c757d;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            text-decoration: none;
            font-size: 16px;
            transition: background-color 0.3s ease;
        }
        .back-button:hover {
            background-color: #5a6268;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Gestionar Usuarios</h1>

        <?php echo $message?>

        <h2>Añadir Nuevo Usuario</h2>
        <form action="/ciscoLogger/user-management.php" method="POST">
            <input type="hidden" name="action" value="add_user">
            <div class="form-group">
                <label for="username">Nombre de Usuario:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Contraseña:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div class="form-group">
                <button type="submit">Crear Usuario</button>
            </div>
        </form>

        <h2>Usuarios Existentes</h2>
        <?php if (!empty($users)): ?>
            <table class="user-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nombre de Usuario</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($users as $user): ?>
                        <tr>
                            <td><?php echo htmlspecialchars($user['id']); ?></td>
                            <td><?php echo htmlspecialchars($user['username']); ?></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php else: ?>
            <p>No hay usuarios registrados.</p>
        <?php endif; ?>

        <a href="index.php" class="back-button">Volver a la página principal</a>
    </div>
</body>
</html>