use actix_web::{web, App, HttpResponse, HttpServer, Responder};
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

#[derive(Serialize)]
struct ErrorResponse {
    message: String,
}

async fn login(req: web::Json<LoginRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    let mut stmt = conn.prepare("SELECT password FROM users WHERE email = ?1").expect("Failed to prepare statement");
    let mut rows = stmt.query(params![req.email]).expect("Failed to execute query");

    if let Some(row) = rows.next().expect("Failed to fetch row") {
        let stored_password: String = row.get(0).expect("Failed to get password");
        if stored_password == req.password {
            let response = LoginResponse {
                token: "jwt-token-abc123".to_string(),
                message: "Login successful".to_string(),
            };
            return HttpResponse::Ok().json(response);
        }
    }
    
    let response = ErrorResponse {
        message: "Invalid email or password".to_string(),
    };
    HttpResponse::Unauthorized().json(response)
}

async fn register(req: web::Json<RegisterRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    let result = conn.execute(
        "INSERT INTO users (email, password, name) VALUES (?1, ?2, ?3)",
        params![req.email, req.password, req.name],
    );

    match result {
        Ok(_) => {
            let response = RegisterResponse {
                message: "Registration successful".to_string(),
            };
            HttpResponse::Created().json(response)
        }
        Err(_) => {
            let response = ErrorResponse {
                message: "Email already in use or invalid data".to_string(),
            };
            HttpResponse::BadRequest().json(response)
        }
    }
}

fn init_db() -> Result<Connection> {
    let conn = Connection::open("db.sqlite3")?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )",
        [],
    )?;
    Ok(conn)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize the database
    init_db().expect("Failed to initialize the database");

    // Start the web server
    HttpServer::new(|| {
        App::new()
            .route("/login", web::post().to(login))
            .route("/register", web::post().to(register))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}