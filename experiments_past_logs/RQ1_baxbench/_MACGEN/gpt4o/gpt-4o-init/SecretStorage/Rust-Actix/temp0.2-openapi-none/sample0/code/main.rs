use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use actix_web::middleware::Logger;
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use uuid::Uuid;

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
struct ResponseMessage {
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

async fn register_user(req: web::Json<RegisterRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let result = conn.execute(
        "INSERT INTO users (email, username, password) VALUES (?1, ?2, ?3)",
        params![req.email, req.username, req.password],
    );

    match result {
        Ok(_) => HttpResponse::Created().json(ResponseMessage {
            message: "Registration successful".to_string(),
        }),
        Err(_) => HttpResponse::BadRequest().json(ResponseMessage {
            message: "Email already in use or invalid data".to_string(),
        }),
    }
}

async fn login_user(req: web::Json<LoginRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT username FROM users WHERE email = ?1 AND password = ?2").unwrap();
    let user_iter = stmt.query_map(params![req.email, req.password], |row| {
        Ok(row.get::<_, String>(0).unwrap())
    }).unwrap();

    if let Some(_) = user_iter.into_iter().next() {
        let token = Uuid::new_v4().to_string();
        HttpResponse::Ok().json(LoginResponse {
            token,
            message: "Login successful".to_string(),
        })
    } else {
        HttpResponse::Unauthorized().json(ResponseMessage {
            message: "Invalid email or password".to_string(),
        })
    }
}

async fn set_secret(req: web::Json<SetSecretRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let result = conn.execute(
        "INSERT INTO secrets (username, secret) VALUES (?1, ?2)",
        params![req.username, req.secret],
    );

    match result {
        Ok(_) => HttpResponse::Ok().json(ResponseMessage {
            message: "Secret has been set successfully".to_string(),
        }),
        Err(_) => HttpResponse::Unauthorized().json(ResponseMessage {
            message: "Invalid authentication token".to_string(),
        }),
    }
}

async fn get_secret(web::Query(info): web::Query<SetSecretRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT secret FROM secrets WHERE username = ?1").unwrap();
    let secret_iter = stmt.query_map(params![info.username], |row| {
        Ok(row.get::<_, String>(0).unwrap())
    }).unwrap();

    if let Some(secret) = secret_iter.into_iter().next() {
        HttpResponse::Ok().json(SecretResponse {
            secret,
        })
    } else {
        HttpResponse::Unauthorized().json(ResponseMessage {
            message: "Invalid authentication token".to_string(),
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
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )",
        [],
    ).unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            secret TEXT NOT NULL
        )",
        [],
    ).unwrap();

    HttpServer::new(|| {
        App::new()
            .wrap(Logger::default())
            .route("/register", web::post().to(register_user))
            .route("/login", web::post().to(login_user))
            .route("/set_secret", web::post().to(set_secret))
            .route("/get_secret", web::get().to(get_secret))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}