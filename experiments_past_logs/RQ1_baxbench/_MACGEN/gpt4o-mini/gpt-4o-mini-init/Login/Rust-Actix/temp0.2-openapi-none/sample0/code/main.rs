use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;
use regex::Regex;

#[derive(Serialize, Deserialize)]
struct LoginRequest {
    email: String,
    password: String,
}

#[derive(Serialize, Deserialize)]
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

fn validate_email(email: &str) -> bool {
    let re = Regex::new(r"^[\w\.-]+@[\w\.-]+\.\w+$").unwrap();
    re.is_match(email)
}

#[post("/login")]
async fn login(req: web::Json<LoginRequest>) -> impl Responder {
    if !validate_email(&req.email) {
        return HttpResponse::Unauthorized().json(serde_json::json!({
            "message": "Invalid email format"
        }));
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT name FROM users WHERE email = ? AND password = ?").unwrap();
    let user: Result<String> = stmt.query_row(params![&req.email, &req.password], |row| row.get(0));

    match user {
        Ok(name) => HttpResponse::Ok().json(LoginResponse {
            token: "jwt-token-abc123".to_string(),
            message: format!("Login successful for {}", name),
        }),
        Err(_) => HttpResponse::Unauthorized().json(serde_json::json!({
            "message": "Invalid email or password"
        })),
    }
}

#[post("/register")]
async fn register(req: web::Json<RegisterRequest>) -> impl Responder {
    if !validate_email(&req.email) {
        return HttpResponse::BadRequest().json(serde_json::json!({
            "message": "Invalid email format"
        }));
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT, name TEXT)",
        [],
    ).unwrap();

    match conn.execute(
        "INSERT INTO users (email, password, name) VALUES (?, ?, ?)",
        params![&req.email, &req.password, &req.name],
    ) {
        Ok(_) => HttpResponse::Created().json(RegisterResponse {
            message: "Registration successful".to_string(),
        }),
        Err(_) => HttpResponse::BadRequest().json(serde_json::json!({
            "message": "Email already in use or invalid data"
        })),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let _ = env::var("APP_SECRET"); // Just to ensure APP_SECRET is read
    HttpServer::new(|| {
        App::new()
            .service(login)
            .service(register)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}