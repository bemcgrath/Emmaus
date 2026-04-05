from __future__ import annotations

from pathlib import Path

from emmaus.domain.models import PassageReference, PassageText, TextSourceDescriptor
from emmaus.providers.text import LocalJsonBibleTextProvider, RemoteApiBibleTextProvider, TextProviderRegistry


class TextSourceService:
    def __init__(self, registry: TextProviderRegistry, data_dir: Path, default_source: str) -> None:
        self.registry = registry
        self.data_dir = data_dir
        self.default_source = default_source

    def list_sources(self) -> list[TextSourceDescriptor]:
        return self.registry.list()

    def register_local_source(self, source_id: str, name: str, file_path: str, license_name: str) -> TextSourceDescriptor:
        provider = LocalJsonBibleTextProvider(
            source_id=source_id,
            name=name,
            file_path=Path(file_path),
            license_name=license_name,
        )
        self.registry.register(provider)
        return provider.descriptor

    def register_api_source(
        self,
        source_id: str,
        name: str,
        base_url: str,
        api_key: str | None,
        license_name: str,
    ) -> TextSourceDescriptor:
        provider = RemoteApiBibleTextProvider(
            source_id=source_id,
            name=name,
            base_url=base_url,
            api_key=api_key,
            license_name=license_name,
        )
        self.registry.register(provider)
        return provider.descriptor

    def get_passage(self, reference: PassageReference, source_id: str | None = None) -> PassageText:
        resolved_source = source_id or self.default_source
        provider = self.registry.get(resolved_source)
        return provider.get_passage(reference)
