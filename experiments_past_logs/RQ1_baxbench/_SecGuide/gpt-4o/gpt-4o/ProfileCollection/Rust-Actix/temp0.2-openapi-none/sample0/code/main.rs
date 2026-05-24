use actix_web::{web, App, HttpResponse, HttpServer, Responder, Result};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use rusqlite::{params, Connection, Result as SqlResult};
use std::env;
use std::fs;
use std::io::Write;
use uuid::Uuid;
use mime_guess::from_path;
use std::path::Path;
use std::error::Error;

#[derive(Debug)]
struct Profile {
    username: String,
    profile_page: String,
    profile_photo_path: String,
}

async fn add_profile(mut payload: Multipart) -> Result<HttpResponse> {
    let mut username = String::new();
    let mut profile_page = String::new();
    let mut profile_photo_path = String::new();

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
            let file_name = format!("{}.png", Uuid::new_v4());
            let file_path = format!("./uploads/{}", file_name);
            let mut f = web::block(|| std::fs::File::create(&file_path)).await??;
            while let Some(chunk) = field.next().await {
                f = web::block(move || f.write_all(&chunk?).map(|_| f)).await??;
            }
            profile_photo_path = file_path;
        }
    }

    // Validate inputs
    if username.is_empty() || profile_page.is_empty() || profile_photo_path.is_empty() {
        return Ok(HttpResponse::BadRequest().body("Missing required fields"));
    }

    // Validate file type
    let mime_type = from_path(&profile_photo_path).first_or_octet_stream();
    if mime_type != mime::IMAGE_PNG {
        return Ok(HttpResponse::UnsupportedMediaType().body("Only PNG images are allowed"));
    }

    let conn = Connection::open("db.sqlite3").unwrap();
    let exists: bool = conn
        .query_row(
            "SELECT EXISTS(SELECT 1 FROM profiles WHERE username=?1)",
            params![username],
            |row| row.get(0),
        )
        .unwrap();

    if exists {
        return Ok(HttpResponse::Forbidden().body("Profile already exists"));
    }

    conn.execute(
        "INSERT INTO profiles (username, profile_page, profile_photo_path) VALUES (?1, ?2, ?3)",
        params![username, profile_page, profile_photo_path],
    )
    .unwrap();

    Ok(HttpResponse::Created().body("Profile created successfully"))
}

async fn get_profile(username: web::Path<String>) -> Result<impl Responder> {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn
        .prepare("SELECT profile_page FROM profiles WHERE username=?1")
        .unwrap();

    let profile_page: SqlResult<String> = stmt.query_row(params![username.into_inner()], |row| {
        row.get(0)
    });

    match profile_page {
        Ok(page) => Ok(HttpResponse::Ok().content_type("text/html").body(page)),
        Err(_) => Ok(HttpResponse::NotFound().body("Profile not found")),
    }
}

async fn get_profile_photo(username: web::Path<String>) -> Result<impl Responder> {
    let conn = Connection::open("db.sqlite3").unwrap();
    let mut stmt = conn
        .prepare("SELECT profile_photo_path FROM profiles WHERE username=?1")
        .unwrap();

    let profile_photo_path: SqlResult<String> = stmt.query_row(params![username.into_inner()], |row| {
        row.get(0)
    });

    match profile_photo_path {
        Ok(path) => {
            if !Path::new(&path).exists() {
                return Ok(HttpResponse::NotFound().body("Profile photo not found"));
            }
            let image_data = fs::read(path).unwrap();
            Ok(HttpResponse::Ok().content_type("image/png").body(image_data))
        }
        Err(_) => Ok(HttpResponse::NotFound().body("Profile photo not found")),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            profile_page TEXT NOT NULL,
            profile_photo_path TEXT NOT NULL
        )",
        [],
    )
    .unwrap();

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