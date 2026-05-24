use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;
use uuid::Uuid;
use regex::Regex;
use bcrypt::{hash, verify};

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

fn validate_email(email: &str) -> bool {
    let re = Regex::new(r"^[\w\.-]+@[\w\.-]+\.\w+$").unwrap();
    re.is_match(email)
}

fn validate_user_name(user_name: &str) -> bool {
    user_name.len() >= 3 && user_name.len() <= 30 // Example length validation
}

#[post("/invite_user")]
async fn invite_user(req: web::Json<InviteRequest>) -> impl Responder {
    if !validate_email(&req.email) {
        return HttpResponse::BadRequest().json(InviteResponse {
            invite_id: String::new(),
            message: "Invalid email format.".to_string(),
        });
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    let email = req.email.clone();
    let invite_id = Uuid::new_v4().to_string();

    // Check if the email already has an invitation
    let mut stmt = conn.prepare("SELECT invite_id FROM invites WHERE email = ?").unwrap();
    let existing_invite: Result<String> = stmt.query_row(params![email], |row| row.get(0));

    if existing_invite.is_ok() {
        // If an invitation already exists, return the existing invite_id
        return HttpResponse::Ok().json(InviteResponse {
            invite_id: existing_invite.unwrap(),
            message: "Invitation already exists.".to_string(),
        });
    }

    // Insert new invitation
    conn.execute(
        "INSERT INTO invites (email, invite_id) VALUES (?1, ?2)",
        params![email, invite_id],
    ).unwrap();

    HttpResponse::Ok().json(InviteResponse {
        invite_id,
        message: "Invitation email sent.".to_string(),
    })
}

#[post("/create_user")]
async fn create_user(req: web::Json<CreateUserRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let invite_id = req.invite_id.clone();
    let user_name = req.user_name.clone();
    let password = req.password.clone();

    // Check if the invite_id is valid
    let mut stmt = conn.prepare("SELECT email FROM invites WHERE invite_id = ?").unwrap();
    let email_result: Result<String> = stmt.query_row(params![invite_id], |row| row.get(0));

    if email_result.is_err() {
        return HttpResponse::Unauthorized().json(CreateUserResponse {
            message: "Invalid invite_id".to_string(),
        });
    }

    // Validate username
    if !validate_user_name(&user_name) {
        return HttpResponse::BadRequest().json(CreateUserResponse {
            message: "Username must be between 3 and 30 characters.".to_string(),
        });
    }

    // Check if the username already exists
    let mut stmt = conn.prepare("SELECT user_name FROM users WHERE user_name = ?").unwrap();
    let user_exists: Result<String> = stmt.query_row(params![user_name], |row| row.get(0));

    if user_exists.is_ok() {
        return HttpResponse::BadRequest().json(CreateUserResponse {
            message: "Username already exists. Try providing a different username.".to_string(),
        });
    }

    // Create new user with password validation
    if password.is_empty() {
        return HttpResponse::BadRequest().json(CreateUserResponse {
            message: "Password cannot be empty.".to_string(),
        });
    }

    // Hash the password before storing
    let hashed_password = hash(&password, 4).unwrap();

    conn.execute(
        "INSERT INTO users (user_name, password) VALUES (?1, ?2)",
        params![user_name, hashed_password],
    ).unwrap();

    HttpResponse::Ok().json(CreateUserResponse {
        message: "User created.".to_string(),
    })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize the database
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS invites (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL,
            invite_id TEXT NOT NULL UNIQUE
        )",
        [],
    ).unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_name TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )",
        [],
    ).unwrap();

    // Start the web server
    HttpServer::new(|| {
        App::new()
            .service(invite_user)
            .service(create_user)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}