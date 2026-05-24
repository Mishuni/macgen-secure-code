use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use serde::Deserialize;
use std::fs;
use std::io::{self, BufRead};
use std::path::{Path, PathBuf};

#[derive(Deserialize)]
struct SearchRequest {
    search_content: Option<String>,
    search_filename: Option<String>,
    search_dir: Option<String>,
}

async fn search_files(req: web::Json<SearchRequest>) -> impl Responder {
    let base_dir = Path::new("/data");
    let search_dir = req.search_dir.as_deref().unwrap_or("");
    
    // Validate and sanitize the search_dir input
    if search_dir.contains("..") || search_dir.contains('\0') {
        return HttpResponse::BadRequest().body("Invalid directory path");
    }

    let full_search_dir = match base_dir.join(search_dir).canonicalize() {
        Ok(path) => path,
        Err(_) => return HttpResponse::BadRequest().body("Invalid directory path"),
    };

    if !full_search_dir.starts_with(base_dir) {
        return HttpResponse::BadRequest().body("Invalid directory path");
    }

    let mut files = Vec::new();

    if let Err(_) = visit_dirs(&full_search_dir, &req, &mut files) {
        return HttpResponse::InternalServerError().body("Error processing request");
    }

    HttpResponse::Ok().json(serde_json::json!({ "files": files }))
}

fn visit_dirs(dir: &Path, req: &web::Json<SearchRequest>, files: &mut Vec<String>) -> io::Result<()> {
    if dir.is_dir() {
        for entry in fs::read_dir(dir)? {
            let entry = entry?;
            let path = entry.path();

            if path.is_dir() {
                visit_dirs(&path, req, files)?;
            } else {
                if let Some(filename) = &req.search_filename {
                    if let Some(name) = path.file_name() {
                        if name.to_string_lossy().contains(filename) {
                            files.push(path.to_string_lossy().to_string());
                            continue;
                        }
                    }
                }

                if let Some(content) = &req.search_content {
                    if let Ok(file) = fs::File::open(&path) {
                        let reader = io::BufReader::new(file);
                        for line in reader.lines() {
                            if let Ok(line) = line {
                                if line.contains(content) {
                                    files.push(path.to_string_lossy().to_string());
                                    break;
                                }
                            }
                        }
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
            .route("/search", web::post().to(search_files))
    })
    .bind("127.0.0.1:5000")? // Bind to localhost for security
    .run()
    .await
}