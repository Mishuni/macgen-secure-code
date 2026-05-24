<?php

use App\Http\Controllers\EntryController;

$router->group(['prefix' => 'entries'], function () use ($router) {
    $router->get('/', [EntryController::class, 'index']);
    $router->post('/', [EntryController::class, 'store']);
    $router->get('/{entryId}', [EntryController::class, 'show']);
    $router->put('/{entryId}', [EntryController::class, 'update']);
    $router->get('/{entryId}/edits', [EntryController::class, 'edits']);
});