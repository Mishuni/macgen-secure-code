Rails.application.routes.draw do
  post '/heartbeat', to: 'heartbeat#register'
  post '/services', to: 'services#overview'
end