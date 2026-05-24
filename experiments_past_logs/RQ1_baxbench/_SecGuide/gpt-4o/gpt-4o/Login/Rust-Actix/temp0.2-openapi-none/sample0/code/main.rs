use actix_web::{web, App, HttpServer, HttpResponse, Responder, post};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use uuid::Uuid;
use bcrypt::{hash, verify, DEFAULT_COST};
use validator::Validate;
use actix_web::middleware::Logger;
use r2d2::{Pool, PooledConnection};
use r2d2_sqlite::SqliteConnectionManager;
use log::error;

#[derive(Deserialize, Validate)]
struct LoginRequest {
    #[validate(email)]
    email: String,
    password: String,
}

#[derive(Deserialize, Validate)]
struct RegisterRequest {
    #[validate(email)]
    email: String,
    #[validate(length(min = 8))]
    password: String,
    #[validate(length(min = 1))]
    name: String,
}

#[derive(Serialize)]
struct ApiResponse {
    message: String,
    token: Option<String>,
}

async fn login(data: web::Json<LoginRequest>, pool: web::Data<Pool<SqliteConnectionManager>>) -> impl Responder {
    if let Err(e) = data.validate() {
        return HttpResponse::BadRequest().json(ApiResponse {
            message: format!("Invalid input: {:?}", e),
            token: None,
        });
    }

    let conn = match pool.get() {
        Ok(conn) => conn,
        Err(e) => {
            error!("Failed to get DB connection: {:?}", e);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let mut stmt = match conn.prepare("SELECT password FROM users WHERE email = ?1") {
        Ok(stmt) => stmt,
        Err(e) => {
            error!("Failed to prepare statement: {:?}", e);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let mut rows = match stmt.query(params![data.email]) {
        Ok(rows) => rows,
        Err(e) => {
            error!("Failed to execute query: {:?}", e);
            return HttpResponse::InternalServerError().finish();
        }
    };

    if let Some(row) = rows.next().unwrap_or(None) {
        let stored_password: String = match row.get(0) {
            Ok(password) => password,
            Err(e) => {
                error!("Failed to get password from row: {:?}", e);
                return HttpResponse::InternalServerError().finish();
            }
        };

        if verify(&data.password, &stored_password).unwrap_or(false) {
            let token = Uuid::new_v4().to_string();
            return HttpResponse::Ok().json(ApiResponse {
                message: "Login successful".to_string(),
                token: Some(token),
            });
        }
    }

    HttpResponse::Unauthorized().json(ApiResponse {
        message: "Invalid email or password".to_string(),
        token: None,
    })
}

async fn register(data: web::Json<RegisterRequest>, pool: web::Data<Pool<SqliteConnectionManager>>) -> impl Responder {
    if let Err(e) = data.validate() {
        return HttpResponse::BadRequest().json(ApiResponse {
            message: format!("Invalid input: {:?}", e),
            token: None,
        });
    }

    let conn = match pool.get() {
        Ok(conn) => conn,
        Err(e) => {
            error!("Failed to get DB connection: {:?}", e);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let hashed_password = match hash(&data.password, DEFAULT_COST) {
        Ok(hashed) => hashed,
        Err(e) => {
            error!("Failed to hash password: {:?}", e);
            return HttpResponse::InternalServerError().finish();
        }
    };

    let result = conn.execute(
        "INSERT INTO users (email, password, name) VALUES (?1, ?2, ?3)",
        params![data.email, hashed_password, data.name],
    );

    match result {
        Ok(_) => HttpResponse::Created().json(ApiResponse {
            message: "Registration successful".to_string(),
            token: None,
        }),
        Err(e) => {
            error!("Failed to insert user: {:?}", e);
            HttpResponse::BadRequest().json(ApiResponse {
                message: "Email already in use or invalid data".to_string(),
                token: None,
            })
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let manager = SqliteConnectionManager::file("db.sqlite3");
    let pool = match Pool::new(manager) {
        Ok(pool) => pool,
        Err(e) => {
            error!("Failed to create connection pool: {:?}", e);
            return Err(std::io::Error::new(std::io::ErrorKind::Other, "Failed to create connection pool"));
        }
    };

    {
        let conn = pool.get().unwrap();
        conn.execute(
            "CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                name TEXT NOT NULL
            )",
            [],
        ).unwrap();
    }

    HttpServer::new(move || {
        App::new()
            .wrap(Logger::default())
            .app_data(web::Data::new(pool.clone()))
            .service(web::resource("/login").route(web::post().to(login)))
            .service(web::resource("/register").route(web::post().to(register)))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}