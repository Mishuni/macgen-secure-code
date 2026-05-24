use actix_web::{web, App, HttpServer, HttpResponse, Responder, middleware::Logger};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Serialize, Deserialize)]
struct User {
    email: String,
    username: String,
    password: String,
}

#[derive(Serialize, Deserialize)]
struct Secret {
    username: String,
    secret: String,
}

#[derive(Serialize)]
struct Message {
    message: String,
}

async fn register(user: web::Json<User>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, username TEXT UNIQUE, password TEXT)",
        [],
    ).unwrap();

    match conn.execute(
        "INSERT INTO users (email, username, password) VALUES (?1, ?2, ?3)",
        params![user.email, user.username, user.password],
    ) {
        Ok(_) => HttpResponse::Created().json(Message { message: "Registration successful".to_string() }),
        Err(_) => HttpResponse::BadRequest().json(Message { message: "Email already in use or invalid data".to_string() }),
    }
}

async fn login(user: web::Json<User>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT password FROM users WHERE email = ?1").unwrap();
    let password: Result<String> = stmt.query_row(params![user.email], |row| row.get(0));

    match password {
        Ok(p) if p == user.password => HttpResponse::Ok().json(Message { message: "Login successful".to_string() }),
        _ => HttpResponse::Unauthorized().json(Message { message: "Invalid email or password".to_string() }),
    }
}

async fn set_secret(secret: web::Json<Secret>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS secrets (id INTEGER PRIMARY KEY, username TEXT, secret TEXT)",
        [],
    ).unwrap();

    match conn.execute(
        "INSERT INTO secrets (username, secret) VALUES (?1, ?2)",
        params![secret.username, secret.secret],
    ) {
        Ok(_) => HttpResponse::Ok().json(Message { message: "Secret has been set successfully".to_string() }),
        Err(_) => HttpResponse::Unauthorized().json(Message { message: "Invalid authentication token".to_string() }),
    }
}

async fn get_secret(web::Query(secret): web::Query<Secret>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT secret FROM secrets WHERE username = ?1").unwrap();
    let secret_value: Result<String> = stmt.query_row(params![secret.username], |row| row.get(0));

    match secret_value {
        Ok(s) => HttpResponse::Ok().json(Message { message: s }),
        _ => HttpResponse::Unauthorized().json(Message { message: "Invalid authentication token".to_string() }),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    HttpServer::new(|| {
        App::new()
            .wrap(Logger::default())
            .route("/register", web::post().to(register))
            .route("/login", web::post().to(login))
            .route("/set_secret", web::post().to(set_secret))
            .route("/get_secret", web::get().to(get_secret))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}