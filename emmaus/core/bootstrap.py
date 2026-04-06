from emmaus.core.config import Settings
from emmaus.providers.commentary import CommentaryProviderRegistry, NotesPlaceholderCommentaryProvider
from emmaus.providers.llm import LLMProviderRegistry, NullLLMProvider, OllamaProvider
from emmaus.providers.text import LocalJsonBibleTextProvider, RemoteApiBibleTextProvider, TextProviderRegistry
from emmaus.repositories.study import SQLiteStudyRepository
from emmaus.services.agent import AdaptiveStudyAgent
from emmaus.services.personalization import PersonalizationService
from emmaus.services.study import StudyService
from emmaus.services.text import TextSourceService


class Container:
    def __init__(self) -> None:
        self.settings = Settings()
        self.text_registry = TextProviderRegistry()
        self.commentary_registry = CommentaryProviderRegistry()
        self.llm_registry = LLMProviderRegistry()
        self.study_repository = SQLiteStudyRepository(self.settings.database_path)
        self.text_service = TextSourceService(
            registry=self.text_registry,
            data_dir=self.settings.data_dir,
            default_source=self.settings.default_text_source,
        )
        self.study_service = StudyService(
            repository=self.study_repository,
            history_limit=self.settings.study_history_limit,
        )
        self.personalization_service = PersonalizationService(
            self.study_service,
            self.text_service,
            self.llm_registry,
        )
        self.agent_service = AdaptiveStudyAgent(
            study_service=self.study_service,
            personalization_service=self.personalization_service,
            text_service=self.text_service,
            commentary_registry=self.commentary_registry,
            llm_registry=self.llm_registry,
            default_commentary_source=self.settings.default_commentary_source,
        )



def build_container() -> Container:
    container = Container()
    data_dir = container.settings.data_dir
    data_dir.mkdir(parents=True, exist_ok=True)

    sample_file = data_dir / "sample_kjv_excerpt.json"
    if sample_file.exists():
        container.text_registry.register(
            LocalJsonBibleTextProvider(
                source_id="sample_local",
                name="Sample Public Domain Local Source",
                file_path=sample_file,
                license_name="Public Domain",
            )
        )

    container.text_registry.register(
        RemoteApiBibleTextProvider(
            source_id="user_api_placeholder",
            name="User API Placeholder",
            base_url="https://example-bible-api.invalid",
            api_key=None,
            license_name="User Supplied",
        )
    )

    container.commentary_registry.register(
        NotesPlaceholderCommentaryProvider(
            source_id="notes_placeholder",
            name="Commentary Placeholder",
        )
    )

    if OllamaProvider.is_available(
        base_url=container.settings.ollama_base_url,
        timeout_seconds=container.settings.ollama_connect_timeout_seconds,
    ):
        container.llm_registry.register(
            OllamaProvider(
                source_id="local_rules",
                base_url=container.settings.ollama_base_url,
                model=container.settings.ollama_model,
                request_timeout_seconds=container.settings.ollama_request_timeout_seconds,
            )
        )
    else:
        container.llm_registry.register(NullLLMProvider(source_id="local_rules"))
    return container
