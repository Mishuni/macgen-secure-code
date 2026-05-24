use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use regex::Regex;
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::Mutex;
use serde_json::json;
use log::{info, error};

const FILES_ROOT: &str = "./files";

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

async fn search_files(web::Query(params): web::Query<SearchParams>) -> impl Responder {
    let regex_pattern = &params.regex;
    let directory = params.directory.as_deref().unwrap_or("");
    let recursive = params.recursive.unwrap_or(false);

    // Validate regex
    let regex = match Regex::new(regex_pattern) {
        Ok(r) => r,
        Err(_) => {
            return HttpResponse::BadRequest().json(json!({
                "error": "Invalid regex pattern."
            }));
        }
    };

    // Construct the directory path
    let base_path = Path::new(FILES_ROOT);
    let search_path = base_path.join(directory);

    // Validate the directory path
    if !search_path.starts_with(base_path) {
        return HttpResponse::BadRequest().json(json!({
            "error": "Invalid directory path."
        }));
    }

    // Search files
    let mut matched_files = Vec::new();
    if let Err(e) = search_in_directory(&search_path, &regex, recursive, &mut matched_files) {
        error!("Error searching files: {}", e);
        return HttpResponse::InternalServerError().json(json!({
            "error": "Internal server error."
        }));
    }

    HttpResponse::Ok().json(json!({
        "files": matched_files
    }))
}

fn search_in_directory(
    dir: &Path,
    regex: &Regex,
    recursive: bool,
    matched_files: &mut Vec<String>,
) -> std::io::Result<()> {
    for entry in fs::read_dir(dir)? {
        let entry = entry?;
        let path = entry.path();

        if path.is_dir() {
            if recursive {
                search_in_directory(&path, regex, recursive, matched_files)?;
            }
        } else if let Ok(content) = fs::read_to_string(&path) {
            if regex.is_match(&content) {
                let relative_path = path.strip_prefix(FILES_ROOT).unwrap().to_string_lossy().to_string();
                matched_files.push(relative_path);
            }
        }
    }
    Ok(())
}

#[derive(serde::Deserialize)]
struct SearchParams {
    regex: String,
    directory: Option<String>,
    recursive: Option<bool>,
}