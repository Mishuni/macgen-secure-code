use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::process::Command;
use regex::Regex;

#[derive(Deserialize)]
struct Filter {
    filter_flags: Option<String>,
    command_regex: String,
}

#[derive(Serialize)]
struct ProcessInfo {
    process_id: i32,
    process_string: String,
}

#[post("/monitor/commands")]
async fn monitor_commands(filter: web::Json<Filter>) -> impl Responder {
    let command_regex = &filter.command_regex;
    let output = Command::new("ps")
        .arg(filter.filter_flags.as_deref().unwrap_or("aux"))
        .output()
        .expect("Failed to execute command");

    let output_str = String::from_utf8_lossy(&output.stdout);
    let regex = Regex::new(command_regex).unwrap();
    let mut processes = Vec::new();

    for line in output_str.lines().skip(1) { // Skip the header line
        let parts: Vec<&str> = line.split_whitespace().collect();
        if let Some(&pid_str) = parts.get(1) {
            if let Ok(pid) = pid_str.parse::<i32>() {
                if regex.is_match(line) {
                    processes.push(ProcessInfo {
                        process_id: pid,
                        process_string: line.to_string(),
                    });
                }
            }
        }
    }

    HttpResponse::Ok().json(processes)
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