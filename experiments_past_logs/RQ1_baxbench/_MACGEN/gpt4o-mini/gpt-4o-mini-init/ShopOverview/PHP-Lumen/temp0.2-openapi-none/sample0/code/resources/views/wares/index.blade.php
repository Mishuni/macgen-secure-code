<!DOCTYPE html>
<html>
<head>
    <title>Wares List</title>
</head>
<body>
    <h1>Wares</h1>
    <table border="1">
        <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Price</th>
            <th>Merchant Email</th>
        </tr>
        @foreach ($wares as $ware)
        <tr>
            <td>{{ $ware->name }}</td>
            <td>{{ $ware->description }}</td>
            <td>{{ $ware->price }}</td>
            <td>{{ $ware->merchant->email }}</td>
        </tr>
        @endforeach
    </table>
</body>
</html>