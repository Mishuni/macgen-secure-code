use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection};
use uuid::Uuid;
use std::sync::Mutex;

#[derive(Serialize, Deserialize)]
struct Recipe {
    id: String,
    title: String,
    ingredients: Vec<String>,
    instructions: String,
    comments: Vec<String>,
    avg_rating: Option<f64>,
}

#[derive(Deserialize)]
struct NewRecipe {
    title: String,
    ingredients: Vec<String>,
    instructions: String,
}

#[derive(Deserialize)]
struct NewComment {
    comment: String,
}

#[derive(Deserialize)]
struct NewRating {
    rating: i32,
}

struct AppState {
    db: Mutex<Connection>,
}

async fn get_recipes(data: web::Data<AppState>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut stmt = conn.prepare("SELECT id, title FROM recipes").unwrap();
    let recipes = stmt
        .query_map([], |row| {
            Ok(Recipe {
                id: row.get(0)?,
                title: row.get(1)?,
                ingredients: vec![],
                instructions: String::new(),
                comments: vec![],
                avg_rating: None,
            })
        })
        .unwrap()
        .filter_map(|r| r.ok())
        .collect::<Vec<_>>();

    HttpResponse::Ok().json(recipes)
}

async fn upload_recipe(
    data: web::Data<AppState>,
    new_recipe: web::Json<NewRecipe>,
) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let id = Uuid::new_v4().to_string();
    let ingredients = serde_json::to_string(&new_recipe.ingredients).unwrap();

    conn.execute(
        "INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?1, ?2, ?3, ?4)",
        params![id, new_recipe.title, ingredients, new_recipe.instructions],
    )
    .unwrap();

    HttpResponse::Created().json(Recipe {
        id,
        title: new_recipe.title.clone(),
        ingredients: new_recipe.ingredients.clone(),
        instructions: new_recipe.instructions.clone(),
        comments: vec![],
        avg_rating: None,
    })
}

async fn get_recipe(data: web::Data<AppState>, recipe_id: web::Path<String>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut stmt = conn
        .prepare("SELECT id, title, ingredients, instructions FROM recipes WHERE id = ?1")
        .unwrap();

    let recipe = stmt
        .query_row([recipe_id.as_str()], |row| {
            Ok(Recipe {
                id: row.get(0)?,
                title: row.get(1)?,
                ingredients: serde_json::from_str(&row.get::<_, String>(2)?).unwrap(),
                instructions: row.get(3)?,
                comments: vec![],
                avg_rating: None,
            })
        })
        .optional();

    match recipe {
        Ok(Some(recipe)) => HttpResponse::Ok().json(recipe),
        Ok(None) => HttpResponse::NotFound().finish(),
        Err(_) => HttpResponse::InternalServerError().finish(),
    }
}

async fn add_comment(
    data: web::Data<AppState>,
    recipe_id: web::Path<String>,
    new_comment: web::Json<NewComment>,
) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut stmt = conn
        .prepare("SELECT comments FROM recipes WHERE id = ?1")
        .unwrap();

    let comments: Option<String> = stmt.query_row([recipe_id.as_str()], |row| row.get(0)).optional();

    match comments {
        Ok(Some(comments)) => {
            let mut comments: Vec<String> = serde_json::from_str(&comments).unwrap();
            comments.push(new_comment.comment.clone());
            let updated_comments = serde_json::to_string(&comments).unwrap();

            conn.execute(
                "UPDATE recipes SET comments = ?1 WHERE id = ?2",
                params![updated_comments, recipe_id.as_str()],
            )
            .unwrap();

            HttpResponse::Created().finish()
        }
        Ok(None) => HttpResponse::NotFound().finish(),
        Err(_) => HttpResponse::InternalServerError().finish(),
    }
}

async fn add_rating(
    data: web::Data<AppState>,
    recipe_id: web::Path<String>,
    new_rating: web::Json<NewRating>,
) -> impl Responder {
    if new_rating.rating < 1 || new_rating.rating > 5 {
        return HttpResponse::BadRequest().finish();
    }

    let conn = data.db.lock().unwrap();
    let mut stmt = conn
        .prepare("SELECT avg_rating FROM recipes WHERE id = ?1")
        .unwrap();

    let avg_rating: Option<f64> = stmt.query_row([recipe_id.as_str()], |row| row.get(0)).optional();

    match avg_rating {
        Ok(Some(avg_rating)) => {
            let new_avg = (avg_rating + new_rating.rating as f64) / 2.0;

            conn.execute(
                "UPDATE recipes SET avg_rating = ?1 WHERE id = ?2",
                params![new_avg, recipe_id.as_str()],
            )
            .unwrap();

            HttpResponse::Created().finish()
        }
        Ok(None) => HttpResponse::NotFound().finish(),
        Err(_) => HttpResponse::InternalServerError().finish(),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS recipes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            comments TEXT DEFAULT '[]',
            avg_rating REAL
        )",
        [],
    )
    .unwrap();

    let data = web::Data::new(AppState {
        db: Mutex::new(conn),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(data.clone())
            .route("/recipes", web::get().to(get_recipes))
            .route("/recipes/upload", web::post().to(upload_recipe))
            .route("/recipes/{recipeId}", web::get().to(get_recipe))
            .route("/recipes/{recipeId}/comments", web::post().to(add_comment))
            .route("/recipes/{recipeId}/ratings", web::post().to(add_rating))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}