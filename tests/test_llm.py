import importlib
from urllib import error

from emmaus.providers.llm import NullLLMProvider, OllamaProvider


def test_ollama_provider_falls_back_when_request_fails(monkeypatch):
    provider = OllamaProvider(
        source_id="local_rules",
        base_url="http://127.0.0.1:11434",
        model="phi3.5",
        request_timeout_seconds=0.1,
    )

    def raise_url_error(*args, **kwargs):
        raise error.URLError("offline")

    monkeypatch.setattr("emmaus.providers.llm.request.urlopen", raise_url_error)
    guidance = provider.generate_guidance("Guide this study session.")
    assert "phi3.5" in guidance
    assert "falling back" in guidance



def test_build_container_uses_null_provider_when_ollama_is_unavailable(tmp_path, monkeypatch):
    monkeypatch.setenv("EMMAUS_DATABASE_PATH", str(tmp_path / "emmaus.sqlite3"))
    monkeypatch.setattr(OllamaProvider, "is_available", staticmethod(lambda base_url, timeout_seconds=0.25: False))

    import emmaus.core.bootstrap as bootstrap_module

    importlib.reload(bootstrap_module)
    container = bootstrap_module.build_container()
    assert isinstance(container.llm_registry.get("local_rules"), NullLLMProvider)



def test_build_container_uses_ollama_provider_when_available(tmp_path, monkeypatch):
    monkeypatch.setenv("EMMAUS_DATABASE_PATH", str(tmp_path / "emmaus.sqlite3"))
    monkeypatch.setenv("EMMAUS_OLLAMA_MODEL", "phi3.5")
    monkeypatch.setattr(OllamaProvider, "is_available", staticmethod(lambda base_url, timeout_seconds=0.25: True))

    import emmaus.core.bootstrap as bootstrap_module

    importlib.reload(bootstrap_module)
    container = bootstrap_module.build_container()
    provider = container.llm_registry.get("local_rules")
    assert isinstance(provider, OllamaProvider)
    assert provider.model == "phi3.5"
