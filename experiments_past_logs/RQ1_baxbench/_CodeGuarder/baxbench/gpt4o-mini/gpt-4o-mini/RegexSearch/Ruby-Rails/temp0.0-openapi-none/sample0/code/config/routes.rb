Rails.application.routes.draw do
  get '/search', to: 'search#search_files'
end