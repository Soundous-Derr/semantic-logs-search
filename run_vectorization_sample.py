from src.vectorization import VectorizationPipeline

if __name__ == "__main__":
    pipeline = VectorizationPipeline()
    success = pipeline.run("data/processed/logs_parsed_sample")
    if not success:
        raise SystemExit(1)
