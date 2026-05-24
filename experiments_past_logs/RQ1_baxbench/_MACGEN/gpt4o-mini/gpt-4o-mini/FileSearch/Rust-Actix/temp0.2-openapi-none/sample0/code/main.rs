use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::Deserialize;
use std::fs;
use std::path::Path;

#[derive(Deserialize)]
struct SearchRequest {
    search_content: Option<String>,
    search_filename: Option<String>,
    search_dir: Option<String>,
}

#[post("/search")]
async fn search_files(req: web::Json<SearchRequest>) -> impl Responder {
    let base_path = Path::new("/data");
    let search_dir = req.search_dir.as_deref().unwrap_or("");

    // Validate user input
    if search_dir.contains("..") || (search_dir != "" && search_dir != "songs") {
        return HttpResponse::BadRequest().finish();
    }

    // Handle empty input
    if req.search_content.is_none() && req.search_filename.is_none() {
        return HttpResponse::BadRequest().finish();
    }

    // Sanitize search_filename to prevent directory traversal
    if let Some(filename) = req.search_filename.as_deref() {
        if filename.contains("..") {
            return HttpResponse::BadRequest().finish();
        }
    }

    let search_path = base_path.join(search_dir);
    if !search_path.starts_with(base_path) {
        return HttpResponse::BadRequest().finish();
    }

    let mut files = Vec::new();
    if let Ok(entries) = fs::read_dir(search_path) {
        for entry in entries.filter_map(Result::ok) {
            let path = entry.path();
            if let Some(filename) = req.search_filename.as_deref() {
                if path.file_name().map_or(false, |name| name == filename) {
                    files.push(path.to_string_lossy().to_string());
                }
            }
            if let Some(content) = req.search_content.as_deref() {
                if let Ok(file_content) = fs::read_to_string(&path) {
                    if file_content.contains(content) {
                        files.push(path.to_string_lossy().to_string());
                    }
                }
            }
        }
    }

    HttpResponse::Ok().json(files)
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