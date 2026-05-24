<!DOCTYPE html>
<html>
<head>
    <title>Edit History</title>
</head>
<body>
    <h1>Edit History</h1>
    <ul>
        @foreach ($edits as $edit)
            <li>
                <p>Modified by: {{ $edit->modifiedBy }} on {{ $edit->modifiedAt }}</p>
                <p>Summary: {{ $edit->summary }}</p>
                <p>Content: {{ $edit->content }}</p>
            </li>
        @endforeach
    </ul>
</body>
</html>