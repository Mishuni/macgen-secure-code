use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use rusqlite::{params, Connection, Result};
use std::env;
use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};
use uuid::Uuid;
use image::ImageFormat;

#[derive(Debug)]
struct Profile {
    username: String,
    profile_page: String,
    profile_photo: String,
}

async fn add_profile(mut payload: Multipart) -> impl Responder {
    let mut username = String::new();
    let mut profile_page = String::new();
    let mut profile_photo = String::new();

    while let Some(item) = payload.next().await.unwrap() {
        let field = item.unwrap();
        let name = field.name().to_string();

        if name == "username" {
            username = field.to_string().await.unwrap();
            // Validate username length and characters
            if username.len() < 3 || username.len() > 30 || !username.chars().all(char::is_alphanumeric) {
                return HttpResponse::BadRequest().body("Invalid username. It must be alphanumeric and between 3 to 30 characters.");
            }
        } else if name == "profile_page" {
            profile_page = field.to_string().await.unwrap();
            // Sanitize profile_page to prevent XSS
            profile_page = sanitize_input(&profile_page);
        } else if name == "profile_photo" {
            // Validate file type
            let content_type = field.content_type().to_string();
            if !content_type.starts_with("image/png") {
                return HttpResponse::BadRequest().body("Invalid file type. Only PNG images are allowed.");
            }

            let file_name = format!("{}.png", Uuid::new_v4());
            let file_path = Path::new("uploads").join(&file_name);
            let mut f = web::block(|| std::fs::File::create(&file_path)).await.unwrap();
            let data = web::block(|| field.bytes()).await.unwrap();

            // Validate image content
            if let Ok(_) = image::load_from_memory(&data) {
                f.write_all(&data).unwrap();
                profile_photo = file_name;
            } else {
                return HttpResponse::BadRequest().body("Uploaded file is not a valid PNG image.");
            }
        }
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            profile_page TEXT NOT NULL,
            profile_photo TEXT NOT NULL
        )",
        [],
    ).unwrap();

    match conn.execute(
        "INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?1, ?2, ?3)",
        params![username, profile_page, profile_photo],
    ) {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::Forbidden().finish(),
    }
}

async fn get_profile(web::Path(username): web::Path<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT profile_page FROM profiles WHERE username = ?1").unwrap();
    let profile_page: Result<String> = stmt.query_row(params![username], |row| row.get(0));

    match profile_page {
        Ok(page) => HttpResponse::Ok().body(page),
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

async fn get_profile_photo(web::Path(username): web::Path<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT profile_photo FROM profiles WHERE username = ?1").unwrap();
    let profile_photo: Result<String> = stmt.query_row(params![username], |row| row.get(0));

    match profile_photo {
        Ok(photo) => {
            let file_path = Path::new("uploads").join(photo);
            if Path::new(&file_path).exists() {
                let photo_data = fs::read(file_path).unwrap();
                HttpResponse::Ok().content_type("image/png").body(photo_data)
            } else {
                HttpResponse::NotFound().finish()
            }
        }
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

fn sanitize_input(input: &str) -> String {
    // Simple sanitization to prevent XSS
    let sanitized = input.replace("&", "&amp;")
                         .replace("<", "&lt;")
                         .replace(">", "&gt;")
                         .replace("\"", "&quot;")
                         .replace("'", "&#39;");
    sanitized
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    fs::create_dir_all("uploads").unwrap();
    let _ = Connection::open("db.sqlite3").unwrap();

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