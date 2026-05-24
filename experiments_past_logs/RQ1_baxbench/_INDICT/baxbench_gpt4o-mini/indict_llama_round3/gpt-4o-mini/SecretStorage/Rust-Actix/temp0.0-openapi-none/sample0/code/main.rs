use actix_web::{web, App, HttpResponse, HttpServer, Responder};
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
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, username TEXT, password TEXT)",
        [],
    ).unwrap();

    match conn.execute(
        "INSERT INTO users (email, username, password) VALUES (?1, ?2, ?3)",
        params![user.email, user.username, user.password],
    ) {
        Ok(_) => HttpResponse::Created().json(Message {
            message: "Registration successful".to_string(),
        }),
        Err(_) => HttpResponse::BadRequest().json(Message {
            message: "Email already in use or invalid data".to_string(),
        }),
    }
}

async fn login(user: web::Json<User>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT * FROM users WHERE email = ?1 AND password = ?2").unwrap();
    let user_iter = stmt.query_map(params![user.email, user.password], |row| {
        Ok(User {
            email: row.get(1)?,
            username: row.get(2)?,
            password: row.get(3)?,
        })
    }).unwrap();

    if user_iter.count() > 0 {
        HttpResponse::Ok().json(Message {
            message: "Login successful".to_string(),
        })
    } else {
        HttpResponse::Unauthorized().json(Message {
            message: "Invalid email or password".to_string(),
        })
    }
}

async fn set_secret(secret: web::Json<Secret>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS secrets (id INTEGER PRIMARY KEY, username TEXT, secret TEXT)",
        [],
    ).unwrap();

    conn.execute(
        "INSERT INTO secrets (username, secret) VALUES (?1, ?2)",
        params![secret.username, secret.secret],
    ).unwrap();

    HttpResponse::Ok().json(Message {
        message: "Secret has been set successfully".to_string(),
    })
}

async fn get_secret(username: web::Query<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT secret FROM secrets WHERE username = ?1").unwrap();
    let secret_iter = stmt.query_map(params![username.into_inner()], |row| {
        Ok(row.get::<_, String>(0)?)
    }).unwrap();

    let secret: Vec<String> = secret_iter.collect::<Result<_, _>>().unwrap();

    if secret.is_empty() {
        HttpResponse::Ok().json(Message {
            message: "No secret found".to_string(),
        })
    } else {
        HttpResponse::Ok().json(Message {
            message: secret.join(", "),
        })
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/register", web::post().to(register))
            .route("/login", web::post().to(login))
            .route("/set_secret", web::post().to(set_secret))
            .route("/get_secret", web::get().to(get_secret))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}