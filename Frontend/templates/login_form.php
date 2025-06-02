<!DOCTYPE html>
<html lang="en">
<head>
   <meta charset="UTF-8" />
   <meta name="viewport" content="width=device-width, initial-scale=1" />
   <title>Login</title>
   <link rel="stylesheet" href="/assets/css/styles.css" />
   <link rel="icon" type="image/x-icon" href="/assets/favicon.png">

</head>
<body>
   <div class="login-container" role="main">
       <h2 class="ciscoLogger">cisco_logger</h2>
       <?php if (!empty($error)) : ?>
           <div class="error-message" role="alert"><?= htmlspecialchars($error) ?></div>
       <?php endif; ?>
       <form method="POST" action="">
           <div class="input-group">
               <label for="username">Username</label>
               <input
                    type="text"
                    id="username"
                    name="username"
                    required
                    autofocus
                    autocomplete="username"
                    value="<?= htmlspecialchars($username ?? '') ?>"
                />
           </div>
           <div class="input-group">
               <label for="password">Password</label>
               <input
                    type="password"
                    id="password"
                    name="password"
                    required
                    autocomplete="current-password"
                />
           </div>
           <button type="submit" aria-label="Log in">Log In</button>
       </form>
   </div>
</body>
</html>
