use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;
use uuid::Uuid;
use regex::Regex;

#[derive(Serialize, Deserialize)]
struct InviteRequest {
    email: String,
}

#[derive(Serialize, Deserialize)]
struct InviteResponse {
    invite_id: String,
    message: String,
}

#[derive(Serialize, Deserialize)]
struct CreateUserRequest {
    invite_id: String,
    user_name: String,
    password: String,
}

#[derive(Serialize, Deserialize)]
struct CreateUserResponse {
    message: String,
}

#[derive(Serialize, Deserialize)]
struct ErrorResponse {
    message: String,
}

fn init_db() -> Result<Connection> {
    let conn = Connection::open("db.sqlite3")?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS invitations (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL UNIQUE
        )",
        [],
    )?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )",
        [],
    )?;
    Ok(conn)
}

fn is_valid_email(email: &str) -> bool {
    let email_regex = Regex::new(r"^[\w\.-]+@[\w\.-]+\.\w+$").unwrap();
    email_regex.is_match(email)
}

#[post("/invite_user")]
async fn invite_user(req: web::Json<InviteRequest>) -> impl Responder {
    let conn = init_db().expect("Failed to initialize database");
    let email = req.email.clone();

    if !is_valid_email(&email) {
        return HttpResponse::BadRequest().json(ErrorResponse {
            message: "Invalid email format".to_string(),
        });
    }

    let mut stmt = conn.prepare("SELECT id FROM invitations WHERE email = ?1").expect("Failed to prepare statement");
    let invite_id: Option<String> = stmt.query_row(params![email], |row| row.get(0)).optional().expect("Failed to query invitation");

    let invite_id = match invite_id {
        Some(id) => id,
        None => {
            let new_id = Uuid::new_v4().to_string();
            conn.execute("INSERT INTO invitations (id, email) VALUES (?1, ?2)", params![new_id, email]).expect("Failed to insert invitation");
            new_id
        }
    };

    HttpResponse::Ok().json(InviteResponse {
        invite_id,
        message: "Invitation email prepared".to_string(),
    })
}

#[post("/create_user")]
async fn create_user(req: web::Json<CreateUserRequest>) -> impl Responder {
    let conn = init_db().expect("Failed to initialize database");
    let invite_id = req.invite_id.clone();
    let user_name = req.user_name.clone();
    let password = req.password.clone();

    let mut stmt = conn.prepare("SELECT email FROM invitations WHERE id = ?1").expect("Failed to prepare statement");
    let email_exists: Option<String> = stmt.query_row(params![invite_id], |row| row.get(0)).optional().expect("Failed to query invitation");

    if email_exists.is_none() {
        return HttpResponse::Unauthorized().json(ErrorResponse {
            message: "Invalid invite_id".to_string(),
        });
    }

    let mut stmt = conn.prepare("SELECT user_name FROM users WHERE user_name = ?1").expect("Failed to prepare statement");
    let user_exists: Option<String> = stmt.query_row(params![user_name], |row| row.get(0)).optional().expect("Failed to query user");

    if user_exists.is_some() {
        return HttpResponse::BadRequest().json(ErrorResponse {
            message: "Username already exists. Try providing different username.".to_string(),
        });
    }

    if password.len() < 6 {
        return HttpResponse::BadRequest().json(ErrorResponse {
            message: "Password must be at least 6 characters long.".to_string(),
        });
    }

    conn.execute("INSERT INTO users (user_name, password) VALUES (?1, ?2)", params![user_name, password]).expect("Failed to insert user");

    HttpResponse::Ok().json(CreateUserResponse {
        message: "User created".to_string(),
    })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env::var("APP_SECRET").expect("APP_SECRET must be set");
    HttpServer::new(|| {
        App::new()
            .service(invite_user)
            .service(create_user)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}