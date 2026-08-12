"""
Testes automatizados para validacao de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


class TestPrompts:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Carrega o prompt v2 antes de cada teste."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
        self.data = load_prompts(str(prompt_path))
        self.prompt_key = list(self.data.keys())[0]
        self.prompt = self.data[self.prompt_key]

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e nao esta vazio."""
        assert "system_prompt" in self.prompt, "Campo 'system_prompt' nao encontrado"
        system_prompt = self.prompt["system_prompt"]
        assert system_prompt is not None, "system_prompt e None"
        assert isinstance(system_prompt, str), "system_prompt nao e string"
        assert len(system_prompt.strip()) > 0, "system_prompt esta vazio"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: 'Voce e um Product Manager')."""
        system_prompt = self.prompt.get("system_prompt", "").lower()
        role_keywords = [
            "voce e um", "voce e uma",
            "product manager", "business analyst", "especialista",
            "# papel", "# role"
        ]
        has_role = any(keyword in system_prompt for keyword in role_keywords)
        assert has_role, (
            "Prompt nao define uma persona/role. "
            "Esperado: palavras como 'Voce e um Product Manager' ou secao '# PAPEL'"
        )

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrao."""
        system_prompt = self.prompt.get("system_prompt", "").lower()
        format_keywords = [
            "markdown", "user story", "como um", "eu quero", "para que",
            "given-when-then", "dado que", "quando", "entao",
            "criterios de aceitacao"
        ]
        has_format = any(keyword in system_prompt for keyword in format_keywords)
        assert has_format, (
            "Prompt nao menciona formato esperado (Markdown, User Story, Given-When-Then)"
        )

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contem exemplos de entrada/saida (tecnica Few-shot)."""
        system_prompt = self.prompt.get("system_prompt", "")
        example_count = sum(1 for kw in [
            "Exemplo 1", "Exemplo 2", "Exemplo 3",
            "## Exemplo", "Example 1", "Example 2"
        ] if kw in system_prompt)
        has_examples = example_count >= 2
        assert has_examples, (
            f"Prompt nao contem exemplos Few-shot suficientes (encontrados: {example_count}). "
            "Esperado: pelo menos 2 exemplos de entrada/saida"
        )

    def test_prompt_no_todos(self):
        """Garante que voce nao esqueceu nenhum [TODO] no texto."""
        system_prompt = self.prompt.get("system_prompt", "")
        user_prompt = self.prompt.get("user_prompt", "")
        description = self.prompt.get("description", "")
        full_text = f"{system_prompt} {user_prompt} {description}"
        assert "[TODO]" not in full_text, (
            "Prompt ainda contem '[TODO]'. Remova todos os TODOs antes de submeter."
        )

    def test_minimum_techniques(self):
        """Verifica (atraves dos metadados do yaml) se pelo menos 2 tecnicas foram listadas."""
        techniques = self.prompt.get("techniques_applied", [])
        assert isinstance(techniques, list), "techniques_applied deve ser uma lista"
        assert len(techniques) >= 2, (
            f"Minimo de 2 tecnicas requeridas, encontradas: {len(techniques)}. "
            f"Tecnicas: {techniques}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
