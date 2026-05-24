Rails.application.routes.draw do
  post '/compile', to: 'application#compile'
end