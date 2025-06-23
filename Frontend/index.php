<?php
session_start();

define('DB_HOST', 'localhost');
define('DB_NAME', 'ciscoLogger');
define('DB_USER', 'logger');
define('DB_PASS', 'logger');

$error = "";
$username_input = "";

try {
    $pdo = new PDO(
        "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=utf8mb4",
        DB_USER,
        DB_PASS
    );
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
} catch (PDOException $e) {
    $error = "Database connection failed. Please try again later.";
}

// --- Handle Login Form Submission ---
// Check if the form was submitted via POST request and if there are no prior database connection errors
if ($_SERVER["REQUEST_METHOD"] === "POST" && empty($error)) {
    // Sanitize and trim user inputs to prevent basic injection and whitespace issues
    $username_input = trim($_POST['username'] ?? '');
    $password_input = trim($_POST['password'] ?? '');

    // Basic input validation: check if fields are empty
    if (empty($username_input) || empty($password_input)) {
        $error = "Please enter both username and password.";
    } else {
        try {
            // Prepare SQL statement to fetch user data.
            // Using prepared statements is crucial to prevent SQL injection attacks.
            $stmt = $pdo->prepare("SELECT id, username, password FROM users WHERE username = :username");
            // Bind the username parameter
            $stmt->bindParam(':username', $username_input, PDO::PARAM_STR);
            // Execute the prepared statement
            $stmt->execute();
            // Fetch the user row
            $user = $stmt->fetch();

            // Verify user and password
            // `password_verify()` is used to check a plain password against a hashed password.
            // This assumes passwords in your database are hashed using `password_hash()`.
            if ($user && password_verify($password_input, $user['password'])) {
                // Successful login
                $_SESSION['username'] = $user['username']; // Store username in session
                $_SESSION['user_id'] = $user['id'];       // Store user ID in session (optional, but good practice)

                // Regenerate session ID to prevent session fixation attacks
                session_regenerate_id(true);

                // Redirect to the dashboard or a protected page
                header("Location: ciscoLogger/index.php");
                exit(); // Always exit after a header redirect
            } else {
                // Invalid credentials
                $error = "Invalid username or password.";
            }
        } catch (PDOException $e) {
            // Handle errors during query execution
            $error = "Login failed. Please try again later.";
            // For debugging: error_log("Login query error: " . $e->getMessage());
        }
    }
}
// Include the login form template, passing error and username variable
include __DIR__ . '/templates/login_form.php';
