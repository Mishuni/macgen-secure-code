Rails.application.routes.draw do
  post '/heartbeat', to: 'heartbeats#create'
  post '/services', to: 'services#index'
end