use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use serde::Serialize;
use std::fs;
use std::io::{self, Read};
use std::path::{Path, PathBuf};
use regex::Regex;
use log::{error, info};
use env_logger;

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

#[derive(Serialize)]
struct SearchResponse {
    files: Vec<String>,
}

async fn search_files(query: web::Query<SearchQuery>) -> impl Responder {
    let base_dir = Path::new("./files");
    let search_dir = query.directory.as_deref().unwrap_or("");
    let full_path = base_dir.join(search_dir);

    if !full_path.exists() || !full_path.is_dir() {
        return HttpResponse::BadRequest().json(ErrorResponse {
            error: "Invalid directory path".to_string(),
        });
    }

    let regex = match Regex::new(&query.regex) {
        Ok(r) => r,
        Err(_) => {
            return HttpResponse::BadRequest().json(ErrorResponse {
                error: "Malformed regex pattern".to_string(),
            });
        }
    };

    let mut matching_files = Vec::new();
    if let Err(e) = traverse_directory(&full_path, &regex, query.recursive, &mut matching_files) {
        error!("Error traversing directory: {}", e);
        return HttpResponse::InternalServerError().json(ErrorResponse {
            error: "Internal server error".to_string(),
        });
    }

    HttpResponse::Ok().json(SearchResponse { files: matching_files })
}

fn traverse_directory(
    dir: &Path,
    regex: &Regex,
    recursive: bool,
    matching_files: &mut Vec<String>,
) -> io::Result<()> {
    for entry in fs::read_dir(dir)? {
        let entry = entry?;
        let path = entry.path();

        if path.is_dir() && recursive {
            traverse_directory(&path, regex, recursive, matching_files)?;
        } else if path.is_file() {
            if let Ok(mut file) = fs::File::open(&path) {
                let mut contents = String::new();
                if file.read_to_string(&mut contents).is_ok() && regex.is_match(&contents) {
                    if let Ok(relative_path) = path.strip_prefix("./files") {
                        if let Some(relative_str) = relative_path.to_str() {
                            matching_files.push(relative_str.to_string());
                        }
                    }
                }
            }
        }
    }
    Ok(())
}

#[derive(Deserialize)]
struct SearchQuery {
    regex: String,
    directory: Option<String>,
    recursive: bool,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    info!("Starting server at http://0.0.0.0:5000");

    HttpServer::new(|| {
        App::new()
            .route("/search", web::get().to(search_files))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}