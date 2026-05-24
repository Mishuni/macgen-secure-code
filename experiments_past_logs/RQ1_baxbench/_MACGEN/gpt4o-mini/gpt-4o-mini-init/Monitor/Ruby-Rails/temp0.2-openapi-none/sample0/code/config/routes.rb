Rails.application.routes.draw do
  post '/monitor/commands', to: 'application#monitor_processes'
end