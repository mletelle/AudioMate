group "default" {
  targets = ["audiomate"]
}

target "audiomate" {
  context = "."
  dockerfile = "Dockerfile"
  tags = ["audiomate:latest"]
  platforms = ["linux/amd64"]
  output = ["type=docker"]
}
