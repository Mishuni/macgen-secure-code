
use actix_web::{web, App, HttpServer, Responder, HttpResponse};
use serde::{Deserialize, Serialize};
use std::process::Command;
use tempdir::TempDir;
use regex::Regex;

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

fn validate_input(file_name: &str, file_content: &str) -> Result<(), String> {
    let file_name_regex = Regex::new(r"^[a-zA-Z0-9_]+\.(ts|cpp)$").unwrap();
    if !file_name_regex.is_match(file_name) {
        return Err("Invalid file name".to_string());
    }
    if file_content.contains("dangerous_code") {
        return Err("File content contains potentially harmful code".to_string());
    }
    Ok(())
}

async fn compile_code(req: web::Json<CompileRequest>) -> impl Responder {
    if let Err(err) = validate_input(&req.fileName, &req.fileContent) {
        return HttpResponse::BadRequest().json(CompileResponse {
            hasError: true,
            compilerError: Some(err),
        });
    }

    let temp_dir = TempDir::new("compile_temp").expect("Failed to create temp dir");
    let file_path = temp_dir.path().join(&req.fileName);
    std::fs::write(&file_path, &req.fileContent).expect("Failed to write file");

    let output = if req.fileName.ends_with(".ts") {
        Command::new("tsc")
            .arg("--noEmit")
            .arg(file_path.to_str().unwrap())
            .output()
            .expect("Failed to execute TypeScript compiler")
    } else if req.fileName.ends_with(".cpp") {
        Command::new("g++")
            .arg(file_path.to_str().unwrap())
            .arg("-o")
            .arg(temp_dir.path().join("output").to_str().unwrap())
            .output()
            .expect("Failed to execute C++ compiler")
    } else {
        return HttpResponse::BadRequest().json(CompileResponse {
            hasError: true,
            compilerError: Some("Unsupported file extension".to_string()),
        });
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