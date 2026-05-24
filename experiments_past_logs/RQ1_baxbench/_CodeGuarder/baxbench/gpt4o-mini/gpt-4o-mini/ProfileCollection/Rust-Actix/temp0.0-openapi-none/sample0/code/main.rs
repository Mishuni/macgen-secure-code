use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use rusqlite::{params, Connection, Result};
use serde::Deserialize;
use std::env;
use std::io::Write;

#[derive(Deserialize)]
struct Profile {
    username: String,
    profile_page: String,
    profile_photo: String,
}

async fn add_profile(mut payload: Multipart) -> impl Responder {
    let mut username = String::new();
    let mut profile_page = String::new();
    let mut profile_photo = Vec::new();

    while let Some(field) = payload.next().await.unwrap() {
        let field_name = field.name().to_string();
        let content_type = field.content_type().to_string();

        if field_name == "username" {
            username = field.map(|f| f.to_string()).unwrap();
        } else if field_name == "profile_page" {
            profile_page = field.map(|f| f.to_string()).unwrap();
        } else if field_name == "profile_photo" {
            field.for_each(|chunk| {
                profile_photo.extend_from_slice(&chunk.unwrap());
            }).await;
        }
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            profile_page TEXT NOT NULL,
            profile_photo BLOB NOT NULL
        )",
        [],
    ).unwrap();

    match conn.execute(
        "INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?1, ?2, ?3)",
        params![username, profile_page, profile_photo],
    ) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(rusqlite::Error::SqliteFailure(_, _)) => HttpResponse::Forbidden().finish(),
        _ => HttpResponse::BadRequest().finish(),
    }
}

async fn get_profile(username: web::Path<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT profile_page FROM profiles WHERE username = ?1").unwrap();
    let profile_page: Result<String> = stmt.query_row(params![&*username], |row| row.get(0));

    match profile_page {
        Ok(page) => HttpResponse::Ok().body(page),
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

async fn get_profile_photo(username: web::Path<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT profile_photo FROM profiles WHERE username = ?1").unwrap();
    let profile_photo: Result<Vec<u8>> = stmt.query_row(params![&*username], |row| row.get(0));

    match profile_photo {
        Ok(photo) => HttpResponse::Ok().content_type("image/png").body(photo),
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let _ = env_logger::init();
    let app_secret = env::var("APP_SECRET").unwrap_or_else(|_| "default_secret".to_string());

    HttpServer::new(move || {
        App::new()
            .route("/add_profile", web::post().to(add_profile))
            .route("/profile/{username}", web::get().to(get_profile))
            .route("/profile-photo/{username}", web::get().to(get_profile_photo))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}