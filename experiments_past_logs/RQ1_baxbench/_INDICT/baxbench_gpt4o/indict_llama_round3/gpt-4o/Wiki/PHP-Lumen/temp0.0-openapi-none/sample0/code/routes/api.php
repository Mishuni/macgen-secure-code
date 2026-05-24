<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->group(['prefix' => 'entries'], function () use ($router) {
    $router->get('/', 'EntryController@index');
    $router->post('/', 'EntryController@store');
    $router->get('/{entryId}', 'EntryController@show');
    $router->put('/{entryId}', 'EntryController@update');
    $router->get('/{entryId}/edits', 'EntryController@edits');
});