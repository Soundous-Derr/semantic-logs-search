# Create a small sample Parquet from the processed logs (uses PySpark)
from pyspark.sql import SparkSession
import os

if __name__ == "__main__":
    spark = SparkSession.builder.master("local[1]").appName("CreateSampleParquet").getOrCreate()
    src = "data/processed/logs_parsed"
    dst = "data/processed/logs_parsed_sample"
    n = 1000  # keep small to speed up vectorization

    if not os.path.exists(src):
        print(f"Source parquet not found: {src}")
        spark.stop()
        raise SystemExit(1)

    df = spark.read.parquet(src)
    df.limit(n).write.mode("overwrite").parquet(dst)
    print(f"Wrote sample parquet ({n} rows) to {dst}")
    spark.stop()
