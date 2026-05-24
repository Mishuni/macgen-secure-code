<!DOCTYPE html>
<html>
<head>
    <title>{{ htmlspecialchars($recipe->title, ENT_QUOTES, 'UTF-8') }}</title>
</head>
<body>
    <h1>{{ htmlspecialchars($recipe->title, ENT_QUOTES, 'UTF-8') }}</h1>
    <h2>Ingredients</h2>
    <ul>
        @foreach ($recipe->ingredients as $ingredient)
            <li>{{ htmlspecialchars($ingredient, ENT_QUOTES, 'UTF-8') }}</li>
        @endforeach
    </ul>
    <h2>Instructions</h2>
    <p>{{ htmlspecialchars($recipe->instructions, ENT_QUOTES, 'UTF-8') }}</p>
    <h2>Comments</h2>
    <ul>
        @foreach ($recipe->comments as $comment)
            <li>{{ htmlspecialchars($comment->comment, ENT_QUOTES, 'UTF-8') }}</li>
        @endforeach
    </ul>
    <h2>Average Rating</h2>
    <p>{{ $recipe->ratings->avg('rating') ?? 'No ratings yet' }}</p>
</body>
</html>