use actix_web::{post, web, App, HttpServer, HttpResponse};
use serde::{Deserialize, Serialize};
use std::process::Command;
use std::fs::File;
use std::io::Write;
use tempfile::tempdir;

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

#[post("/compile")]
async fn compile(req: web::Json<CompileRequest>) -> HttpResponse {
    let file_name = &req.fileName;
    let file_content = &req.fileContent;

    // Sanitize fileName
    if !file_name.ends_with(".ts") && !file_name.ends_with(".cpp") {
        return HttpResponse::BadRequest().json(CompileResponse {
            hasError: true,
            compilerError: Some("Invalid file extension.".to_string()),
        });
    }

    // Create a temporary directory
    let dir = tempdir().expect("Failed to create temp dir");
    let file_path = dir.path().join(file_name);

    // Write the file content to a temporary file
    let mut file = File::create(&file_path).expect("Failed to create temp file");
    file.write_all(file_content.as_bytes()).expect("Failed to write to temp file");

    // Compile the file
    let output = if file_name.ends_with(".ts") {
        Command::new("tsc")
            .arg(file_path.to_str().unwrap())
            .output()
            .expect("Failed to execute TypeScript compiler")
    } else {
        Command::new("g++")
            .arg(file_path.to_str().unwrap())
            .arg("-o")
            .arg("output")
            .output()
            .expect("Failed to execute C++ compiler")
    };

    // Check for compilation errors
    if !output.status.success() {
        let error_message = String::from_utf8_lossy(&output.stderr).to_string();
        return HttpResponse::Ok().json(CompileResponse {
            hasError: true,
            compilerError: Some(error_message),
        });
    }

    HttpResponse::Ok().json(CompileResponse {
        hasError: false,
        compilerError: None,
    })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(compile)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}