use actix_web::{web, App, HttpServer, Responder, HttpResponse, middleware};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection};
use std::env;

// Structs for request and response bodies
#[derive(Deserialize)]
struct LoginRequest {
    email: String,
    password: String,
}

#[derive(Serialize)]
struct LoginResponse {
    token: String,
    message: String,
}

#[derive(Deserialize)]
struct RegisterRequest {
    email: String,
    password: String,
    name: String,
}

#[derive(Serialize)]
struct RegisterResponse {
    message: String,
}

#[derive(Serialize)]
struct ErrorResponse {
    message: String,
}

// Initialize SQLite database
fn init_db() {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )",
        [],
    )
    .expect("Failed to create users table");
}

// Handler for user login
async fn login(data: web::Json<LoginRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");

    let mut stmt = conn
        .prepare("SELECT password FROM users WHERE email = ?")
        .expect("Failed to prepare query");

    let stored_password: Result<String, _> = stmt.query_row(params![data.email], |row| row.get(0));

    match stored_password {
        Ok(password) => {
            if password == data.password {
                HttpResponse::Ok().json(LoginResponse {
                    token: "jwt-token-abc123".to_string(),
                    message: "Login successful".to_string(),
                })
            } else {
                HttpResponse::Unauthorized().json(ErrorResponse {
                    message: "Invalid email or password".to_string(),
                })
            }
        }
        Err(_) => HttpResponse::Unauthorized().json(ErrorResponse {
            message: "Invalid email or password".to_string(),
        }),
    }
}

// Handler for user registration
async fn register(data: web::Json<RegisterRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");

    let result = conn.execute(
        "INSERT INTO users (email, password, name) VALUES (?, ?, ?)",
        params![data.email, data.password, data.name],
    );

    match result {
        Ok(_) => HttpResponse::Created().json(RegisterResponse {
            message: "Registration successful".to_string(),
        }),
        Err(_) => HttpResponse::BadRequest().json(ErrorResponse {
            message: "Email already in use or invalid data".to_string(),
        }),
    }
}

// Main function to start the server
#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize logging
    env_logger::init();

    // Initialize the database
    init_db();

    // Get the application secret from the environment
    let app_secret = env::var("APP_SECRET").expect("APP_SECRET environment variable not set");

    println!("Using APP_SECRET: {}", app_secret);

    // Start the server
    HttpServer::new(|| {
        App::new()
            .wrap(middleware::Logger::default())
            .route("/login", web::post().to(login))
            .route("/register", web::post().to(register))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}