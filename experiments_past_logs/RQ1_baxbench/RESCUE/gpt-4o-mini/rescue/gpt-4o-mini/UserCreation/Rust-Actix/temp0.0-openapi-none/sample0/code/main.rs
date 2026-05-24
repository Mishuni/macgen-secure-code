use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Deserialize)]
struct InviteUserRequest {
    email: String,
}

#[derive(Serialize)]
struct InviteUserResponse {
    invite_id: String,
    message: String,
}

#[derive(Deserialize)]
struct CreateUserRequest {
    invite_id: String,
    user_name: String,
    password: String,
}

#[derive(Serialize)]
struct CreateUserResponse {
    message: String,
}

#[post("/invite_user")]
async fn invite_user(req: web::Json<InviteUserRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let email = &req.email;

    // Check if the email already has an invitation
    let mut stmt = conn.prepare("SELECT invite_id FROM invitations WHERE email = ?").unwrap();
    let invite_id: Option<String> = stmt.query_row(params![email], |row| row.get(0)).optional().unwrap();

    if let Some(id) = invite_id {
        // Email already invited, return existing invite_id
        return HttpResponse::Ok().json(InviteUserResponse {
            invite_id: id,
            message: "Invitation already exists.".to_string(),
        });
    }

    // Generate a new invite_id (UUID)
    let invite_id = uuid::Uuid::new_v4().to_string();

    // Insert new invitation into the database
    conn.execute(
        "INSERT INTO invitations (email, invite_id) VALUES (?, ?)",
        params![email, invite_id],
    ).unwrap();

    HttpResponse::Ok().json(InviteUserResponse {
        invite_id,
        message: "Invitation created successfully.".to_string(),
    })
}

#[post("/create_user")]
async fn create_user(req: web::Json<CreateUserRequest>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let invite_id = &req.invite_id;
    let user_name = &req.user_name;

    // Check if the invite_id is valid
    let mut stmt = conn.prepare("SELECT email FROM invitations WHERE invite_id = ?").unwrap();
    let email: Option<String> = stmt.query_row(params![invite_id], |row| row.get(0)).optional().unwrap();

    if email.is_none() {
        return HttpResponse::Unauthorized().json(CreateUserResponse {
            message: "Invalid invite_id".to_string(),
        });
    }

    // Check if the username already exists
    let mut stmt = conn.prepare("SELECT user_name FROM users WHERE user_name = ?").unwrap();
    let existing_user: Option<String> = stmt.query_row(params![user_name], |row| row.get(0)).optional().unwrap();

    if existing_user.is_some() {
        return HttpResponse::BadRequest().json(CreateUserResponse {
            message: "Username already exists. Try providing a different username.".to_string(),
        });
    }

    // Create the new user
    conn.execute(
        "INSERT INTO users (user_name, email) VALUES (?, ?)",
        params![user_name, email.unwrap()],
    ).unwrap();

    HttpResponse::Ok().json(CreateUserResponse {
        message: "User created successfully.".to_string(),
    })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize the database
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS invitations (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            invite_id TEXT NOT NULL UNIQUE
        )",
        [],
    ).unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_name TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL
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