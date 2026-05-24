use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::process::{Command, Stdio};
use regex::Regex;

#[derive(Deserialize)]
struct MonitorRequest {
    filter_flags: Option<String>,
    command_regex: String,
}

#[derive(Serialize)]
struct ProcessInfo {
    processId: i32,
    processString: String,
}

fn validate_filter_flags(flags: &str) -> bool {
    // Allow only specific flags (e.g., "-e", "-o", etc.)
    let allowed_flags = vec!["-e", "-o"];
    flags.split_whitespace().all(|flag| allowed_flags.contains(&flag))
}

fn sanitize_command_regex(regex: &str) -> Result<Regex, String> {
    // Basic validation to prevent catastrophic backtracking
    if regex.len() > 100 {
        return Err("Regex too long".to_string());
    }
    Regex::new(regex).map_err(|e| e.to_string())
}

#[post("/monitor/commands")]
async fn monitor_commands(req: web::Json<MonitorRequest>) -> impl Responder {
    let filter_flags = req.filter_flags.as_deref().unwrap_or("");
    let command_regex = &req.command_regex;

    // Validate filter flags
    if !validate_filter_flags(filter_flags) {
        return HttpResponse::BadRequest().body("Invalid filter flags");
    }

    // Sanitize command regex
    let regex = match sanitize_command_regex(command_regex) {
        Ok(r) => r,
        Err(err) => return HttpResponse::BadRequest().body(format!("Invalid regex: {}", err)),
    };

    // Execute the `ps` command with the provided flags
    let output = Command::new("ps")
        .arg(filter_flags)
        .arg("aux")
        .stdout(Stdio::piped())
        .output();

    match output {
        Ok(output) => {
            let output_str = String::from_utf8_lossy(&output.stdout);
            let mut process_list = Vec::new();

            // Filter processes based on the regex
            for line in output_str.lines().skip(1) { // Skip the header line
                if regex.is_match(line) {
                    let parts: Vec<&str> = line.split_whitespace().collect();
                    if let Some(pid_str) = parts.get(1) {
                        if let Ok(pid) = pid_str.parse::<i32>() {
                            process_list.push(ProcessInfo {
                                processId: pid,
                                processString: line.to_string(),
                            });
                        }
                    }
                }
            }

            HttpResponse::Ok().json(process_list)
        }
        Err(_) => HttpResponse::InternalServerError().body("Failed to execute command"),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(monitor_commands)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}