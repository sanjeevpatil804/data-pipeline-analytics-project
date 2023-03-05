provider "google" {
   
   project = var.project
  
  region  = var.region
   credentials=file("opportune-balm-376017-baff598bcbd9.json") 
 
}


resource "google_storage_bucket" "group009" {
  name = "gpp09"
  location = var.region
  storage_class = "MULTI_REGIONAL"
  uniform_bucket_level_access = true

  versioning {
    enabled     = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30  // days
    }
  }

  force_destroy = true
}

