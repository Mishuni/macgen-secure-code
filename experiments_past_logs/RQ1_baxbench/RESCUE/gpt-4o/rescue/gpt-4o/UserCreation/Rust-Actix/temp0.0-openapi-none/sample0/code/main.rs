use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection};
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

#[derive(Serialize)]
struct ErrorResponse {
    message: String,
}

async fn invite_user(
    req: web::Json<InviteUserRequest>,
    conn: web::Data<Connection>,
) -> impl Responder {
    let email = req.email.trim();

    if email.is_empty() {
        return HttpResponse::BadRequest().json(ErrorResponse {
            message: "Email cannot be empty".to_string(),
        });
    }

    let invite_id = Uuid::new_v4().to_string();

    match conn.execute(
        "INSERT OR IGNORE INTO invitations (email, invite_id) VALUES (?1, ?2)",
        params![email, invite_id],
    ) {
        Ok(_) => {
            let mut stmt = conn
                .prepare("SELECT invite_id FROM invitations WHERE email = ?1")
                .unwrap();
            let mut rows = stmt.query(params![email]).unwrap();

            if let Some(row) = rows.next().unwrap() {
                let existing_invite_id: String = row.get(0).unwrap();
                HttpResponse::Ok().json(InviteUserResponse {
                    invite_id: existing_invite_id,
                    message: "Invitation created or retrieved successfully".to_string(),
                })
            } else {
                HttpResponse::InternalServerError().json(ErrorResponse {
                    message: "Failed to retrieve invitation".to_string(),
                })
            }
        }
        Err(_) => HttpResponse::InternalServerError().json(ErrorResponse {
            message: "Failed to create invitation".to_string(),
        }),
    }
}

async fn create_user(
    req: web::Json<CreateUserRequest>,
    conn: web::Data<Connection>,
) -> impl Responder {
    let invite_id = req.invite_id.trim();
    let user_name = req.user_name.trim();
    let password = req.password.trim();

    if invite_id.is_empty() || user_name.is_empty() || password.is_empty() {
        return HttpResponse::BadRequest().json(ErrorResponse {
            message: "Invite ID, username, and password cannot be empty".to_string(),
        });
    }

    let mut stmt = conn
        .prepare("SELECT email FROM invitations WHERE invite_id = ?1")
        .unwrap();
    let mut rows = stmt.query(params![invite_id]).unwrap();

    if let Some(row) = rows.next().unwrap() {
        let email: String = row.get(0).unwrap();

        match conn.execute(
            "INSERT INTO users (user_name, password, email) VALUES (?1, ?2, ?3)",
            params![user_name, password, email],
        ) {
            Ok(_) => HttpResponse::Ok().json(CreateUserResponse {
                message: "User created successfully".to_string(),
            }),
            Err(_) => HttpResponse::BadRequest().json(ErrorResponse {
                message: "Username already exists. Try providing a different username.".to_string(),
            }),
        }
    } else {
        HttpResponse::Unauthorized().json(ErrorResponse {
            message: "Invalid invite_id".to_string(),
        })
    }
}

fn init_db() -> Connection {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");

    conn.execute(
        "CREATE TABLE IF NOT EXISTS invitations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            invite_id TEXT UNIQUE NOT NULL
        )",
        [],
    )
    .expect("Failed to create invitations table");

    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL
        )",
        [],
    )
    .expect("Failed to create users table");

    conn
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    let conn = init_db();
    let conn_data = web::Data::new(conn);

    HttpServer::new(move || {
        App::new()
            .app_data(conn_data.clone())
            .route("/invite_user", web::post().to(invite_user))
            .route("/create_user", web::post().to(create_user))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}