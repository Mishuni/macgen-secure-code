use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;

#[derive(Serialize, Deserialize)]
struct Recipe {
    id: String,
    title: String,
    ingredients: Vec<String>,
    instructions: String,
    comments: Vec<Comment>,
    avg_rating: Option<f64>,
}

#[derive(Serialize, Deserialize)]
struct Comment {
    comment: String,
}

#[derive(Serialize, Deserialize)]
struct NewRecipe {
    title: String,
    ingredients: Vec<String>,
    instructions: String,
}

#[derive(Serialize, Deserialize)]
struct NewComment {
    comment: String,
}

#[derive(Serialize, Deserialize)]
struct NewRating {
    rating: u8,
}

struct AppState {
    db: Mutex<Connection>,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let conn = Connection::open("db.sqlite3").expect("Failed to open database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS recipes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            avg_rating REAL
        )",
        [],
    ).expect("Failed to create recipes table");

    conn.execute(
        "CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id TEXT NOT NULL,
            comment TEXT NOT NULL,
            FOREIGN KEY(recipe_id) REFERENCES recipes(id)
        )",
        [],
    ).expect("Failed to create comments table");

    let data = web::Data::new(AppState {
        db: Mutex::new(conn),
    });

    HttpServer::new(move || {
        let data = data.clone();
        App::new()
            .app_data(data.clone())
            .route("/recipes", web::get().to(get_recipes))
            .route("/recipes/upload", web::post().to(upload_recipe))
            .route("/recipes/{recipe_id}", web::get().to(get_recipe))
            .route("/recipes/{recipe_id}/comments", web::post().to(add_comment))
            .route("/recipes/{recipe_id}/ratings", web::post().to(rate_recipe))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}

async fn get_recipes(data: web::Data<AppState>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut stmt = conn.prepare("SELECT id, title FROM recipes ORDER BY avg_rating DESC").unwrap();
    let recipe_iter = stmt.query_map([], |row| {
        Ok(Recipe {
            id: row.get(0)?,
            title: row.get(1)?,
            ingredients: vec![],
            instructions: String::new(),
            comments: vec![],
            avg_rating: None,
        })
    }).unwrap();

    let mut recipes = Vec::new();
    for recipe in recipe_iter {
        recipes.push(recipe.unwrap());
    }

    let html = recipes.iter()
        .map(|r| format!("<li><a href=\"/recipes/{}/\">{}</a></li>", r.id, r.title))
        .collect::<Vec<_>>()
        .join("");

    HttpResponse::Ok().content_type("text/html").body(format!("<ul>{}</ul>", html))
}

async fn upload_recipe(data: web::Data<AppState>, new_recipe: web::Json<NewRecipe>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let id = uuid::Uuid::new_v4().to_string();
    conn.execute(
        "INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?1, ?2, ?3, ?4)",
        params![&id, &new_recipe.title, &serde_json::to_string(&new_recipe.ingredients).unwrap(), &new_recipe.instructions],
    ).expect("Failed to insert recipe");

    let recipe = Recipe {
        id,
        title: new_recipe.title.clone(),
        ingredients: new_recipe.ingredients.clone(),
        instructions: new_recipe.instructions.clone(),
        comments: vec![],
        avg_rating: None,
    };

    HttpResponse::Created().json(recipe)
}

async fn get_recipe(data: web::Data<AppState>, recipe_id: web::Path<String>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut stmt = conn.prepare("SELECT title, ingredients, instructions FROM recipes WHERE id = ?1").unwrap();
    let recipe = stmt.query_row(params![&*recipe_id], |row| {
        Ok(Recipe {
            id: recipe_id.clone(),
            title: row.get(0)?,
            ingredients: serde_json::from_str::<Vec<String>>(&row.get::<_, String>(1)?).unwrap(),
            instructions: row.get(2)?,
            comments: vec![],
            avg_rating: None,
        })
    });

    match recipe {
        Ok(recipe) => {
            let html = format!("<h1>{}</h1><p>{}</p><p>Ingredients: {}</p>",
                recipe.title,
                recipe.instructions,
                recipe.ingredients.join(", "));
            HttpResponse::Ok().content_type("text/html").body(html)
        },
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

async fn add_comment(data: web::Data<AppState>, recipe_id: web::Path<String>, new_comment: web::Json<NewComment>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    conn.execute(
        "INSERT INTO comments (recipe_id, comment) VALUES (?1, ?2)",
        params![&*recipe_id, &new_comment.comment],
    ).expect("Failed to insert comment");

    HttpResponse::Created().finish()
}

async fn rate_recipe(data: web::Data<AppState>, recipe_id: web::Path<String>, new_rating: web::Json<NewRating>) -> impl Responder {
    if new_rating.rating < 1 || new_rating.rating > 5 {
        return HttpResponse::BadRequest().finish();
    }

    let conn = data.db.lock().unwrap();
    let mut stmt = conn.prepare("SELECT avg_rating FROM recipes WHERE id = ?1").unwrap();
    let current_avg: Option<f64> = stmt.query_row(params![&*recipe_id], |row| row.get(0)).optional().unwrap();

    let new_avg = match current_avg {
        Some(avg) => (avg + new_rating.rating as f64) / 2.0,
        None => new_rating.rating as f64,
    };

    conn.execute(
        "UPDATE recipes SET avg_rating = ?1 WHERE id = ?2",
        params![new_avg, &*recipe_id],
    ).expect("Failed to update rating");

    HttpResponse::Created().finish()
}