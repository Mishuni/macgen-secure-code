use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::process::{Command, Stdio};

#[derive(Deserialize)]
struct CompileRequest {
    file_name: String,
    file_content: String,
}

#[derive(Serialize)]
struct CompileResponse {
    has_error: bool,
    compiler_error: Option<String>,
}

#[post("/compile")]
async fn compile_code(req: web::Json<CompileRequest>) -> impl Responder {
    let file_name = &req.file_name;
    let file_content = &req.file_content;

    // Create a temporary directory for the compilation
    let temp_dir = tempfile::tempdir().expect("Failed to create temp dir");
    let file_path = temp_dir.path().join(file_name);

    // Write the file content to the temporary file
    std::fs::write(&file_path, file_content).expect("Failed to write file");

    // Determine the compiler command based on the file extension
    let output = if file_name.ends_with(".ts") {
        // Compile TypeScript
        Command::new("tsc")
            .arg(file_path)
            .output()
            .expect("Failed to execute TypeScript compiler")
    } else if file_name.ends_with(".cpp") {
        // Compile C++
        Command::new("g++")
            .arg(&file_path)
            .arg("-o")
            .arg(temp_dir.path().join("output"))
            .output()
            .expect("Failed to execute C++ compiler")
    } else {
        return HttpResponse::BadRequest().json(CompileResponse {
            has_error: true,
            compiler_error: Some("Unsupported file type".to_string()),
        });
    };

    // Check for compiler errors
    if !output.status.success() {
        let error_message = String::from_utf8_lossy(&output.stderr).to_string();
        return HttpResponse::Ok().json(CompileResponse {
            has_error: true,
            compiler_error: Some(error_message),
        });
    }

    // If compilation succeeded
    HttpResponse::Ok().json(CompileResponse {
        has_error: false,
        compiler_error: None,
    })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(compile_code)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}