use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;
use log::{info, error};

#[derive(Serialize, Deserialize)]
struct UserRegistration {
    email: String,
    password: String,
    name: String,
}

#[derive(Serialize, Deserialize)]
struct UserLogin {
    email: String,
    password: String,
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

async fn register_user(user: web::Json<UserRegistration>) -> impl Responder {
    let conn = establish_connection().unwrap();
    let result = conn.execute(
        "INSERT INTO users (email, password, name) VALUES (?1, ?2, ?3)",
        params![user.email, user.password, user.name],
    );

    match result {
        Ok(_) => {
            info!("User registered: {}", user.email);
            HttpResponse::Created().json(ResponseMessage {
                message: "Registration successful".to_string(),
            })
        }
        Err(_) => {
            error!("Failed to register user: {}", user.email);
            HttpResponse::BadRequest().json(ResponseMessage {
                message: "Email already in use or invalid data".to_string(),
            })
        }
    }
}

async fn login_user(user: web::Json<UserLogin>) -> impl Responder {
    let conn = establish_connection().unwrap();
    let mut stmt = conn.prepare("SELECT name FROM users WHERE email = ?1 AND password = ?2").unwrap();
    let user_iter = stmt.query_map(params![user.email, user.password], |row| {
        row.get::<_, String>(0)
    });

    match user_iter {
        Ok(mut rows) => {
            if let Some(Ok(name)) = rows.next() {
                info!("User logged in: {}", user.email);
                HttpResponse::Ok().json(LoginResponse {
                    token: "jwt-token-abc123".to_string(),
                    message: "Login successful".to_string(),
                })
            } else {
                error!("Invalid login attempt for: {}", user.email);
                HttpResponse::Unauthorized().json(ResponseMessage {
                    message: "Invalid email or password".to_string(),
                })
            }
        }
        Err(_) => {
            error!("Database query failed for: {}", user.email);
            HttpResponse::InternalServerError().finish()
        }
    }
}

fn establish_connection() -> Result<Connection> {
    let conn = Connection::open("db.sqlite3")?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )",
        [],
    )?;
    Ok(conn)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env::set_var("RUST_LOG", "info");
    env_logger::init();

    establish_connection().unwrap();

    HttpServer::new(|| {
        App::new()
            .route("/register", web::post().to(register_user))
            .route("/login", web::post().to(login_user))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}