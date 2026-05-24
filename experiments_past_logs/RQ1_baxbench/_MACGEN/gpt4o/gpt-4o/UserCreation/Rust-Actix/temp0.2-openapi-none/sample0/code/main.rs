use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use uuid::Uuid;
use std::sync::Mutex;

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

#[derive(Serialize)]
struct ErrorResponse {
    message: String,
}

struct AppState {
    db: Mutex<Connection>,
}

async fn invite_user(data: web::Data<AppState>, req: web::Json<InviteUserRequest>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let email = &req.email;

    let mut stmt = conn.prepare("SELECT invite_id FROM invitations WHERE email = ?1").unwrap();
    let invite_id: Result<String> = stmt.query_row(params![email], |row| row.get(0));

    match invite_id {
        Ok(id) => HttpResponse::Ok().json(InviteUserResponse {
            invite_id: id,
            message: "Invitation already exists.".to_string(),
        }),
        Err(_) => {
            let new_invite_id = Uuid::new_v4().to_string();
            conn.execute(
                "INSERT INTO invitations (email, invite_id) VALUES (?1, ?2)",
                params![email, new_invite_id],
            ).unwrap();

            HttpResponse::Ok().json(InviteUserResponse {
                invite_id: new_invite_id,
                message: "Invitation created.".to_string(),
            })
        }
    }
}

async fn create_user(data: web::Data<AppState>, req: web::Json<CreateUserRequest>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let invite_id = &req.invite_id;
    let user_name = &req.user_name;

    let mut stmt = conn.prepare("SELECT email FROM invitations WHERE invite_id = ?1").unwrap();
    let email: Result<String> = stmt.query_row(params![invite_id], |row| row.get(0));

    match email {
        Ok(_) => {
            let mut stmt = conn.prepare("SELECT user_name FROM users WHERE user_name = ?1").unwrap();
            let user_exists: Result<String> = stmt.query_row(params![user_name], |row| row.get(0));

            match user_exists {
                Ok(_) => HttpResponse::BadRequest().json(ErrorResponse {
                    message: "Username already exists. Try providing different username.".to_string(),
                }),
                Err(_) => {
                    conn.execute(
                        "INSERT INTO users (user_name, password) VALUES (?1, ?2)",
                        params![user_name, &req.password],
                    ).unwrap();

                    HttpResponse::Ok().json(CreateUserResponse {
                        message: "User created.".to_string(),
                    })
                }
            }
        }
        Err(_) => HttpResponse::Unauthorized().json(ErrorResponse {
            message: "Invalid invite_id".to_string(),
        }),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
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

    let data = web::Data::new(AppState {
        db: Mutex::new(conn),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(data.clone())
            .route("/invite_user", web::post().to(invite_user))
            .route("/create_user", web::post().to(create_user))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}