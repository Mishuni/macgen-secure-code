<?php

use Illuminate\Support\Facades\Route;

Route::post('/register', 'AuthController@register');
Route::post('/login', 'AuthController@login');
Route::post('/set_secret', 'SecretController@setSecret');
Route::get('/get_secret', 'SecretController@getSecret');