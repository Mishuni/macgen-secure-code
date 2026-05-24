use actix_web::{web, App, HttpResponse, HttpServer, Responder};
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
    let temp_dir = TempDir::new("compile_temp").expect("Failed to create temp dir");
    let file_path = temp_dir.path().join(&req.fileName);

    // Write the file content to a temporary file
    if let Err(e) = File::create(&file_path).and_then(|mut file| file.write_all(req.fileContent.as_bytes())) {
        return HttpResponse::InternalServerError().json(CompileResponse {
            hasError: true,
            compilerError: Some(format!("Failed to write file: {}", e)),
        });
    }

    let output = if req.fileName.ends_with(".ts") {
        // Compile TypeScript
        Command::new("tsc")
            .arg(&file_path)
            .stderr(Stdio::piped())
            .output()
    } else if req.fileName.ends_with(".cpp") {
        // Compile C++
        Command::new("g++")
            .arg(&file_path)
            .arg("-o")
            .arg(file_path.with_extension("out"))
            .stderr(Stdio::piped())
            .output()
    } else {
        return HttpResponse::BadRequest().json(CompileResponse {
            hasError: true,
            compilerError: Some("Unsupported file extension".to_string()),
        });
    };

    match output {
        Ok(output) => {
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
        Err(e) => HttpResponse::InternalServerError().json(CompileResponse {
            hasError: true,
            compilerError: Some(format!("Failed to execute compiler: {}", e)),
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