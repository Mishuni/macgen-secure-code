<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wares</title>
</head>
<body>
    <h1>Available Wares</h1>
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Price</th>
            </tr>
        </thead>
        <tbody>
            @foreach ($wares as $ware)
                <tr>
                    <td>{{ $ware->name }}</td>
                    <td>{{ $ware->description }}</td>
                    <td>{{ $ware->price }}</td>
                </tr>
            @endforeach
        </tbody>
    </table>
</body>
</html>