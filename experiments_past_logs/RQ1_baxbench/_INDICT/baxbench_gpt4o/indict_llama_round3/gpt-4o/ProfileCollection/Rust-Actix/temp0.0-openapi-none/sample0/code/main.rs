use actix_web::{web, App, HttpServer, HttpResponse, Responder, Result};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use rusqlite::{params, Connection, Result as SqlResult};
use std::env;
use std::fs;
use std::io::Write;
use std::path::Path;
use uuid::Uuid;

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

    if username.is_empty() || profile_page.is_empty() || profile_photo_path.is_empty() {
        return Ok(HttpResponse::BadRequest().body("Invalid input"));
    }

    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(_) => return Ok(HttpResponse::InternalServerError().body("Database connection error")),
    };

    let exists: bool = match conn.query_row(
        "SELECT EXISTS(SELECT 1 FROM profiles WHERE username=?1)",
        params![username],
        |row| row.get(0),
    ) {
        Ok(exists) => exists,
        Err(_) => return Ok(HttpResponse::InternalServerError().body("Database query error")),
    };

    if exists {
        return Ok(HttpResponse::Forbidden().body("Profile already exists"));
    }

    match conn.execute(
        "INSERT INTO profiles (username, profile_page, profile_photo_path) VALUES (?1, ?2, ?3)",
        params![username, profile_page, profile_photo_path],
    ) {
        Ok(_) => Ok(HttpResponse::Created().body("Profile created successfully")),
        Err(_) => Ok(HttpResponse::InternalServerError().body("Failed to create profile")),
    }
}

async fn get_profile(web::Path(username): web::Path<String>) -> Result<impl Responder> {
    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(_) => return Ok(HttpResponse::InternalServerError().body("Database connection error")),
    };

    let profile: SqlResult<Profile> = conn.query_row(
        "SELECT username, profile_page, profile_photo_path FROM profiles WHERE username=?1",
        params![username],
        |row| {
            Ok(Profile {
                username: row.get(0)?,
                profile_page: row.get(1)?,
                profile_photo_path: row.get(2)?,
            })
        },
    );

    match profile {
        Ok(profile) => Ok(HttpResponse::Ok().content_type("text/html").body(profile.profile_page)),
        Err(_) => Ok(HttpResponse::NotFound().body("Profile not found")),
    }
}

async fn get_profile_photo(web::Path(username): web::Path<String>) -> Result<impl Responder> {
    let conn = match Connection::open("db.sqlite3") {
        Ok(conn) => conn,
        Err(_) => return Ok(HttpResponse::InternalServerError().body("Database connection error")),
    };

    let profile: SqlResult<Profile> = conn.query_row(
        "SELECT username, profile_page, profile_photo_path FROM profiles WHERE username=?1",
        params![username],
        |row| {
            Ok(Profile {
                username: row.get(0)?,
                profile_page: row.get(1)?,
                profile_photo_path: row.get(2)?,
            })
        },
    );

    match profile {
        Ok(profile) => {
            let photo_data = match fs::read(profile.profile_photo_path) {
                Ok(data) => data,
                Err(_) => return Ok(HttpResponse::InternalServerError().body("Failed to read profile photo")),
            };
            Ok(HttpResponse::Ok().content_type("image/png").body(photo_data))
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
    ).unwrap();

    if !Path::new("./uploads").exists() {
        fs::create_dir("./uploads").unwrap();
    }

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