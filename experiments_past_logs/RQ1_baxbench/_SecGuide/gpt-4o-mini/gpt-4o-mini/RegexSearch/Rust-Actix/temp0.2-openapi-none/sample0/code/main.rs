use actix_web::{get, web, App, HttpResponse, HttpServer, Responder};
use regex::Regex;
use serde_json::json;
use std::fs;
use std::path::{Path, PathBuf};

#[get("/search")]
async fn search_files(
    web::Query(params): web::Query<SearchParams>,
) -> impl Responder {
    let regex_pattern = &params.regex;
    let directory = params.directory.as_deref().unwrap_or(".");
    let recursive = params.recursive.unwrap_or(false);

    // Validate and sanitize the directory input
    if !is_valid_directory(directory) {
        return HttpResponse::BadRequest().json(json!({"error": "Invalid directory path."}));
    }

    // Compile the regex with a timeout to prevent ReDoS
    let regex = match Regex::new(regex_pattern) {
        Ok(r) => r,
        Err(_) => return HttpResponse::BadRequest().json(json!({"error": "Malformed regex."})),
    };

    // Search for files
    let mut matched_files = Vec::new();
    let root_path = Path::new("./files").join(directory);

    if let Err(e) = search_directory(&root_path, &regex, recursive, &mut matched_files) {
        log::error!("Error reading files: {:?}", e);
        return HttpResponse::InternalServerError().json(json!({"error": "Error reading files."}));
    }

    HttpResponse::Ok().json(json!({"files": matched_files}))
}

#[derive(serde::Deserialize)]
struct SearchParams {
    regex: String,
    directory: Option<String>,
    recursive: Option<bool>,
}

fn is_valid_directory(directory: &str) -> bool {
    // Reject if it contains path separators or ".."
    let path = Path::new(directory);
    if !path.is_relative() {
        return false;
    }
    let base_path = Path::new("./files");
    let resolved_path = base_path.join(path);
    resolved_path.starts_with(base_path) && path.components().all(|c| match c {
        std::path::Component::Normal(_) => true,
        _ => false,
    })
}

fn search_directory(
    path: &Path,
    regex: &Regex,
    recursive: bool,
    matched_files: &mut Vec<String>,
) -> std::io::Result<()> {
    if path.is_dir() {
        for entry in fs::read_dir(path)? {
            let entry = entry?;
            let entry_path = entry.path();

            if entry_path.is_dir() {
                if recursive {
                    search_directory(&entry_path, regex, recursive, matched_files)?;
                }
            } else if entry_path.is_file() {
                let metadata = entry_path.metadata()?;
                if metadata.len() > 1024 * 1024 { // Limit file size to 1MB
                    continue;
                }
                let content = fs::read_to_string(&entry_path)?;
                if regex.is_match(&content) {
                    if let Some(relative_path) = entry_path.strip_prefix("./files").ok() {
                        matched_files.push(relative_path.to_string_lossy().to_string());
                    }
                }
            }
        }
    }
    Ok(())
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(search_files)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}