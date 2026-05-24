use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use rusqlite::{params, Connection};
use serde::{Deserialize, Serialize};
use std::env;
use bcrypt::{hash, verify, DEFAULT_COST};
use std::sync::Arc;
use r2d2::{Pool, PooledConnection, ConnectionManager};

#[derive(Deserialize)]
struct LoginRequest {
    email: String,
    password: String,
}

#[derive(Deserialize)]
struct RegisterRequest {
    email: String,
    password: String,
    name: String,
}

#[derive(Serialize)]
struct LoginResponse {
    message: String,
}

#[derive(Serialize)]
struct RegisterResponse {
    message: String,
}

#[derive(Serialize)]
struct ErrorResponse {
    message: String,
}

type DbPool = Pool<ConnectionManager<Connection>>;

async fn login(req: web::Json<LoginRequest>, pool: web::Data<DbPool>) -> impl Responder {
    let conn = pool.get().map_err(|_| {
        HttpResponse::InternalServerError().json(ErrorResponse {
            message: "Database connection error".to_string(),
        })
    })?;
    
    let mut stmt = conn.prepare("SELECT name, password FROM users WHERE email = ?").map_err(|_| {
        HttpResponse::InternalServerError().json(ErrorResponse {
            message: "Database query error".to_string(),
        })
    })?;
    
    let user: Result<(String, String), _> = stmt.query_row(params![&req.email], |row| {
        let name: String = row.get(0)?;
        let password: String = row.get(1)?;
        Ok((name, password))
    });
    
    match user {
        Ok((name, hashed_password)) => {
            if verify(&req.password, &hashed_password).unwrap_or(false) {
                let response = LoginResponse {
                    message: format!("Login successful for {}", name),
                };
                HttpResponse::Ok().json(response)
            } else {
                HttpResponse::Unauthorized().json(ErrorResponse {
                    message: "Invalid email or password".to_string(),
                })
            }
        },
        Err(_) => {
            HttpResponse::Unauthorized().json(ErrorResponse {
                message: "Invalid email or password".to_string(),
            })
        },
    }
}

async fn register(req: web::Json<RegisterRequest>, pool: web::Data<DbPool>) -> impl Responder {
    let conn = pool.get().map_err(|_| {
        HttpResponse::InternalServerError().json(ErrorResponse {
            message: "Database connection error".to_string(),
        })
    })?;
    
    // Hash the password before storing it
    let hashed_password = hash(&req.password, DEFAULT_COST).unwrap();
    
    match conn.execute(
        "INSERT INTO users (email, password, name) VALUES (?1, ?2, ?3)",
        params![&req.email, &hashed_password, &req.name],
    ) {
        Ok(_) => {
            let response = RegisterResponse {
                message: "Registration successful".to_string(),
            };
            HttpResponse::Created().json(response)
        },
        Err(_) => {
            HttpResponse::BadRequest().json(ErrorResponse {
                message: "Email already in use or invalid data".to_string(),
            })
        },
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize the SQLite database connection pool
    let manager = ConnectionManager::<Connection>::new("db.sqlite3");
    let pool = Pool::builder().build(manager).expect("Failed to create pool.");

    // Initialize the SQLite database
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

    // Start the web server
    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(pool.clone()))
            .route("/login", web::post().to(login))
            .route("/register", web::post().to(register))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}