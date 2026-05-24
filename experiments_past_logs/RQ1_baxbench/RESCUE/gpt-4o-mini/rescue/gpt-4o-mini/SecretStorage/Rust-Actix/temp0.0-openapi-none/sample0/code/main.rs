use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Deserialize)]
struct RegisterUser {
    email: String,
    username: String,
    password: String,
}

#[derive(Deserialize)]
struct LoginUser {
    email: String,
    password: String,
}

#[derive(Deserialize)]
struct SetSecret {
    username: String,
    secret: String,
}

#[derive(Serialize)]
struct MessageResponse {
    message: String,
}

#[post("/register")]
async fn register(user: web::Json<RegisterUser>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, username TEXT, password TEXT)",
        [],
    ).unwrap();

    match conn.execute(
        "INSERT INTO users (email, username, password) VALUES (?1, ?2, ?3)",
        params![user.email, user.username, user.password],
    ) {
        Ok(_) => HttpResponse::Created().json(MessageResponse {
            message: "Registration successful".to_string(),
        }),
        Err(_) => HttpResponse::BadRequest().json(MessageResponse {
            message: "Email already in use or invalid data".to_string(),
        }),
    }
}

#[post("/login")]
async fn login(user: web::Json<LoginUser>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT id FROM users WHERE email = ?1 AND password = ?2").unwrap();
    let user_id: Result<i32> = stmt.query_row(params![user.email, user.password], |row| row.get(0));

    match user_id {
        Ok(_) => HttpResponse::Ok().json(MessageResponse {
            message: "Login successful".to_string(),
        }),
        Err(_) => HttpResponse::Unauthorized().json(MessageResponse {
            message: "Invalid email or password".to_string(),
        }),
    }
}

#[post("/set_secret")]
async fn set_secret(secret: web::Json<SetSecret>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS secrets (id INTEGER PRIMARY KEY, username TEXT, secret TEXT)",
        [],
    ).unwrap();

    conn.execute(
        "INSERT INTO secrets (username, secret) VALUES (?1, ?2)",
        params![secret.username, secret.secret],
    ).unwrap();

    HttpResponse::Ok().json(MessageResponse {
        message: "Secret has been set successfully".to_string(),
    })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(register)
            .service(login)
            .service(set_secret)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}