use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use rusqlite::{params, Connection, Result};
use std::env;
use std::fs::File;
use std::io::Write;
use std::path::Path;
use uuid::Uuid;

#[derive(Debug)]
struct Profile {
    username: String,
    profile_page: String,
    profile_photo: String,
}

async fn add_profile(mut payload: Multipart) -> impl Responder {
    let mut username = String::new();
    let mut profile_page = String::new();
    let mut profile_photo_path = String::new();

    while let Some(field) = payload.next().await.unwrap() {
        let field_name = field.name().to_string();

        match field_name.as_str() {
            "username" => {
                username = field.map(|f| f.to_string()).unwrap();
            }
            "profile_page" => {
                profile_page = field.map(|f| f.to_string()).unwrap();
            }
            "profile_photo" => {
                let file_name = format!("{}.png", Uuid::new_v4());
                profile_photo_path = file_name.clone();
                let mut f = File::create(&file_name).unwrap();
                let mut data = vec![];
                while let Some(chunk) = field.next().await.unwrap() {
                    data.extend_from_slice(&chunk.unwrap());
                }
                f.write_all(&data).unwrap();
            }
            _ => {}
        }
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS profiles (
            username TEXT PRIMARY KEY,
            profile_page TEXT NOT NULL,
            profile_photo TEXT NOT NULL
        )",
        [],
    ).unwrap();

    match conn.execute(
        "INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?1, ?2, ?3)",
        params![username, profile_page, profile_photo_path],
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
            let path = Path::new(&photo);
            if path.exists() {
                let photo_data = std::fs::read(path).unwrap();
                HttpResponse::Ok()
                    .content_type("image/png")
                    .body(photo_data)
            } else {
                HttpResponse::NotFound().finish()
            }
        }
        Err(_) => HttpResponse::NotFound().finish(),
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