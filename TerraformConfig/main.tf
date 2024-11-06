resource "random_pet" "name" {
  count = var.pets
  }

resource "random_pet" "pet2" {
  }