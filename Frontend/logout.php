<?php
session_start(); // Start the session

// Unset all of the session variables
$_SESSION = array();

// Destroy the session.
session_destroy();

// Redirect to the login page after logging out
header("Location: index.php");
exit();
?>