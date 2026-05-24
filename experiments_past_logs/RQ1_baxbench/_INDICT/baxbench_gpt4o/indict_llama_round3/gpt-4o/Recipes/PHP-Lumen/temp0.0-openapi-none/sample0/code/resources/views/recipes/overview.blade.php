<!DOCTYPE html>
<html>
<head>
    <title>Recipe Overview</title>
</head>
<body>
    <h1>Recipes</h1>
    <ul>
        @foreach ($recipes as $recipe)
            <li><a href="/recipes/{{ $recipe->id }}">{{ htmlspecialchars($recipe->title, ENT_QUOTES, 'UTF-8') }}</a></li>
        @endforeach
    </ul>
</body>
</html>