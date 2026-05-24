<?php

use App\Http\Controllers\ProcessController;

$router->post('/monitor/commands', [ProcessController::class, 'getProcesses']);