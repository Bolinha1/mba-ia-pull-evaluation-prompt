"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "{bug_report}")

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt),
        ])

        print(f"   Fazendo push do prompt: {prompt_name}")
        hub.push(prompt_name, prompt_template, new_repo_is_public=True)
        print(f"   ✓ Prompt publicado com sucesso (PÚBLICO)")
        return True

    except Exception as e:
        print(f"   ✗ Erro ao fazer push: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    required_fields = ["description", "system_prompt", "user_prompt", "version"]
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")
        elif isinstance(prompt_data[field], str) and not prompt_data[field].strip():
            errors.append(f"Campo '{field}' está vazio")

    system_prompt = prompt_data.get("system_prompt", "")
    if "[TODO]" in system_prompt:
        errors.append("system_prompt ainda contém [TODO]")

    user_prompt = prompt_data.get("user_prompt", "")
    if "[TODO]" in user_prompt:
        errors.append("user_prompt ainda contém [TODO]")

    techniques = prompt_data.get("techniques_applied", [])
    if len(techniques) < 2:
        errors.append(f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS AO LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")
    prompt_file = "prompts/bug_to_user_story_v2.yml"

    print(f"Username: {username}")
    print(f"Arquivo: {prompt_file}\n")

    data = load_yaml(prompt_file)
    if not data:
        print("❌ Não foi possível carregar o arquivo de prompts")
        return 1

    prompt_key = list(data.keys())[0]
    prompt_data = data[prompt_key]

    print("Validando prompt...")
    is_valid, errors = validate_prompt(prompt_data)

    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    print("   ✓ Prompt válido\n")

    prompt_name = f"{username}/bug_to_user_story_v2"
    success = push_prompt_to_langsmith(prompt_name, prompt_data)

    if success:
        print(f"\n✅ Push concluído com sucesso!")
        print(f"   Prompt: {prompt_name}")
        print(f"   Dashboard: https://smith.langchain.com/prompts")
        return 0
    else:
        print("\n❌ Push falhou.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
