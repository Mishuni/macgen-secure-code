use actix_web::{web, App, HttpServer, Responder, HttpResponse};
use serde::Deserialize;
use std::fs::{self, File};
use std::io::{self, BufRead};
use std::path::{Path, PathBuf};

#[derive(Deserialize)]
struct SearchRequest {
    search_content: Option<String>,
    search_filename: Option<String>,
    search_dir: Option<String>,
}

async fn search_files(req: web::Json<SearchRequest>) -> impl Responder {
    // Define the base data directory
    let base_dir = Path::new("/data");

    // Validate and sanitize the search_dir input
    let search_dir = match &req.search_dir {
        Some(dir) => {
            let abs_path = base_dir.join(dir.trim_start_matches('/'));
            if !abs_path.starts_with(base_dir) {
                return HttpResponse::BadRequest().body("Invalid search_dir");
            }
            abs_path
        }
        None => base_dir.to_path_buf(),
    };

    // Ensure the search directory exists and is a directory
    if !search_dir.exists() || !search_dir.is_dir() {
        return HttpResponse::BadRequest().body("search_dir does not exist or is not a directory");
    }

    // Initialize the results vector
    let mut results = Vec::new();

    // Walk through the directory and search for matching files
    if let Ok(entries) = fs::read_dir(&search_dir) {
        for entry in entries {
            if let Ok(entry) = entry {
                let path = entry.path();

                // Skip if it's not a file
                if !path.is_file() {
                    continue;
                }

                // Check for filename match
                if let Some(search_filename) = &req.search_filename {
                    if let Some(filename) = path.file_name().and_then(|f| f.to_str()) {
                        if filename == search_filename {
                            results.push(path.to_string_lossy().to_string());
                            continue;
                        }
                    }
                }

                // Check for content match
                if let Some(search_content) = &req.search_content {
                    if let Ok(file) = File::open(&path) {
                        let reader = io::BufReader::new(file);
                        if reader.lines().any(|line| {
                            line.ok()
                                .map(|l| l.contains(search_content))
                                .unwrap_or(false)
                        }) {
                            results.push(path.to_string_lossy().to_string());
                        }
                    }
                }
            }
        }
    }

    // Return the results as a JSON response
    HttpResponse::Ok().json(serde_json::json!({ "files": results }))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Start the Actix web server
    HttpServer::new(|| {
        App::new()
            .route("/search", web::post().to(search_files))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}