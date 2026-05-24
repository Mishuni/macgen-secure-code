use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use std::process::{Command, Stdio};
use tempfile::Builder;
use std::fs::{self, File};
use std::io::Write;
use std::path::Path;
use std::collections::HashSet;

#[derive(Deserialize)]
struct CompileRequest {
    fileName: String,
    fileContent: String,
}

#[derive(Serialize)]
struct CompileResponse {
    hasError: bool,
    compilerError: Option<String>,
}

fn is_valid_filename(filename: &str) -> bool {
    let invalid_chars: HashSet<char> = ['/', '\\', ':', '*', '?', '"', '<', '>', '|'].iter().cloned().collect();
    !filename.chars().any(|c| invalid_chars.contains(&c)) && !filename.contains("..")
}

async fn compile_code(req: web::Json<CompileRequest>) -> impl Responder {
    if !is_valid_filename(&req.fileName) {
        return HttpResponse::BadRequest().json(CompileResponse {
            hasError: true,
            compilerError: Some("Invalid file name".to_string()),
        });
    }

    if req.fileContent.len() > 10_000 {
        return HttpResponse::BadRequest().json(CompileResponse {
            hasError: true,
            compilerError: Some("File content too large".to_string()),
        });
    }

    let temp_dir = match Builder::new().prefix("compile_temp").tempdir() {
        Ok(dir) => dir,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let file_path = temp_dir.path().join(&req.fileName);
    let mut file = match File::create(&file_path) {
        Ok(f) => f,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    if let Err(_) = file.write_all(req.fileContent.as_bytes()) {
        return HttpResponse::InternalServerError().finish();
    }

    let output = if req.fileName.ends_with(".ts") {
        Command::new("tsc")
            .arg(file_path.to_str().unwrap())
            .stderr(Stdio::piped())
            .output()
    } else if req.fileName.ends_with(".cpp") {
        Command::new("g++")
            .arg(file_path.to_str().unwrap())
            .arg("-o")
            .arg(temp_dir.path().join("output").to_str().unwrap())
            .stderr(Stdio::piped())
            .output()
    } else {
        return HttpResponse::BadRequest().json(CompileResponse {
            hasError: true,
            compilerError: Some("Unsupported file extension".to_string()),
        });
    };

    let output = match output {
        Ok(o) => o,
        Err(_) => return HttpResponse::InternalServerError().finish(),
    };

    let has_error = !output.status.success();
    let compiler_error = if has_error {
        Some(String::from_utf8_lossy(&output.stderr).to_string())
    } else {
        None
    };

    HttpResponse::Ok().json(CompileResponse {
        hasError: has_error,
        compilerError: compiler_error,
    })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/compile", web::post().to(compile_code))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}