use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;
use uuid::Uuid;

#[derive(Serialize, Deserialize)]
struct InviteRequest {
    email: String,
}

#[derive(Serialize, Deserialize)]
struct CreateUserRequest {
    invite_id: String,
    user_name: String,
    password: String,
}

#[derive(Serialize)]
struct InviteResponse {
    invite_id: String,
    message: String,
}

#[derive(Serialize)]
struct UserResponse {
    message: String,
}

fn init_db() -> Result<Connection> {
    let conn = Connection::open("db.sqlite3")?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS invitations (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            invite_id TEXT NOT NULL UNIQUE
        )",
        [],
    )?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_name TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            invite_id TEXT NOT NULL,
            FOREIGN KEY (invite_id) REFERENCES invitations(invite_id)
        )",
        [],
    )?;
    Ok(conn)
}

#[post("/invite_user")]
async fn invite_user(invite_request: web::Json<InviteRequest>) -> impl Responder {
    let conn = init_db().unwrap();
    let email = &invite_request.email;

    let mut stmt = conn.prepare("SELECT invite_id FROM invitations WHERE email = ?").unwrap();
    let existing_invite: Result<String> = stmt.query_row(params![email], |row| row.get(0));

    let invite_id = match existing_invite {
        Ok(id) => id,
        Err(_) => {
            let new_invite_id = Uuid::new_v4().to_string();
            conn.execute(
                "INSERT INTO invitations (email, invite_id) VALUES (?, ?)",
                params![email, new_invite_id],
            ).unwrap();
            new_invite_id
        }
    };

    let response = InviteResponse {
        invite_id,
        message: "Invitation email prepared.".to_string(),
    };

    HttpResponse::Ok().json(response)
}

#[post("/create_user")]
async fn create_user(create_user_request: web::Json<CreateUserRequest>) -> impl Responder {
    let conn = init_db().unwrap();
    let invite_id = &create_user_request.invite_id;
    let user_name = &create_user_request.user_name;

    let mut stmt = conn.prepare("SELECT invite_id FROM invitations WHERE invite_id = ?").unwrap();
    let valid_invite: Result<String> = stmt.query_row(params![invite_id], |row| row.get(0));

    if valid_invite.is_err() {
        return HttpResponse::Unauthorized().json(UserResponse {
            message: "Invalid invite_id".to_string(),
        });
    }

    let mut stmt = conn.prepare("SELECT user_name FROM users WHERE user_name = ?").unwrap();
    let existing_user: Result<String> = stmt.query_row(params![user_name], |row| row.get(0));

    if existing_user.is_ok() {
        return HttpResponse::BadRequest().json(UserResponse {
            message: "Username already exists. Try providing a different username.".to_string(),
        });
    }

    conn.execute(
        "INSERT INTO users (user_name, password, invite_id) VALUES (?, ?, ?)",
        params![user_name, create_user_request.password, invite_id],
    ).unwrap();

    HttpResponse::Ok().json(UserResponse {
        message: "User created".to_string(),
    })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    HttpServer::new(|| {
        App::new()
            .service(invite_user)
            .service(create_user)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}