use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection};
use std::env;
use uuid::Uuid;

// Structs for request and response payloads
#[derive(Deserialize)]
struct RegisterRequest {
    email: String,
    username: String,
    password: String,
}

#[derive(Deserialize)]
struct LoginRequest {
    email: String,
    password: String,
}

#[derive(Deserialize)]
struct SetSecretRequest {
    username: String,
    secret: String,
}

#[derive(Serialize)]
struct ApiResponse {
    message: String,
}

#[derive(Serialize)]
struct LoginResponse {
    token: String,
    message: String,
}

#[derive(Serialize)]
struct SecretResponse {
    secret: String,
}

// Initialize SQLite database
fn init_db() {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )",
        [],
    )
    .expect("Failed to create users table");

    conn.execute(
        "CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            secret TEXT NOT NULL,
            FOREIGN KEY(username) REFERENCES users(username)
        )",
        [],
    )
    .expect("Failed to create secrets table");
}

// Handlers
async fn register_user(req: web::Json<RegisterRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");

    let result = conn.execute(
        "INSERT INTO users (email, username, password) VALUES (?1, ?2, ?3)",
        params![req.email, req.username, req.password],
    );

    match result {
        Ok(_) => HttpResponse::Created().json(ApiResponse {
            message: "Registration successful".to_string(),
        }),
        Err(_) => HttpResponse::BadRequest().json(ApiResponse {
            message: "Email already in use or invalid data".to_string(),
        }),
    }
}

async fn login_user(req: web::Json<LoginRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");

    let mut stmt = conn
        .prepare("SELECT email FROM users WHERE email = ?1 AND password = ?2")
        .expect("Failed to prepare query");

    let mut rows = stmt
        .query(params![req.email, req.password])
        .expect("Failed to execute query");

    if let Some(_) = rows.next().expect("Failed to fetch row") {
        let token = Uuid::new_v4().to_string();
        HttpResponse::Ok().json(LoginResponse {
            token,
            message: "Login successful".to_string(),
        })
    } else {
        HttpResponse::Unauthorized().json(ApiResponse {
            message: "Invalid email or password".to_string(),
        })
    }
}

async fn set_secret(req: web::Json<SetSecretRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");

    let result = conn.execute(
        "INSERT INTO secrets (username, secret) VALUES (?1, ?2)",
        params![req.username, req.secret],
    );

    match result {
        Ok(_) => HttpResponse::Ok().json(ApiResponse {
            message: "Secret has been set successfully".to_string(),
        }),
        Err(_) => HttpResponse::Unauthorized().json(ApiResponse {
            message: "Invalid authentication token".to_string(),
        }),
    }
}

async fn get_secret(query: web::Query<SetSecretRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");

    let mut stmt = conn
        .prepare("SELECT secret FROM secrets WHERE username = ?1")
        .expect("Failed to prepare query");

    let mut rows = stmt
        .query(params![query.username])
        .expect("Failed to execute query");

    if let Some(row) = rows.next().expect("Failed to fetch row") {
        let secret: String = row.get(0).expect("Failed to get secret");
        HttpResponse::Ok().json(SecretResponse { secret })
    } else {
        HttpResponse::Unauthorized().json(ApiResponse {
            message: "Invalid authentication token".to_string(),
        })
    }
}

// Main function
#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    init_db();

    HttpServer::new(|| {
        App::new()
            .route("/register", web::post().to(register_user))
            .route("/login", web::post().to(login_user))
            .route("/set_secret", web::post().to(set_secret))
            .route("/get_secret", web::get().to(get_secret))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}