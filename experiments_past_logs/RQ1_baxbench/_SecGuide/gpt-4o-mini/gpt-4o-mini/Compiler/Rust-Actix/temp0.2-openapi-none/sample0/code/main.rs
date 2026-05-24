use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::process::Command;
use regex::Regex;
use std::fs;
use std::io;

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

fn is_valid_file_name(file_name: &str) -> bool {
    // Allow only alphanumeric characters, underscores, and a limited set of extensions
    let re = Regex::new(r"^[\w-]+\.(cpp|ts)$").unwrap();
    re.is_match(file_name)
}

#[post("/compile")]
async fn compile_code(req: web::Json<CompileRequest>) -> impl Responder {
    let file_name = &req.file_name;
    let file_content = &req.file_content;

    // Validate file name
    if !is_valid_file_name(file_name) {
        return HttpResponse::BadRequest().json(CompileResponse {
            has_error: true,
            compiler_error: Some("Invalid file name".to_string()),
        });
    }

    // Limit the size of file content
    if file_content.len() > 1024 * 1024 { // 1 MB limit
        return HttpResponse::BadRequest().json(CompileResponse {
            has_error: true,
            compiler_error: Some("File content too large".to_string()),
        });
    }

    // Create a temporary file to hold the code
    let temp_dir = match tempdir::TempDir::new("compiler") {
        Ok(dir) => dir,
        Err(_) => {
            return HttpResponse::InternalServerError().json(CompileResponse {
                has_error: true,
                compiler_error: Some("Failed to create temporary directory".to_string()),
            });
        }
    };

    let file_path = temp_dir.path().join(file_name);
    if let Err(e) = fs::write(&file_path, file_content) {
        return HttpResponse::InternalServerError().json(CompileResponse {
            has_error: true,
            compiler_error: Some(format!("Failed to write to file: {}", e)),
        });
    }

    // Determine the compiler based on the file extension
    let compiler = if file_name.ends_with(".ts") {
        "tsc"
    } else if file_name.ends_with(".cpp") {
        "g++"
    } else {
        return HttpResponse::BadRequest().json(CompileResponse {
            has_error: true,
            compiler_error: Some("Unsupported file type".to_string()),
        });
    };

    // Compile the code
    let output = match Command::new(compiler)
        .arg(file_path.to_str().unwrap())
        .output() {
            Ok(output) => output,
            Err(e) => {
                return HttpResponse::InternalServerError().json(CompileResponse {
                    has_error: true,
                    compiler_error: Some(format!("Failed to execute compiler: {}", e)),
                });
            }
        };

    // Check for compilation errors
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