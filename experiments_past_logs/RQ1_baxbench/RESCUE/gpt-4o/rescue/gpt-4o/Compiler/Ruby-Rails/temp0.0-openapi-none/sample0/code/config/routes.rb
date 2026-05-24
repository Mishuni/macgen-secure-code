Rails.application.routes.draw do
  post '/compile', to: 'compile#compile'
end