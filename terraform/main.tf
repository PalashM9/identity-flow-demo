terraform {
  required_version = ">= 1.6.0"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.6"
    }
  }
}

provider "docker" {}

resource "docker_network" "identity_network" {
  name = "identity-demo-network"
}

resource "docker_volume" "postgres_data" {
  name = "identity-demo-postgres-data"
}

resource "docker_image" "postgres" {
  name         = "postgres:16-alpine"
  keep_locally = true
}

resource "docker_container" "postgres" {
  name  = "identity-demo-postgres"
  image = docker_image.postgres.image_id

  networks_advanced {
    name = docker_network.identity_network.name
  }

  env = [
    "POSTGRES_DB=${var.postgres_db}",
    "POSTGRES_USER=${var.postgres_user}",
    "POSTGRES_PASSWORD=${var.postgres_password}"
  ]

  volumes {
    volume_name    = docker_volume.postgres_data.name
    container_path = "/var/lib/postgresql/data"
  }

  ports {
    internal = 5432
    external = 5432
  }
}

resource "docker_image" "receiver" {
  name = "identity-demo-receiver:local"

  build {
    context = "${path.module}/../receiver"
  }
}

resource "docker_container" "receiver" {
  name  = "identity-demo-receiver"
  image = docker_image.receiver.image_id

  networks_advanced {
    name = docker_network.identity_network.name
  }

  env = [
    "WEBHOOK_SECRET=${var.webhook_secret}"
  ]

  ports {
    internal = 3001
    external = 3001
  }
}

resource "docker_image" "api" {
  name = "identity-demo-api:local"

  build {
    context = "${path.module}/../api"
  }
}

resource "docker_container" "api" {
  name  = "identity-demo-api"
  image = docker_image.api.image_id

  networks_advanced {
    name = docker_network.identity_network.name
  }

  env = [
    "DATABASE_URL=postgresql+psycopg://${var.postgres_user}:${var.postgres_password}@postgres:5432/${var.postgres_db}",
    "API_USERNAME=${var.api_username}",
    "API_PASSWORD=${var.api_password}",
    "WEBHOOK_URL=http://receiver:3001/webhooks/identity",
    "WEBHOOK_SECRET=${var.webhook_secret}",
    "LOG_LEVEL=INFO"
  ]

  ports {
    internal = 8000
    external = 8000
  }

  depends_on = [
    docker_container.postgres,
    docker_container.receiver
  ]
}