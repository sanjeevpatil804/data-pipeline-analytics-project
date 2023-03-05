import os

from pathlib import Path
from datetime import datetime

from airflow import DAG
from airflow.models.baseoperator import chain
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryCreateEmptyDatasetOperator,
    BigQueryDeleteDatasetOperator,
    BigQueryCreateEmptyTableOperator,
)
from airflow.providers.google.cloud.transfers.local_to_gcs import (
    LocalFilesystemToGCSOperator,
)
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import (
    GCSToBigQueryOperator,
)
from great_expectations_provider.operators.great_expectations import (
    GreatExpectationsOperator,
)
from google.cloud import storage
storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024* 1024  # 5 MB
storage.blob._MAX_MULTIPART_SIZE = 5 * 1024* 1024  # 5 MB

base_path = Path(__file__).parents[1]
data_file=os.path.join(
    base_path,
    "data",
    "amazon.csv",
)
ge_root_dir = os.path.join(base_path, "config", "ge")

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
gcp_bucket = os.environ.get("GCP_GCS_BUCKET")

bq_dataset = "amazon_data"
bq_table = "amazon_tbl"

gcp_data_dest = "data/amazon.csv"

with DAG(
    "data_ingestion_local_gcs_GroupID09",
    description="Example DAG showcasing loading and data quality checking with amazon data.",
    doc_md=__doc__,
    schedule_interval=None,
    start_date=datetime(2021, 1, 1),
    catchup=False,
) as dag:
    
    create_dataset = BigQueryCreateEmptyDatasetOperator(
        task_id="create_dataset", dataset_id=bq_dataset
    )
    
    upload_amazon_data=LocalFilesystemToGCSOperator(
        task_id="upload_amazon_data",
        src=data_file,
        dst=gcp_data_dest,
        bucket=gcp_bucket,
    )
    create_temp_table = BigQueryCreateEmptyTableOperator(
        task_id="create_temp_table",
        dataset_id=bq_dataset,
        table_id=f"{bq_table}_temp",
        schema_fields=[
            {"name": "product_id", "type": "STRING", "mode": "NULLABLE"},
            {"name": "product_name", "type": "STRING", "mode": "NULLABLE"},
            {"name": "category", "type": "STRING", "mode": "NULLABLE"},
            {"name": "discounted_price", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "actual_price", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "discount_percentage", "type": "STRING", "mode": "NULLABLE"},
            {"name": "rating", "type": "STRING", "mode": "NULLABLE"},
            {"name": "rating_count", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "about_product", "type": "STRING", "mode": "NULLABLE"},
            {"name": "user_id", "type": "STRING", "mode": "NULLABLE"},
            {"name": "user_name", "type": "STRING", "mode": "NULLABLE"},
            {"name": "review_id", "type": "STRING", "mode": "NULLABLE"},
            {"name": "review_title", "type": "STRING", "mode": "NULLABLE"},
            {"name": "review_content", "type": "STRING", "mode": "NULLABLE"},
            {"name": "img_link", "type": "STRING", "mode": "NULLABLE"},
            {"name": "product_link", "type": "STRING", "mode": "NULLABLE"},
        ],
    )
    transfer_amazon_data = GCSToBigQueryOperator(
        task_id="amazon_gcs_to_bigquery",
        bucket=gcp_bucket,
        source_objects=[gcp_data_dest],
        skip_leading_rows=1,
        destination_project_dataset_table="{}.{}.{}".format(PROJECT_ID, bq_dataset, bq_table),
        schema_fields=[
            {"name": "product_id", "type": "STRING", "mode": "NULLABLE"},
            {"name": "product_name", "type": "STRING", "mode": "NULLABLE"},
            {"name": "category", "type": "STRING", "mode": "NULLABLE"},
            {"name": "discounted_price", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "actual_price", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "discount_percentage", "type": "STRING", "mode": "NULLABLE"},
            {"name": "rating", "type": "STRING", "mode": "NULLABLE"},
            {"name": "rating_count", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "about_product", "type": "STRING", "mode": "NULLABLE"},
            {"name": "user_id", "type": "STRING", "mode": "NULLABLE"},
            {"name": "user_name", "type": "STRING", "mode": "NULLABLE"},
            {"name": "review_id", "type": "STRING", "mode": "NULLABLE"},
            {"name": "review_title", "type": "STRING", "mode": "NULLABLE"},
            {"name": "review_content", "type": "STRING", "mode": "NULLABLE"},
            {"name": "img_link", "type": "STRING", "mode": "NULLABLE"},
            {"name": "product_link", "type": "STRING", "mode": "NULLABLE"},
            
        ],
        source_format="CSV",
        create_disposition="CREATE_IF_NEEDED",
        write_disposition="WRITE_TRUNCATE",
        allow_jagged_rows=True,
    )        
    # ge_bigquery_validation_pass = GreatExpectationsOperator(
   #     task_id="ge_bigquery_validation_pass",
   #     data_context_root_dir=ge_root_dir,
   #     checkpoint_name='demo_911_pass_chk',
   #     return_json_dict=True
   # )

   # ge_bigquery_validation_fail = GreatExpectationsOperator(
   #     task_id="ge_bigquery_validation_fail",
   #     data_context_root_dir=ge_root_dir,
   #     checkpoint_name='demo_911_fail_chk',
   #     return_json_dict=True
   # )
   # delete_dataset = BigQueryDeleteDatasetOperator(
   #     task_id="delete_dataset",
   #     project_id=PROJECT_ID,
   #     dataset_id=bq_dataset,
   #     delete_contents=True,
   #     trigger_rule="all_done"
   # )   
    begin = DummyOperator(task_id="begin")
    end = DummyOperator(task_id="end")
    chain(
        begin,
        create_dataset,
        create_temp_table,
        upload_amazon_data,
        transfer_amazon_data,
       # [ge_bigquery_validation_fail,ge_bigquery_validation_pass],
       # delete_dataset,
        end,
    )
