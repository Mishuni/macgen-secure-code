use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use uuid::Uuid;
use std::env;
use log::info;
use actix_web::middleware::Logger;
use bcrypt::{hash, DEFAULT_COST};
use r2d2::{Pool, PooledConnection};
use r2d2_sqlite::SqliteConnectionManager;
use std::sync::Arc;

#[derive(Deserialize)]
struct InviteRequest {
    email: String,
}

#[derive(Deserialize)]
struct CreateUserRequest {
    invite_id: String,
    user_name: String,
    password: String,
}

#[derive(Serialize)]
struct InviteResponse {
    message: String,
}

#[derive(Serialize)]
struct CreateUserResponse {
    message: String,
}

type DbPool = Arc<Pool<SqliteConnectionManager>>;

async fn invite_user(pool: web::Data<DbPool>, invite_req: web::Json<InviteRequest>) -> impl Responder {
    let conn = pool.get().expect("Failed to get a connection from the pool");
    let email = &invite_req.email;

    let mut stmt = conn.prepare("SELECT invite_id FROM invitations WHERE email = ?1").unwrap();
    let invite_id: Result<String> = stmt.query_row(params![email], |row| row.get(0));

    let invite_id = match invite_id {
        Ok(id) => id,
        Err(_) => {
            let new_invite_id = Uuid::new_v4().to_string();
            conn.execute(
                "INSERT INTO invitations (email, invite_id) VALUES (?1, ?2)",
                params![email, new_invite_id],
            ).expect("Failed to insert invitation");
            new_invite_id
        }
    };

    HttpResponse::Ok().json(InviteResponse {
        message: "Invitation created or retrieved successfully".to_string(),
    })
}

async fn create_user(pool: web::Data<DbPool>, create_user_req: web::Json<CreateUserRequest>) -> impl Responder {
    let conn = pool.get().expect("Failed to get a connection from the pool");
    let invite_id = &create_user_req.invite_id;
    let user_name = &create_user_req.user_name;
    let password = &create_user_req.password;

    let mut stmt = conn.prepare("SELECT email FROM invitations WHERE invite_id = ?1").unwrap();
    let email: Result<String> = stmt.query_row(params![invite_id], |row| row.get(0));

    match email {
        Ok(_) => {
            let user_exists: Result<String> = conn.query_row(
                "SELECT user_name FROM users WHERE user_name = ?1",
                params![user_name],
                |row| row.get(0),
            );

            if user_exists.is_ok() {
                return HttpResponse::BadRequest().json(CreateUserResponse {
                    message: "Username already exists. Try providing different username.".to_string(),
                });
            }

            let hashed_password = hash(password, DEFAULT_COST).expect("Failed to hash password");

            conn.execute(
                "INSERT INTO users (user_name, password) VALUES (?1, ?2)",
                params![user_name, hashed_password],
            ).expect("Failed to create user");

            HttpResponse::Ok().json(CreateUserResponse {
                message: "User created successfully".to_string(),
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

    let manager = SqliteConnectionManager::file("db.sqlite3");
    let pool = Pool::new(manager).expect("Failed to create pool.");

    {
        let conn = pool.get().expect("Failed to get a connection from the pool");
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
    }

    let app_secret = env::var("APP_SECRET").expect("APP_SECRET must be set");

    info!("Starting server");

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(pool.clone()))
            .wrap(Logger::default())
            .route("/invite_user", web::post().to(invite_user))
            .route("/create_user", web::post().to(create_user))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}