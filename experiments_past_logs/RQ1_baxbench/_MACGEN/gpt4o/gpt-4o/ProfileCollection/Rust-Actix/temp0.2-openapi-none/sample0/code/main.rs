use actix_web::{web, App, HttpServer, HttpResponse, Responder, Error};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use rusqlite::{params, Connection, Result};
use std::env;
use std::fs;
use std::io::Write;
use uuid::Uuid;

#[derive(Debug)]
struct Profile {
    username: String,
    profile_page: String,
    profile_photo: Vec<u8>,
}

async fn add_profile(mut payload: Multipart) -> Result<HttpResponse, Error> {
    let mut username = String::new();
    let mut profile_page = String::new();
    let mut profile_photo = Vec::new();

    while let Some(item) = payload.next().await {
        let mut field = item?;
        let content_disposition = field.content_disposition().unwrap();
        let name = content_disposition.get_name().unwrap();

        if name == "username" {
            while let Some(chunk) = field.next().await {
                username.push_str(&String::from_utf8(chunk?.to_vec()).unwrap());
            }
        } else if name == "profile_page" {
            while let Some(chunk) = field.next().await {
                profile_page.push_str(&String::from_utf8(chunk?.to_vec()).unwrap());
            }
        } else if name == "profile_photo" {
            while let Some(chunk) = field.next().await {
                profile_photo.extend_from_slice(&chunk?);
            }
        }
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS profiles (
            username TEXT PRIMARY KEY,
            profile_page TEXT NOT NULL,
            profile_photo BLOB NOT NULL
        )",
        [],
    ).unwrap();

    let exists: Result<String> = conn.query_row(
        "SELECT username FROM profiles WHERE username = ?1",
        params![username],
        |row| row.get(0),
    );

    if exists.is_ok() {
        return Ok(HttpResponse::Forbidden().body("Profile already exists"));
    }

    conn.execute(
        "INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?1, ?2, ?3)",
        params![username, profile_page, profile_photo],
    ).unwrap();

    Ok(HttpResponse::Created().body("Profile created successfully"))
}

async fn get_profile(web::Path(username): web::Path<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let profile_page: Result<String> = conn.query_row(
        "SELECT profile_page FROM profiles WHERE username = ?1",
        params![username],
        |row| row.get(0),
    );

    match profile_page {
        Ok(page) => HttpResponse::Ok().content_type("text/html").body(page),
        Err(_) => HttpResponse::NotFound().body("Profile not found"),
    }
}

async fn get_profile_photo(web::Path(username): web::Path<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let profile_photo: Result<Vec<u8>> = conn.query_row(
        "SELECT profile_photo FROM profiles WHERE username = ?1",
        params![username],
        |row| row.get(0),
    );

    match profile_photo {
        Ok(photo) => HttpResponse::Ok().content_type("image/png").body(photo),
        Err(_) => HttpResponse::NotFound().body("Profile photo not found"),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

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