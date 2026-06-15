import pandas as pd
import numpy as np
import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
from pipelines.data_cleaning_pipeline import DataCleaningPipeline

@pytest.mark.IT_preprocessing_pipeline
def test_full_pipeline_execution(tmp_path):
    """
    Tag: IT_preprocessing_pipeline
    Purpose: Ensure modules interact correctly when chained together in the pipeline.
    """
    raw_dir = tmp_path / "raw"
    proc_dir = tmp_path / "proc"
    raw_dir.mkdir()
    proc_dir.mkdir()
    
    df = pd.DataFrame({
        'id': [1, 2, 2],
        'age': [np.nan, 25, 25]
    })
    raw_file = raw_dir / "test.csv"
    df.to_csv(raw_file, index=False)
    
    pipeline = DataCleaningPipeline(raw_data_dir=str(raw_dir), processed_data_dir=str(proc_dir))
    clean_results = pipeline.run_pipeline(
        filename='test.csv',
        scale_method='minmax',
        output_filename='out.csv'
    )
    
    clean_df = clean_results['ml_ready']
    
    assert len(clean_df) == 2 # 1 exact duplicate dropped
    assert 'age' in clean_df.columns
    assert not clean_df.isnull().any().any()
