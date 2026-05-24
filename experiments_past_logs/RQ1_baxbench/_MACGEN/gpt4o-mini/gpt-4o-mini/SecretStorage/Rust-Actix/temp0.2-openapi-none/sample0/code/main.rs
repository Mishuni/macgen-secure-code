use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;
use regex::Regex;

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

fn validate_email(email: &str) -> bool {
    let re = Regex::new(r"^[\w\.-]+@[\w\.-]+\.\w+$").unwrap();
    re.is_match(email)
}

fn validate_username(username: &str) -> bool {
    let re = Regex::new(r"^[a-zA-Z0-9_]+$").unwrap();
    re.is_match(username)
}

async fn register(user: web::Json<User>) -> impl Responder {
    if !validate_email(&user.email) || !validate_username(&user.username) {
        return HttpResponse::BadRequest().json(Message {
            message: "Email already in use or invalid data".to_string(),
        });
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, username TEXT UNIQUE, password TEXT)",
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
    if !validate_email(&user.email) {
        return HttpResponse::Unauthorized().json(Message {
            message: "Invalid email or password".to_string(),
        });
    }

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
    if !validate_username(&secret.username) {
        return HttpResponse::Unauthorized().json(Message {
            message: "Invalid authentication token".to_string(),
        });
    }

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

async fn get_secret(web::Query(secret): web::Query<Secret>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT secret FROM secrets WHERE username = ?1").unwrap();
    let secret_iter = stmt.query_map(params![secret.username], |row| {
        Ok(row.get::<_, String>(0)?)
    }).unwrap();

    if let Some(secret_value) = secret_iter.into_iter().next() {
        match secret_value {
            Ok(secret) => HttpResponse::Ok().json(serde_json::json!({ "secret": secret })),
            Err(_) => HttpResponse::Unauthorized().json(Message {
                message: "Invalid authentication token".to_string(),
            }),
        }
    } else {
        HttpResponse::Unauthorized().json(Message {
            message: "Invalid authentication token".to_string(),
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