resource "google_bigquery_dataset" "dataset1" {
  dataset_id = var.BQ_DATASET
  project    = var.project
  location   = var.region
}