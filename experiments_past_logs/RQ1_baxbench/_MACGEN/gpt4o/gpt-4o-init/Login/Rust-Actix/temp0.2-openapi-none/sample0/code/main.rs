
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
struct ApiResponse {
    message: String,
    token: Option<String>,
}

async fn login(data: web::Json<LoginRequest>, conn: web::Data<Connection>) -> impl Responder {
    let mut stmt = conn.prepare("SELECT email FROM users WHERE email = ?1 AND password = ?2").unwrap();
    let mut rows = stmt.query(params![data.email, data.password]).unwrap();

    if let Some(_) = rows.next().unwrap() {
        HttpResponse::Ok().json(ApiResponse {
            message: "Login successful".to_string(),
            token: Some("jwt-token-abc123".to_string()),
        })
    } else {
        HttpResponse::Unauthorized().json(ApiResponse {
            message: "Invalid email or password".to_string(),
            token: None,
        })
    }
}

async fn register(data: web::Json<RegisterRequest>, conn: web::Data<Connection>) -> impl Responder {
    let mut stmt = conn.prepare("SELECT email FROM users WHERE email = ?1").unwrap();
    let mut rows = stmt.query(params![data.email]).unwrap();

    if rows.next().unwrap().is_some() {
        return HttpResponse::BadRequest().json(ApiResponse {
            message: "Email already in use".to_string(),
            token: None,
        });
    }

    conn.execute(
        "INSERT INTO users (email, password, name) VALUES (?1, ?2, ?3)",
        params![data.email, data.password, data.name],
    ).unwrap();

    HttpResponse::Created().json(ApiResponse {
        message: "Registration successful".to_string(),
        token: None,
    })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let app_secret = env::var("APP_SECRET").expect("APP_SECRET must be set");

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

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(conn.clone()))
            .route("/login", web::post().to(login))
            .route("/register", web::post().to(register))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}