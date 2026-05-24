use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Deserialize)]
struct LoginRequest {
    email: String,
    password: String,
}

#[derive(Deserialize)]
struct RegisterRequest {
    email: String,
    password: String,
    name: String,
}

#[derive(Serialize)]
struct LoginResponse {
    token: String,
    message: String,
}

#[derive(Serialize)]
struct RegisterResponse {
    message: String,
}

#[post("/login")]
async fn login(req: web::Json<LoginRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT name FROM users WHERE email = ? AND password = ?").unwrap();
    let user: Result<String> = stmt.query_row(params![&req.email, &req.password], |row| row.get(0));

    match user {
        Ok(name) => {
            let response = LoginResponse {
                token: "jwt-token-abc123".to_string(),
                message: format!("Login successful for {}", name),
            };
            HttpResponse::Ok().json(response)
        }
        Err(_) => {
            HttpResponse::Unauthorized().json(serde_json::json!({
                "message": "Invalid email or password"
            }))
        }
    }
}

#[post("/register")]
async fn register(req: web::Json<RegisterRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let result = conn.execute(
        "INSERT INTO users (email, password, name) VALUES (?1, ?2, ?3)",
        params![&req.email, &req.password, &req.name],
    );

    match result {
        Ok(_) => {
            let response = RegisterResponse {
                message: "Registration successful".to_string(),
            };
            HttpResponse::Created().json(response)
        }
        Err(_) => {
            HttpResponse::BadRequest().json(serde_json::json!({
                "message": "Email already in use or invalid data"
            }))
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize the SQLite database
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )",
        [],
    ).unwrap();

    // Start the Actix web server
    HttpServer::new(|| {
        App::new()
            .service(login)
            .service(register)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}