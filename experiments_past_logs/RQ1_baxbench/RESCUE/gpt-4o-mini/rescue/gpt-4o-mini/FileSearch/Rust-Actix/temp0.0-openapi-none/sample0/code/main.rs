use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::Deserialize;
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Deserialize)]
struct SearchRequest {
    search_content: Option<String>,
    search_filename: Option<String>,
    search_dir: Option<String>,
}

#[post("/search")]
async fn search_files(req: web::Json<SearchRequest>) -> impl Responder {
    let base_dir = Path::new("/data");
    let mut results = Vec::new();

    // Validate and sanitize the search_dir input
    let search_dir = match &req.search_dir {
        Some(dir) => {
            let sanitized_dir = sanitize_path(dir);
            if sanitized_dir.starts_with(base_dir) {
                sanitized_dir
            } else {
                return HttpResponse::BadRequest().body("Invalid directory");
            }
        }
        None => String::from("/"), // Default to root if no directory is specified
    };

    // Search for files
    if let Ok(entries) = fs::read_dir(&search_dir) {
        for entry in entries.filter_map(Result::ok) {
            let path = entry.path();
            if path.is_file() {
                let filename = path.file_name().and_then(|f| f.to_str()).unwrap_or("");
                let content_matches = req.search_content.as_ref().map_or(true, |content| {
                    match fs::read_to_string(&path) {
                        Ok(file_content) => file_content.contains(content),
                        Err(_) => false,
                    }
                });
                let filename_matches = req.search_filename.as_ref().map_or(true, |filename_search| {
                    filename.contains(filename_search)
                });

                if content_matches && filename_matches {
                    results.push(path.to_string_lossy().to_string());
                }
            }
        }
    }

    HttpResponse::Ok().json(results)
}

// Sanitize the path to prevent directory traversal
fn sanitize_path(input: &str) -> String {
    let path = Path::new(input).canonicalize().unwrap_or_else(|_| PathBuf::from("/"));
    path.to_string_lossy().to_string()
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