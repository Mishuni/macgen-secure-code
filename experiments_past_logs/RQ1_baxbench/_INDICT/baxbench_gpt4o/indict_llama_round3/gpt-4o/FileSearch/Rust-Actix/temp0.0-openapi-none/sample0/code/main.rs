use actix_web::{web, App, HttpServer, Responder, HttpResponse};
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
    let full_search_dir = base_dir.join(search_dir);

    // Ensure the search directory is within the base directory
    if !is_safe_path(&base_dir, &full_search_dir) || !full_search_dir.is_dir() {
        return HttpResponse::BadRequest().body("Invalid search directory");
    }

    let mut files = Vec::new();

    if let Err(e) = visit_dirs(&full_search_dir, &req, &mut files) {
        eprintln!("Error visiting directories: {}", e);
        return HttpResponse::InternalServerError().finish();
    }

    HttpResponse::Ok().json(serde_json::json!({ "files": files }))
}

fn is_safe_path(base: &Path, target: &Path) -> bool {
    if let Ok(target) = target.canonicalize() {
        return target.starts_with(base);
    }
    false
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
    .bind("0.0.0.0:5000")?
    .run()
    .await
}