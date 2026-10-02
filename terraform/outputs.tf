output "api_url" {
  value = "http://localhost:8000"
}

output "receiver_url" {
  value = "http://localhost:3001"
}

output "demo_command" {
  value = "curl -u ${var.api_username}:<API_PASSWORD> http://localhost:8000/v1/demo-people"
}