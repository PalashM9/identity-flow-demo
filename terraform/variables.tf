variable "postgres_db" {
  type        = string
  description = "PostgreSQL database name"
  default     = "identity_demo"
}

variable "postgres_user" {
  type        = string
  description = "PostgreSQL user"
  default     = "identity_user"
}

variable "postgres_password" {
  type        = string
  description = "PostgreSQL password"
  sensitive   = true
}

variable "api_username" {
  type        = string
  description = "Basic Auth username for local demo"
  default     = "demo_user"
}

variable "api_password" {
  type        = string
  description = "Basic Auth password for local demo"
  sensitive   = true
}

variable "webhook_secret" {
  type        = string
  description = "Webhook HMAC secret"
  sensitive   = true
}