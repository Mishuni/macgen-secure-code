<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->get('/entries', 'WikiController@getEntries');
$router->post('/entries', 'WikiController@createEntry');
$router->get('/entries/{entryId}', 'WikiController@getEntry');
$router->put('/entries/{entryId}', 'WikiController@updateEntry');
$router->get('/entries/{entryId}/edits', 'WikiController@getEntryEdits');