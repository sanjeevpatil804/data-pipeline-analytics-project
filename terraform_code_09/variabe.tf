variable "project" {
  description = "Your GCP Project ID"
  default = "opportune-balm-376017"
}

variable "region" {
  #description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default = "EU"
 
}

variable "storage_class" {
  description = "Storage class type for your bucket. Check official docs for more info."
  default = "MULTI_REGIONAL"
}

variable "BQ_DATASET" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type = string
  default = "Group_0909"
}

