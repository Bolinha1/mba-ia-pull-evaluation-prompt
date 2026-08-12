"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """
    Faz pull do prompt do LangSmith Hub e salva localmente.

    Returns:
        True se sucesso, False caso contrário
    """
    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return False

    prompt_name = "leonanluppi/bug_to_user_story_v1"
    output_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v1.yml"

    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")
    print(f"Prompt: {prompt_name}")
    print(f"Destino: {output_path}\n")

    try:
        print("Fazendo pull do prompt...")
        prompt = hub.pull(prompt_name)
        print("   ✓ Prompt carregado com sucesso do Hub")

        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": "",
                "user_prompt": "",
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"],
            }
        }

        messages = prompt.messages if hasattr(prompt, "messages") else []
        for msg in messages:
            template = msg.prompt.template if hasattr(msg, "prompt") else str(msg)
            if hasattr(msg, "prompt") and "system" in type(msg).__name__.lower():
                prompt_data["bug_to_user_story_v1"]["system_prompt"] = template
            elif hasattr(msg, "prompt"):
                prompt_data["bug_to_user_story_v1"]["user_prompt"] = template

        if save_yaml(prompt_data, str(output_path)):
            print(f"   ✓ Prompt salvo em: {output_path}")
            return True
        else:
            print("   ✗ Erro ao salvar prompt")
            return False

    except Exception as e:
        print(f"   ✗ Erro ao fazer pull: {e}")
        return False


def main():
    """Função principal"""
    success = pull_prompts_from_langsmith()
    if success:
        print("\n✅ Pull concluído com sucesso!")
        return 0
    else:
        print("\n❌ Pull falhou. Verifique as credenciais e tente novamente.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
