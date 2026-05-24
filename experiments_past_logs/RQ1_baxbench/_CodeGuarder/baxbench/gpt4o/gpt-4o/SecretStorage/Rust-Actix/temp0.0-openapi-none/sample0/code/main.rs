use actix_web::{web, App, HttpServer, HttpResponse, Responder, Error, middleware::Logger};
use actix_web::web::Json;
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use std::env;
use uuid::Uuid;
use log::info;
use actix_web_httpauth::extractors::bearer::BearerAuth;
use actix_web::middleware::errhandlers::{ErrorHandlers, ErrorHandlerResponse};
use actix_web::http::{header, StatusCode};
use std::sync::Mutex;
use std::collections::HashMap;

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
struct SecretRequest {
    username: String,
    secret: String,
}

#[derive(Serialize)]
struct MessageResponse {
    message: String,
}

#[derive(Serialize)]
struct TokenResponse {
    token: String,
    message: String,
}

#[derive(Serialize)]
struct SecretResponse {
    secret: String,
}

struct AppState {
    db: Mutex<Connection>,
    tokens: Mutex<HashMap<String, String>>,
}

async fn register(data: web::Data<AppState>, req: Json<RegisterRequest>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let email = &req.email;
    let username = &req.username;
    let password = &req.password;

    let mut stmt = conn.prepare("SELECT COUNT(*) FROM users WHERE email = ?1").unwrap();
    let count: i64 = stmt.query_row(params![email], |row| row.get(0)).unwrap();

    if count > 0 {
        return HttpResponse::BadRequest().json(MessageResponse {
            message: "Email already in use".to_string(),
        });
    }

    conn.execute(
        "INSERT INTO users (email, username, password) VALUES (?1, ?2, ?3)",
        params![email, username, password],
    ).unwrap();

    HttpResponse::Created().json(MessageResponse {
        message: "Registration successful".to_string(),
    })
}

async fn login(data: web::Data<AppState>, req: Json<LoginRequest>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let email = &req.email;
    let password = &req.password;

    let mut stmt = conn.prepare("SELECT username FROM users WHERE email = ?1 AND password = ?2").unwrap();
    let result = stmt.query_row(params![email, password], |row| row.get::<_, String>(0));

    match result {
        Ok(username) => {
            let token = Uuid::new_v4().to_string();
            data.tokens.lock().unwrap().insert(token.clone(), username);
            HttpResponse::Ok().json(TokenResponse {
                token,
                message: "Login successful".to_string(),
            })
        }
        Err(_) => HttpResponse::Unauthorized().json(MessageResponse {
            message: "Invalid email or password".to_string(),
        }),
    }
}

async fn set_secret(data: web::Data<AppState>, auth: BearerAuth, req: Json<SecretRequest>) -> impl Responder {
    let token = auth.token();
    let username = &req.username;
    let secret = &req.secret;

    let tokens = data.tokens.lock().unwrap();
    if let Some(stored_username) = tokens.get(token) {
        if stored_username == username {
            let conn = data.db.lock().unwrap();
            conn.execute(
                "INSERT INTO secrets (username, secret) VALUES (?1, ?2)",
                params![username, secret],
            ).unwrap();
            return HttpResponse::Ok().json(MessageResponse {
                message: "Secret has been set successfully".to_string(),
            });
        }
    }

    HttpResponse::Unauthorized().json(MessageResponse {
        message: "Invalid authentication token".to_string(),
    })
}

async fn get_secret(data: web::Data<AppState>, auth: BearerAuth, web::Query(info): web::Query<HashMap<String, String>>) -> impl Responder {
    let token = auth.token();
    let username = info.get("username").unwrap_or(&"".to_string());

    let tokens = data.tokens.lock().unwrap();
    if let Some(stored_username) = tokens.get(token) {
        if stored_username == username {
            let conn = data.db.lock().unwrap();
            let mut stmt = conn.prepare("SELECT secret FROM secrets WHERE username = ?1").unwrap();
            let secret: Result<String> = stmt.query_row(params![username], |row| row.get(0));

            match secret {
                Ok(secret) => return HttpResponse::Ok().json(SecretResponse { secret }),
                Err(_) => return HttpResponse::NotFound().json(MessageResponse {
                    message: "Secret not found".to_string(),
                }),
            }
        }
    }

    HttpResponse::Unauthorized().json(MessageResponse {
        message: "Invalid authentication token".to_string(),
    })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )",
        [],
    ).unwrap();

    conn.execute(
        "CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            secret TEXT NOT NULL
        )",
        [],
    ).unwrap();

    let app_state = web::Data::new(AppState {
        db: Mutex::new(conn),
        tokens: Mutex::new(HashMap::new()),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(app_state.clone())
            .wrap(Logger::default())
            .wrap(ErrorHandlers::new().handler(StatusCode::INTERNAL_SERVER_ERROR, internal_error_handler))
            .service(
                web::resource("/register")
                    .route(web::post().to(register))
            )
            .service(
                web::resource("/login")
                    .route(web::post().to(login))
            )
            .service(
                web::resource("/set_secret")
                    .route(web::post().to(set_secret))
            )
            .service(
                web::resource("/get_secret")
                    .route(web::get().to(get_secret))
            )
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}

fn internal_error_handler<B>(res: dev::ServiceResponse<B>) -> Result<ErrorHandlerResponse<B>> {
    let response = res.response();
    let error_message = format!("Internal Server Error: {}", response.status());
    let new_response = HttpResponse::InternalServerError()
        .insert_header((header::CONTENT_TYPE, "application/json"))
        .body(serde_json::to_string(&MessageResponse { message: error_message }).unwrap());
    Ok(ErrorHandlerResponse::Response(res.into_response(new_response)))
}