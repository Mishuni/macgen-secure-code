<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->get('/entries', 'EntryController@index');
$router->post('/entries', 'EntryController@store');
$router->get('/entries/{entryId}', 'EntryController@show');
$router->put('/entries/{entryId}', 'EntryController@update');
$router->get('/entries/{entryId}/edits', 'EditController@index');