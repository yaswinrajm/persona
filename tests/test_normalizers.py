from app.normalizers.canonical import normalize_city, normalize_company, normalize_skill


def test_city_alias_normalization() -> None:
    assert normalize_city("Bangalore") == "Bengaluru"


def test_company_alias_normalization() -> None:
    assert normalize_company("TCS") == "Tata Consultancy Services"


def test_skill_alias_normalization() -> None:
    assert normalize_skill("ML") == "Machine Learning"
