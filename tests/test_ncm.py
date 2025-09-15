from unittest.mock import patch, Mock
from app.db.chroma_db.data_csv.tipi import fetch_ncm_data
import pandas as pd

def test_fetch_ncm_creates_csv(tmp_path):
    output_file = tmp_path / "ncm_test.csv"

    fake_response = {
        "Nomenclaturas": [
            {"Codigo": "8501", "Descricao": "Produto A"},
            {"Codigo": "8502", "Descricao": "Produto B"},
            {"Codigo": "8601", "Descricao": "Produto C"}  
        ]
    }

    with patch("app.util.ncm.requests.get") as mock_get:
        mock_get.return_value = Mock() 
        mock_get.return_value.json.return_value = fake_response 
        mock_get.return_value.raise_for_status = lambda: None  

        fetch_ncm_data(output_csv=str(output_file), filter_number="85")

    df = pd.read_csv(output_file)

    assert len(df) == 2
    assert all(df["Codigo"].astype(str).str.startswith("85"))

    assert "Descricao" in df.columns