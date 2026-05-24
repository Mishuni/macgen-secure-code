use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use rusqlite::{params, Connection};
use std::env;
use std::io::Write;
use std::path::Path;
use serde::{Deserialize, Serialize};
use std::fs;

#[derive(Serialize, Deserialize)]
struct Profile {
    username: String,
    profile_page: String,
    profile_photo: String,
}

async fn add_profile(mut payload: Multipart) -> impl Responder {
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

    let mut profile: Option<Profile> = None;

    while let Some(field) = payload.next().await.unwrap() {
        let content_type = field.content_type().to_string();
        let field_name = field.name().to_string();

        let mut data = Vec::new();
        let mut file_name = String::new();

        while let Some(chunk) = field.next().await.unwrap() {
            data.extend_from_slice(&chunk);
        }

        if field_name == "username" {
            let username = String::from_utf8_lossy(&data).to_string();
            profile = Some(Profile { username, profile_page: String::new(), profile_photo: String::new() });
        } else if field_name == "profile_page" {
            let profile_page = String::from_utf8_lossy(&data).to_string();
            if let Some(ref mut p) = profile {
                p.profile_page = profile_page;
            }
        } else if field_name == "profile_photo" {
            let profile_photo = format!("{}.png", uuid::Uuid::new_v4());
            let path = Path::new(&profile_photo);
            let mut file = fs::File::create(&path).unwrap();
            file.write_all(&data).unwrap();
            if let Some(ref mut p) = profile {
                p.profile_photo = profile_photo;
            }
        }
    }

    if let Some(p) = profile {
        match conn.execute(
            "INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?1, ?2, ?3)",
            params![p.username, p.profile_page, p.profile_photo],
        ) {
            Ok(_) => HttpResponse::Created().finish(),
            Err(_) => HttpResponse::Forbidden().body("Profile already exists"),
        }
    } else {
        HttpResponse::BadRequest().body("Invalid input")
    }
}

async fn get_profile(web::Path(username): web::Path<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT profile_page FROM profiles WHERE username = ?1").unwrap();
    let profile_page: Result<String, _> = stmt.query_row(params![username], |row| row.get(0));

    match profile_page {
        Ok(page) => HttpResponse::Ok().body(page),
        Err(_) => HttpResponse::NotFound().body("Profile not found"),
    }
}

async fn get_profile_photo(web::Path(username): web::Path<String>) -> impl Responder {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn.prepare("SELECT profile_photo FROM profiles WHERE username = ?1").unwrap();
    let profile_photo: Result<String, _> = stmt.query_row(params![username], |row| row.get(0));

    match profile_photo {
        Ok(photo) => {
            let path = Path::new(&photo);
            if path.exists() {
                let data = fs::read(path).unwrap();
                HttpResponse::Ok()
                    .content_type("image/png")
                    .body(data)
            } else {
                HttpResponse::NotFound().body("Profile photo not found")
            }
        }
        Err(_) => HttpResponse::NotFound().body("Profile photo not found"),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let _ = env_logger::init();
    let app_secret = env::var("APP_SECRET").expect("APP_SECRET must be set");

    println!("Starting server with secret: {}", app_secret);

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