use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use uuid::Uuid;

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

async fn invite_user(req: web::Json<InviteUserRequest>) -> impl Responder {
    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };
    let email = &req.email;

    let mut stmt = match conn.prepare("SELECT invite_id FROM invitations WHERE email = ?1") {
        Ok(stmt) => stmt,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };
    let invite_id: Result<String> = stmt.query_row(params![email], |row| row.get(0));

    let invite_id = match invite_id {
        Ok(id) => id,
        Err(_) => {
            let new_invite_id = Uuid::new_v4().to_string();
            if conn.execute(
                "INSERT INTO invitations (email, invite_id) VALUES (?1, ?2)",
                params![email, new_invite_id],
            ).is_err() {
                return HttpResponse::InternalServerError().finish();
            }
            new_invite_id
        }
    };

    HttpResponse::Ok().json(InviteUserResponse {
        invite_id,
        message: "Invitation created or retrieved successfully.".to_string(),
    })
}

async fn create_user(req: web::Json<CreateUserRequest>) -> impl Responder {
    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };
    let invite_id = &req.invite_id;
    let user_name = &req.user_name;

    let mut stmt = match conn.prepare("SELECT email FROM invitations WHERE invite_id = ?1") {
        Ok(stmt) => stmt,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };
    let email: Result<String> = stmt.query_row(params![invite_id], |row| row.get(0));

    match email {
        Ok(_) => {
            let mut stmt = match conn.prepare("SELECT user_name FROM users WHERE user_name = ?1") {
                Ok(stmt) => stmt,
                Err(_) => return HttpResponse::InternalServerError().finish(),
            };
            let user_exists: Result<String> = stmt.query_row(params![user_name], |row| row.get(0));

            if user_exists.is_ok() {
                return HttpResponse::BadRequest().json(CreateUserResponse {
                    message: "Username already exists. Try providing different username.".to_string(),
                });
            }

            if conn.execute(
                "INSERT INTO users (user_name, password) VALUES (?1, ?2)",
                params![user_name, &req.password],
            ).is_err() {
                return HttpResponse::InternalServerError().finish();
            }

            HttpResponse::Ok().json(CreateUserResponse {
                message: "User created successfully.".to_string(),
            })
        }
        Err(_) => HttpResponse::Unauthorized().json(CreateUserResponse {
            message: "Invalid invite_id".to_string(),
        }),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS invitations (
            email TEXT PRIMARY KEY,
            invite_id TEXT NOT NULL
        )",
        [],
    ).unwrap();

    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (
            user_name TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )",
        [],
    ).unwrap();

    HttpServer::new(|| {
        App::new()
            .route("/invite_user", web::post().to(invite_user))
            .route("/create_user", web::post().to(create_user))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}