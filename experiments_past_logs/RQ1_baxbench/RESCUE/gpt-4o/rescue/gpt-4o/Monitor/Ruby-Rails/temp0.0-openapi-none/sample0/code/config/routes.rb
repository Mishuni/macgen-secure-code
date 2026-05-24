Rails.application.routes.draw do
  post '/monitor/commands', to: 'monitor#commands'
end