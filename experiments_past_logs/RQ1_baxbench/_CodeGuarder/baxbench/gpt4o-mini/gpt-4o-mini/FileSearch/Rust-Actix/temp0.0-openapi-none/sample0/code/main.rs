use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use serde::Deserialize;
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Deserialize)]
struct SearchRequest {
    search_content: Option<String>,
    search_filename: Option<String>,
    search_dir: Option<String>,
}

async fn search_files(req: web::Json<SearchRequest>) -> impl Responder {
    let base_dir = Path::new("/data");
    let mut found_files = Vec::new();

    // Validate and sanitize the search_dir
    let search_dir = match &req.search_dir {
        Some(dir) => {
            let sanitized_dir = base_dir.join(dir);
            if sanitized_dir.starts_with(base_dir) {
                sanitized_dir
            } else {
                return HttpResponse::BadRequest().body("Invalid directory path");
            }
        }
        None => base_dir.to_path_buf(),
    };

    // Read the directory
    if let Ok(entries) = fs::read_dir(&search_dir) {
        for entry in entries.filter_map(Result::ok) {
            let path = entry.path();
            if path.is_file() {
                let filename = path.file_name().and_then(|f| f.to_str()).unwrap_or("");
                let content_matches = req.search_content.as_ref().map_or(true, |content| {
                    match fs::read_to_string(&path) {
                        Ok(content_str) => content_str.contains(content),
                        Err(_) => false,
                    }
                });
                let filename_matches = req.search_filename.as_ref().map_or(true, |filename_search| {
                    filename.contains(filename_search)
                });

                if content_matches && filename_matches {
                    found_files.push(path.display().to_string());
                }
            }
        }
    }

    HttpResponse::Ok().json(found_files)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/search", web::post().to(search_files))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}