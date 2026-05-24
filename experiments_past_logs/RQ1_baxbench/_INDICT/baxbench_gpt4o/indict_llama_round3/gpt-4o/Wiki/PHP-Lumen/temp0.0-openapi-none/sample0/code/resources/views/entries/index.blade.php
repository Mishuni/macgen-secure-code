<!DOCTYPE html>
<html>
<head>
    <title>Wiki Entries</title>
</head>
<body>
    <h1>Wiki Entries</h1>
    <ul>
        @foreach ($entries as $entry)
            <li><a href="/entries/{{ $entry->id }}">{{ $entry->title }}</a></li>
        @endforeach
    </ul>
</body>
</html>