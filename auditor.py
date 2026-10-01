import ollama
import json
import os
from rich.console import Console

console = Console()

ARQUIVO_TUTOR = "historico_tutor.json"
MODELO_LLM = "qwen2.5-coder:7b"

SYSTEM_PROMPT = """
Você é um Auditor de Inteligência Artificial. Sua missão é ler a transcrição de uma aula entre um Tutor IA e um Aluno (SRE), e avaliar EXCLUSIVAMENTE a postura do Tutor.
O Tutor foi muito bonzinho? Ele deu a resposta ao invés de usar o método Socrático? Ele ignorou o fato de o aluno ter errado?

REGRA OBRIGATÓRIA: 
A sua saída será injetada diretamente no "cérebro" do Tutor como uma diretriz do sistema.
Escreva APENAS UMA FRASE DIRETA dando uma bronca ou instrução clara para o Tutor usar na próxima interação.
NÃO use saudações. NÃO explique. Seja uma máquina enviando um comando.

Exemplos de saída esperada:
- "FEEDBACK DO SISTEMA: Você está sendo muito permissivo. Na próxima resposta, exija que o aluno digite os comandos do Kubernetes."
- "FEEDBACK DO SISTEMA: Excelente aula. Mantenha o nível de dificuldade alto e inicie o próximo conceito."
"""

def rodar_auditoria():
    console.print("[bold yellow]Iniciando auditoria da memória do Tutor...[/bold yellow]")
    
    if not os.path.exists(ARQUIVO_TUTOR):
        console.print("[bold red]Nenhum histórico do tutor encontrado.[/bold red]")
        return

    # 1. Abre o cérebro do Tutor
    with open(ARQUIVO_TUTOR, 'r', encoding='utf-8') as f:
        historico_tutor = json.load(f)

    # Se tiver menos de 3 mensagens (só o prompt e o oi inicial), não tem o que auditar
    if len(historico_tutor) < 3:
        console.print("[bold yellow]Poucas mensagens para auditar. Volte a estudar![/bold yellow]")
        return

    # 2. Constrói a transcrição para o Auditor ler
    transcricao = "TRANSCRICAO DA AULA:\n\n"
    for msg in historico_tutor:
        if msg['role'] != 'system':
            transcricao += f"{msg['role'].upper()}: {msg['content']}\n\n"

    # 3. Chama o Auditor para analisar
    console.print("[bold yellow]Auditor analisando o comportamento do Tutor...[/bold yellow]")
    mensagens_auditor = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': f"Analise a aula e gere o comando de correção:\n\n{transcricao}"}
    ]
    
    resposta = ollama.chat(model=MODELO_LLM, messages=mensagens_auditor)
    feedback = resposta['message']['content'].strip()
    
    # 4. A MÁGICA: Injeta o feedback como uma mensagem de 'system' no histórico do Tutor
    historico_tutor.append({
        'role': 'system', 
        'content': f"DIRETRIZ INVISÍVEL PARA VOCÊ (TUTOR): {feedback}"
    })

    # Salva o arquivo JSON atualizado
    with open(ARQUIVO_TUTOR, 'w', encoding='utf-8') as f:
        json.dump(historico_tutor, f, ensure_ascii=False, indent=4)

    console.print(f"[bold green]✅ Auditoria concluída! O Tutor foi atualizado com a instrução:[/bold green]")
    console.print(f"[italic cyan]{feedback}[/italic cyan]")

if __name__ == "__main__":
    rodar_auditoria()