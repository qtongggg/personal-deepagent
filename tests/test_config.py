def test_settings_load_defaults():
    from src.config import get_settings
    settings = get_settings()
    assert settings.CATALOG_CSV_PATH == "data/catalog.csv"
    assert settings.SIMILARITY_THRESHOLD == 0.4
