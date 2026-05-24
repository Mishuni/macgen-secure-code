use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use regex::Regex;
use std::fs::{self, File};
use std::io::{self, BufReader, Read};
use std::path::{Path, PathBuf};

#[derive(serde::Deserialize)]
struct SearchParams {
    regex: String,
    directory: Option<String>,
    recursive: Option<bool>,
}

async fn search_files(params: web::Query<SearchParams>) -> impl Responder {
    let base_path = Path::new("./files");
    let directory = params.directory.as_deref().unwrap_or(".");
    let recursive = params.recursive.unwrap_or(false);

    // Improved validation for directory input
    if directory.contains("..") || directory.contains("/") || directory.contains("\\") {
        return HttpResponse::BadRequest().json(serde_json::json!({
            "error": "Invalid directory path."
        }));
    }

    let search_path = base_path.join(directory);
    if !search_path.starts_with(base_path) {
        return HttpResponse::BadRequest().json(serde_json::json!({
            "error": "Invalid directory path."
        }));
    }

    if params.regex.len() > 100 {
        return HttpResponse::BadRequest().json(serde_json::json!({
            "error": "Regex too long."
        }));
    }

    let regex = match Regex::new(&params.regex) {
        Ok(r) => r,
        Err(_) => return HttpResponse::BadRequest().json(serde_json::json!({
            "error": "Malformed regex."
        })),
    };

    let mut matching_files = Vec::new();
    if let Err(e) = search_directory(&search_path, &regex, recursive, &mut matching_files) {
        return HttpResponse::InternalServerError().json(serde_json::json!({
            "error": e.to_string()
        }));
    }

    HttpResponse::Ok().json(serde_json::json!({
        "files": matching_files
    }))
}

fn search_directory(
    path: &Path,
    regex: &Regex,
    recursive: bool,
    matching_files: &mut Vec<String>,
) -> io::Result<()> {
    for entry in fs::read_dir(path)? {
        let entry = entry?;
        let path = entry.path();

        if path.is_dir() {
            if recursive {
                search_directory(&path, regex, recursive, matching_files)?;
            }
        } else {
            if let Some(file_name) = path.file_name().and_then(|n| n.to_str()) {
                if file_name.starts_with('.') {
                    log::warn!("Encountered hidden file: {:?}", path);
                }
            }

            let mut file = File::open(&path)?;
            let mut contents = String::new();
            let mut reader = BufReader::new(file);
            reader.read_to_string(&mut contents)?;

            if regex.is_match(&contents) {
                if let Some(relative_path) = path.strip_prefix("./files").ok() {
                    matching_files.push(relative_path.to_string_lossy().to_string());
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
            .route("/search", web::get().to(search_files))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}