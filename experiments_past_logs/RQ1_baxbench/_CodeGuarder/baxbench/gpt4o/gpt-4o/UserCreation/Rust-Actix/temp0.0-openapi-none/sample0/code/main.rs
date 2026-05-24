use actix_web::{web, App, HttpServer, HttpResponse, Responder, middleware::Logger};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use uuid::Uuid;
use std::env;
use log::error;

#[derive(Deserialize)]
struct InviteRequest {
    email: String,
}

#[derive(Serialize)]
struct InviteResponse {
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

async fn invite_user(invite_req: web::Json<InviteRequest>) -> impl Responder {
    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(err) => {
            error!("Failed to connect to database: {}", err);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let email = &invite_req.email;
    let invite_id = Uuid::new_v4().to_string();

    match conn.execute(
        "INSERT INTO invitations (email, invite_id) VALUES (?1, ?2) ON CONFLICT(email) DO UPDATE SET invite_id=excluded.invite_id",
        params![email, invite_id],
    ) {
        Ok(_) => HttpResponse::Ok().json(InviteResponse {
            invite_id,
            message: "Invitation created successfully".to_string(),
        }),
        Err(err) => {
            error!("Failed to insert invitation: {}", err);
            HttpResponse::InternalServerError().finish()
        }
    }
}

async fn create_user(create_user_req: web::Json<CreateUserRequest>) -> impl Responder {
    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(err) => {
            error!("Failed to connect to database: {}", err);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let invite_id = &create_user_req.invite_id;
    let user_name = &create_user_req.user_name;
    let password = &create_user_req.password;

    let mut stmt = match conn.prepare("SELECT email FROM invitations WHERE invite_id = ?1") {
        Ok(stmt) => stmt,
        Err(err) => {
            error!("Failed to prepare statement: {}", err);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let email_iter = match stmt.query_map(params![invite_id], |row| row.get(0)) {
        Ok(iter) => iter,
        Err(err) => {
            error!("Failed to query invitation: {}", err);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let email: Option<String> = email_iter.filter_map(Result::ok).next();

    if email.is_none() {
        return HttpResponse::Unauthorized().json(CreateUserResponse {
            message: "Invalid invite_id".to_string(),
        });
    }

    match conn.execute(
        "INSERT INTO users (user_name, password) VALUES (?1, ?2)",
        params![user_name, password],
    ) {
        Ok(_) => HttpResponse::Ok().json(CreateUserResponse {
            message: "User created successfully".to_string(),
        }),
        Err(err) => {
            if err.to_string().contains("UNIQUE constraint failed") {
                HttpResponse::BadRequest().json(CreateUserResponse {
                    message: "Username already exists. Try providing different username.".to_string(),
                })
            } else {
                error!("Failed to create user: {}", err);
                HttpResponse::InternalServerError().finish()
            }
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS invitations (
            email TEXT PRIMARY KEY,
            invite_id TEXT NOT NULL
        )",
        [],
    ).expect("Failed to create invitations table");

    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (
            user_name TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )",
        [],
    ).expect("Failed to create users table");

    HttpServer::new(|| {
        App::new()
            .wrap(Logger::default())
            .route("/invite_user", web::post().to(invite_user))
            .route("/create_user", web::post().to(create_user))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}