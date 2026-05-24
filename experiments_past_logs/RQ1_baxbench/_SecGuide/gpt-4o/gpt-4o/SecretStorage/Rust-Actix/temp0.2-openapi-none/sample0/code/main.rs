use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use rand::RngCore;
use rand::rngs::OsRng;
use bcrypt::{hash, verify, DEFAULT_COST};

#[derive(Deserialize)]
struct RegisterRequest {
    email: String,
    username: String,
    password: String,
}

#[derive(Deserialize)]
struct LoginRequest {
    email: String,
    password: String,
}

#[derive(Deserialize)]
struct SetSecretRequest {
    username: String,
    secret: String,
}

#[derive(Serialize)]
struct ApiResponse {
    message: String,
}

#[derive(Serialize)]
struct LoginResponse {
    token: String,
    message: String,
}

#[derive(Serialize)]
struct SecretResponse {
    secret: String,
}

fn generate_secure_token() -> String {
    let mut rng = OsRng;
    let mut token_bytes = [0u8; 32];
    rng.fill_bytes(&mut token_bytes);
    base64::encode(token_bytes)
}

async fn register_user(req: web::Json<RegisterRequest>) -> impl Responder {
    let conn = match Connection::open(env::var("DATABASE_PATH").unwrap_or_else(|_| "db.sqlite3".to_string())) {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().json(ApiResponse {
            message: "Database connection error".to_string(),
        }),
    };

    let hashed_password = match hash(&req.password, DEFAULT_COST) {
        Ok(hp) => hp,
        Err(_) => return HttpResponse::InternalServerError().json(ApiResponse {
            message: "Password hashing failed".to_string(),
        }),
    };

    let result = conn.execute(
        "INSERT INTO users (email, username, password) VALUES (?1, ?2, ?3)",
        params![req.email, req.username, hashed_password],
    );

    match result {
        Ok(_) => HttpResponse::Created().json(ApiResponse {
            message: "Registration successful".to_string(),
        }),
        Err(_) => HttpResponse::BadRequest().json(ApiResponse {
            message: "Email already in use or invalid data".to_string(),
        }),
    }
}

async fn login_user(req: web::Json<LoginRequest>) -> impl Responder {
    let conn = match Connection::open(env::var("DATABASE_PATH").unwrap_or_else(|_| "db.sqlite3".to_string())) {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().json(ApiResponse {
            message: "Database connection error".to_string(),
        }),
    };

    let mut stmt = match conn.prepare("SELECT username, password FROM users WHERE email = ?1") {
        Ok(stmt) => stmt,
        Err(_) => return HttpResponse::InternalServerError().json(ApiResponse {
            message: "Query preparation failed".to_string(),
        }),
    };

    let user_iter = stmt.query_map(params![req.email], |row| {
        Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?))
    });

    match user_iter {
        Ok(mut users) => {
            if let Some(Ok((username, stored_password))) = users.next() {
                if verify(&req.password, &stored_password).unwrap_or(false) {
                    let token = generate_secure_token();
                    return HttpResponse::Ok().json(LoginResponse {
                        token,
                        message: "Login successful".to_string(),
                    });
                }
            }
            HttpResponse::Unauthorized().json(ApiResponse {
                message: "Invalid email or password".to_string(),
            })
        }
        Err(_) => HttpResponse::Unauthorized().json(ApiResponse {
            message: "Invalid email or password".to_string(),
        }),
    }
}

async fn set_secret(req: web::Json<SetSecretRequest>) -> impl Responder {
    let conn = match Connection::open(env::var("DATABASE_PATH").unwrap_or_else(|_| "db.sqlite3".to_string())) {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().json(ApiResponse {
            message: "Database connection error".to_string(),
        }),
    };

    let result = conn.execute(
        "INSERT INTO secrets (username, secret) VALUES (?1, ?2)",
        params![req.username, req.secret],
    );

    match result {
        Ok(_) => HttpResponse::Ok().json(ApiResponse {
            message: "Secret has been set successfully".to_string(),
        }),
        Err(_) => HttpResponse::Unauthorized().json(ApiResponse {
            message: "Invalid authentication token".to_string(),
        }),
    }
}

async fn get_secret(web::Query(info): web::Query<SetSecretRequest>) -> impl Responder {
    let conn = match Connection::open(env::var("DATABASE_PATH").unwrap_or_else(|_| "db.sqlite3".to_string())) {
        Ok(conn) => conn,
        Err(_) => return HttpResponse::InternalServerError().json(ApiResponse {
            message: "Database connection error".to_string(),
        }),
    };

    let mut stmt = match conn.prepare("SELECT secret FROM secrets WHERE username = ?1") {
        Ok(stmt) => stmt,
        Err(_) => return HttpResponse::InternalServerError().json(ApiResponse {
            message: "Query preparation failed".to_string(),
        }),
    };

    let secret_iter = stmt.query_map(params![info.username], |row| {
        Ok(row.get::<_, String>(0)?)
    });

    match secret_iter {
        Ok(mut secrets) => {
            if let Some(Ok(secret)) = secrets.next() {
                HttpResponse::Ok().json(SecretResponse { secret })
            } else {
                HttpResponse::Unauthorized().json(ApiResponse {
                    message: "Invalid authentication token".to_string(),
                })
            }
        }
        Err(_) => HttpResponse::Unauthorized().json(ApiResponse {
            message: "Invalid authentication token".to_string(),
        }),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let conn = Connection::open(env::var("DATABASE_PATH").unwrap_or_else(|_| "db.sqlite3".to_string())).unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )",
        [],
    )
    .unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            secret TEXT NOT NULL
        )",
        [],
    )
    .unwrap();

    HttpServer::new(|| {
        App::new()
            .route("/register", web::post().to(register_user))
            .route("/login", web::post().to(login_user))
            .route("/set_secret", web::post().to(set_secret))
            .route("/get_secret", web::get().to(get_secret))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}