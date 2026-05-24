use actix_web::{web, App, HttpServer, HttpResponse, Responder, post};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use uuid::Uuid;
use log::{info, error};
use env_logger;

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

#[post("/login")]
async fn login(data: web::Json<LoginRequest>) -> impl Responder {
    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(err) => {
            error!("Failed to connect to database: {}", err);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let mut stmt = match conn.prepare("SELECT id FROM users WHERE email = ?1 AND password = ?2") {
        Ok(stmt) => stmt,
        Err(err) => {
            error!("Failed to prepare statement: {}", err);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let user_id: Result<String> = stmt.query_row(params![data.email, data.password], |row| row.get(0));

    match user_id {
        Ok(id) => {
            let token = Uuid::new_v4().to_string();
            info!("User {} logged in successfully", id);
            HttpResponse::Ok().json(LoginResponse {
                token,
                message: "Login successful".to_string(),
            })
        }
        Err(_) => {
            HttpResponse::Unauthorized().json(RegisterResponse {
                message: "Invalid email or password".to_string(),
            })
        }
    }
}

#[post("/register")]
async fn register(data: web::Json<RegisterRequest>) -> impl Responder {
    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(err) => {
            error!("Failed to connect to database: {}", err);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let mut stmt = match conn.prepare("SELECT COUNT(*) FROM users WHERE email = ?1") {
        Ok(stmt) => stmt,
        Err(err) => {
            error!("Failed to prepare statement: {}", err);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let count: i64 = match stmt.query_row(params![data.email], |row| row.get(0)) {
        Ok(count) => count,
        Err(err) => {
            error!("Failed to execute query: {}", err);
            return HttpResponse::InternalServerError().finish();
        }
    };

    if count > 0 {
        return HttpResponse::BadRequest().json(RegisterResponse {
            message: "Email already in use".to_string(),
        });
    }

    match conn.execute(
        "INSERT INTO users (email, password, name) VALUES (?1, ?2, ?3)",
        params![data.email, data.password, data.name],
    ) {
        Ok(_) => {
            info!("User {} registered successfully", data.email);
            HttpResponse::Created().json(RegisterResponse {
                message: "Registration successful".to_string(),
            })
        }
        Err(err) => {
            error!("Failed to insert user: {}", err);
            HttpResponse::InternalServerError().finish()
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )",
        [],
    ).expect("Failed to create users table");

    HttpServer::new(|| {
        App::new()
            .service(login)
            .service(register)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}