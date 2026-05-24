<!DOCTYPE html>
<html>
<head>
    <title>{{ $entry->title }}</title>
</head>
<body>
    <h1>{{ $entry->title }}</h1>
    <p>{{ $entry->content }}</p>
    <p>Last modified by: {{ $entry->lastModifiedBy }} on {{ $entry->lastModifiedAt }}</p>
</body>
</html>