use actix_web::{web, App, HttpServer, HttpResponse, Responder, post};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
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

async fn login(data: web::Json<LoginRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT * FROM users WHERE email = ?1 AND password = ?2").unwrap();
    let user_exists = stmt.exists(params![data.email, data.password]).unwrap();

    if user_exists {
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

async fn register(data: web::Json<RegisterRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT * FROM users WHERE email = ?1").unwrap();
    let email_exists = stmt.exists(params![data.email]).unwrap();

    if email_exists {
        HttpResponse::BadRequest().json(ErrorResponse {
            message: "Email already in use or invalid data".to_string(),
        })
    } else {
        conn.execute(
            "INSERT INTO users (email, password, name) VALUES (?1, ?2, ?3)",
            params![data.email, data.password, data.name],
        ).unwrap();

        HttpResponse::Created().json(RegisterResponse {
            message: "Registration successful".to_string(),
        })
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

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

    HttpServer::new(|| {
        App::new()
            .service(web::resource("/login").route(post().to(login)))
            .service(web::resource("/register").route(post().to(register)))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}