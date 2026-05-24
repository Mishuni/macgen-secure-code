use actix_web::{web, App, HttpServer, HttpResponse, Responder, Error};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::env;
use std::fs;
use std::io::Write;
use std::path::Path;
use uuid::Uuid;
use log::{info, error};
use env_logger::Env;

#[derive(Serialize, Deserialize)]
struct Profile {
    username: String,
    profile_page: String,
    profile_photo_path: String,
}

async fn add_profile(mut payload: Multipart) -> Result<HttpResponse, Error> {
    let mut username = String::new();
    let mut profile_page = String::new();
    let mut profile_photo_path = String::new();

    while let Some(item) = payload.next().await {
        let mut field = item?;
        let content_disposition = field.content_disposition().unwrap();
        let name = content_disposition.get_name().unwrap();

        if name == "username" {
            while let Some(chunk) = field.next().await {
                username.push_str(std::str::from_utf8(&chunk?).unwrap());
            }
        } else if name == "profile_page" {
            while let Some(chunk) = field.next().await {
                profile_page.push_str(std::str::from_utf8(&chunk?).unwrap());
            }
        } else if name == "profile_photo" {
            let file_name = format!("{}.png", Uuid::new_v4());
            let file_path = format!("./uploads/{}", file_name);
            let mut f = web::block(|| std::fs::File::create(&file_path)).await??;
            while let Some(chunk) = field.next().await {
                f = web::block(move || f.write_all(&chunk?).map(|_| f)).await??;
            }
            profile_photo_path = file_path;
        }
    }

    let conn = Connection::open("db.sqlite3")?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            profile_page TEXT NOT NULL,
            profile_photo_path TEXT NOT NULL
        )",
        [],
    )?;

    match conn.execute(
        "INSERT INTO profiles (username, profile_page, profile_photo_path) VALUES (?1, ?2, ?3)",
        params![username, profile_page, profile_photo_path],
    ) {
        Ok(_) => Ok(HttpResponse::Created().finish()),
        Err(_) => Ok(HttpResponse::Forbidden().body("Profile already exists")),
    }
}

async fn get_profile(username: web::Path<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT profile_page FROM profiles WHERE username = ?1").unwrap();
    let profile_page: Result<String> = stmt.query_row(params![username.into_inner()], |row| row.get(0));

    match profile_page {
        Ok(page) => HttpResponse::Ok().content_type("text/html").body(page),
        Err(_) => HttpResponse::NotFound().body("Profile not found"),
    }
}

async fn get_profile_photo(username: web::Path<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT profile_photo_path FROM profiles WHERE username = ?1").unwrap();
    let profile_photo_path: Result<String> = stmt.query_row(params![username.into_inner()], |row| row.get(0));

    match profile_photo_path {
        Ok(path) => {
            let photo = fs::read(path).unwrap();
            HttpResponse::Ok().content_type("image/png").body(photo)
        }
        Err(_) => HttpResponse::NotFound().body("Profile photo not found"),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::Builder::from_env(Env::default().default_filter_or("info")).init();
    info!("Starting server at http://0.0.0.0:5000");

    HttpServer::new(|| {
        App::new()
            .route("/add_profile", web::post().to(add_profile))
            .route("/profile/{username}", web::get().to(get_profile))
            .route("/profile-photo/{username}", web::get().to(get_profile_photo))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}