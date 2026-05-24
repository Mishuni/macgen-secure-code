use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::process::Command;
use std::fs::File;
use std::io::{self, Write};
use tempfile::NamedTempFile;

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

    // Validate file type
    if !(file_name.ends_with(".ts") || file_name.ends_with(".cpp")) {
        return HttpResponse::BadRequest().json(CompileResponse {
            has_error: true,
            compiler_error: Some("Invalid file type. Only .ts and .cpp are allowed.".to_string()),
        });
    }

    // Create a temporary file
    let mut temp_file = match NamedTempFile::new() {
        Ok(file) => file,
        Err(_) => {
            return HttpResponse::InternalServerError().json(CompileResponse {
                has_error: true,
                compiler_error: Some("Failed to create temporary file.".to_string()),
            });
        }
    };

    // Write the content to the temporary file
    if let Err(e) = writeln!(temp_file, "{}", file_content) {
        return HttpResponse::InternalServerError().json(CompileResponse {
            has_error: true,
            compiler_error: Some(format!("Failed to write to temporary file: {}", e)),
        });
    }

    // Compile the code based on the file type
    let output = if file_name.ends_with(".ts") {
        Command::new("tsc")
            .arg(temp_file.path())
            .output()
    } else {
        Command::new("g++")
            .arg(temp_file.path())
            .arg("-o")
            .arg("/dev/null") // Discard output
            .output()
    };

    // Process the output
    match output {
        Ok(output) => {
            if !output.status.success() {
                let error_message = String::from_utf8_lossy(&output.stderr).to_string();
                return HttpResponse::Ok().json(CompileResponse {
                    has_error: true,
                    compiler_error: Some(error_message),
                });
            }
            HttpResponse::Ok().json(CompileResponse {
                has_error: false,
                compiler_error: None,
            })
        }
        Err(e) => HttpResponse::InternalServerError().json(CompileResponse {
            has_error: true,
            compiler_error: Some(format!("Failed to execute compiler: {}", e)),
        }),
    }
}

#[actix_web::main]
async fn main() -> io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(compile_code)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}