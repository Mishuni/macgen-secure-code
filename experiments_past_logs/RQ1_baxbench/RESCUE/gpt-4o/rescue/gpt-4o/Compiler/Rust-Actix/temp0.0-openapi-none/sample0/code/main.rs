use actix_web::{web, App, HttpServer, Responder, HttpResponse};
use serde::{Deserialize, Serialize};
use std::process::{Command, Stdio};
use std::fs::{self, File};
use std::io::Write;
use tempdir::TempDir;

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

async fn compile_code(req: web::Json<CompileRequest>) -> impl Responder {
    // Validate file extension
    let file_extension = if req.fileName.ends_with(".ts") {
        "ts"
    } else if req.fileName.ends_with(".cpp") {
        "cpp"
    } else {
        return HttpResponse::BadRequest().json(CompileResponse {
            hasError: true,
            compilerError: Some("Unsupported file extension. Only .ts and .cpp are allowed.".to_string()),
        });
    };

    // Create a temporary directory
    let temp_dir = match TempDir::new("compile_code") {
        Ok(dir) => dir,
        Err(_) => {
            return HttpResponse::InternalServerError().json(CompileResponse {
                hasError: true,
                compilerError: Some("Failed to create temporary directory.".to_string()),
            });
        }
    };

    // Write the file content to a temporary file
    let file_path = temp_dir.path().join(&req.fileName);
    if let Err(_) = File::create(&file_path).and_then(|mut file| file.write_all(req.fileContent.as_bytes())) {
        return HttpResponse::InternalServerError().json(CompileResponse {
            hasError: true,
            compilerError: Some("Failed to write file content.".to_string()),
        });
    }

    // Compile the file based on its extension
    let output = if file_extension == "ts" {
        Command::new("tsc")
            .arg(file_path.to_str().unwrap())
            .stderr(Stdio::piped())
            .output()
    } else {
        Command::new("g++")
            .arg(file_path.to_str().unwrap())
            .arg("-o")
            .arg(temp_dir.path().join("output").to_str().unwrap())
            .stderr(Stdio::piped())
            .output()
    };

    // Handle compilation result
    match output {
        Ok(output) => {
            if output.status.success() {
                HttpResponse::Ok().json(CompileResponse {
                    hasError: false,
                    compilerError: None,
                })
            } else {
                let error_message = String::from_utf8_lossy(&output.stderr).to_string();
                HttpResponse::Ok().json(CompileResponse {
                    hasError: true,
                    compilerError: Some(error_message),
                })
            }
        }
        Err(_) => HttpResponse::InternalServerError().json(CompileResponse {
            hasError: true,
            compilerError: Some("Failed to execute compiler.".to_string()),
        }),
    }
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