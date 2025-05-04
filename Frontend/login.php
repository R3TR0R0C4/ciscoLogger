<?php
session_start();

// Simulated user credentials
$valid_username = "user";
$valid_password = "password";

// Initialize error message and username variable
$error = "";
$username = "";

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $username = trim($_POST['username'] ?? '');
    $password = trim($_POST['password'] ?? '');

    // Simple validation
    if ($username === $valid_username && $password === $valid_password) {
        // Successful login
        $_SESSION['username'] = $username;
        header("Location: dashboard.php");
        exit();
    } else {
        $error = "Invalid username or password.";
    }
}

// Include the login form template, passing error and username variable
include __DIR__ . '/templates/login_form.php';
