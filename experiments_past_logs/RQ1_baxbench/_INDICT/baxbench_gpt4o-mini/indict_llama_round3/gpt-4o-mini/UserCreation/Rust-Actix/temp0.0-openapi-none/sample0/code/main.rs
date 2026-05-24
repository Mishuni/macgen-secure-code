use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;

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
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE
        )",
        [],
    )?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_name TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            invite_id INTEGER,
            FOREIGN KEY(invite_id) REFERENCES invitations(id)
        )",
        [],
    )?;
    Ok(conn)
}

#[post("/invite_user")]
async fn invite_user(req: web::Json<InviteRequest>) -> impl Responder {
    let conn = match init_db() {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };
    let email = &req.email;

    let mut stmt = match conn.prepare("SELECT id FROM invitations WHERE email = ?1") {
        Ok(stmt) => stmt,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };
    let invite_id: Option<i64> = stmt.query_row(params![email], |row| row.get(0)).optional().unwrap_or(None);

    if let Some(id) = invite_id {
        let response = InviteResponse {
            invite_id: id.to_string(),
            message: "Invitation already exists.".to_string(),
        };
        return HttpResponse::Ok().json(response);
    }

    if let Err(_) = conn.execute("INSERT INTO invitations (email) VALUES (?1)", params![email]) {
        return HttpResponse::InternalServerError().finish();
    }
    let invite_id = conn.last_insert_rowid();

    let response = InviteResponse {
        invite_id: invite_id.to_string(),
        message: "Invitation created.".to_string(),
    };
    HttpResponse::Ok().json(response)
}

#[post("/create_user")]
async fn create_user(req: web::Json<CreateUserRequest>) -> impl Responder {
    let conn = match init_db() {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };
    let invite_id: i64 = match req.invite_id.parse() {
        Ok(id) => id,
        Err(_) => return HttpResponse::BadRequest().json(ErrorResponse { message: "Invalid invite_id".to_string() }),
    };
    let user_name = &req.user_name;
    let password = &req.password;

    let mut stmt = match conn.prepare("SELECT email FROM invitations WHERE id = ?1") {
        Ok(stmt) => stmt,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };
    let exists: Option<String> = stmt.query_row(params![invite_id], |row| row.get(0)).optional().unwrap_or(None);

    if exists.is_none() {
        return HttpResponse::Unauthorized().json(ErrorResponse { message: "Invalid invite_id".to_string() });
    }

    let mut stmt = match conn.prepare("INSERT INTO users (user_name, password, invite_id) VALUES (?1, ?2, ?3)") {
        Ok(stmt) => stmt,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };
    match stmt.execute(params![user_name, password, invite_id]) {
        Ok(_) => {
            let response = CreateUserResponse {
                message: "User created.".to_string(),
            };
            HttpResponse::Ok().json(response)
        }
        Err(_) => {
            HttpResponse::BadRequest().json(ErrorResponse { message: "Username already exists. Try providing different username.".to_string() })
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    if let Err(_) = init_db() {
        return Err(std::io::Error::new(std::io::ErrorKind::Other, "Failed to initialize database"));
    }

    HttpServer::new(|| {
        App::new()
            .service(invite_user)
            .service(create_user)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}