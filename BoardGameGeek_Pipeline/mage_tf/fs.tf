# fs.tf | File System Configuration

resource "google_filestore_instance" "instance" {
  provider = google-beta
  name = "${var.app_name}"
  location = var.zone
  tier = "BASIC_HDD"

  file_shares {
    capacity_gb = 1024
    name        = "share1"
  }

  networks {
    network = "default"
    modes   = ["MODE_IPV4"]
  }

  depends_on = [google_project_service.filestore]
}

resource "google_vpc_access_connector" "connector" {
  provider = google-beta
  name          = "${var.app_name}-connector"
  ip_cidr_range = "10.8.0.0/28"
  region        = var.region
  network       = "default"
}