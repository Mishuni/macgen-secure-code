# MyForum

## Setup

1. Run `composer install` to install dependencies.
2. Create the SQLite database by running the migration:
   ```bash
   php artisan migrate
   ```
3. Start the server:
   ```bash
   php -S 0.0.0.0:5000 -t public
   ```
4. Access the application at `http://localhost:5000`.