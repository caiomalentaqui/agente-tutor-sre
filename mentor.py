import ollama
import json
import os
import re
from rich.console import Console
from rich.markdown import Markdown

console = Console()

# IMPORTANTE: Arquivo de histórico isolado para o Mentor
ARQUIVO_HISTORICO = "historico_mentor.json"
MODELO_LLM = "qwen2.5-coder:7b"

SYSTEM_PROMPT = """
Você é um Staff SRE e Tech Lead Head de Infraestrutura em um grande banco. 
Sua missão não é me ensinar a escovar bits, mas sim guiar a minha CARREIRA e o meu POSICIONAMENTO.

Eu sou um SRE na Camada Zero. Meu objetivo é me consolidar como referência técnica, tirar certificações estratégicas (AWS, Terraform, FinOps) e melhorar minha visibilidade no mercado através do LinkedIn.

REGRAS ABSOLUTAS DE COMPORTAMENTO:
1. PROIBIDO DIZER "COMO POSSO AJUDAR": Se eu mandar um "olá", "oi" ou qualquer saudação simples, VOCÊ ESTÁ PROIBIDO de responder com frases genéricas de assistente (como "Como posso te ajudar?"). 
2. INICIATIVA IMEDIATA: Ao receber uma saudação, assuma imediatamente o controle da reunião. Apresente de cara 3 pautas: 
   - Um direcionamento sobre liderança técnica na Camada Zero.
   - Uma sugestão de tema para o seu próximo post no LinkedIn.
   - Uma cobrança sobre o status do seu roadmap de certificações.
3. TRADUÇÃO PARA NEGÓCIOS: SREs juniores falam de "CPU e RAM". Staff SREs falam de "Redução de Custos, Resiliência e SLA".
4. CRIAÇÃO PARA LINKEDIN: Quando solicitado, crie posts focados em aprendizados reais de infra.

REGRA DE GERAÇÃO DE ARQUIVOS:
Sempre que eu pedir para criar um cronograma ou um post, use a tag:
[ARQUIVO: nome.md]
conteúdo
[/ARQUIVO]
"""

def carregar_historico():
    if os.path.exists(ARQUIVO_HISTORICO):
        with open(ARQUIVO_HISTORICO, 'r', encoding='utf-8') as f:
            mensagens = json.load(f)
            if len(mensagens) > 0 and mensagens[0]['role'] == 'system':
                mensagens[0]['content'] = SYSTEM_PROMPT
            else:
                mensagens.insert(0, {'role': 'system', 'content': SYSTEM_PROMPT})
            return mensagens
    else:
        return [{'role': 'system', 'content': SYSTEM_PROMPT}]

def salvar_historico(mensagens):
    with open(ARQUIVO_HISTORICO, 'w', encoding='utf-8') as f:
        json.dump(mensagens, f, ensure_ascii=False, indent=4)

def iniciar_mentor():
    console.print("[bold magenta]Mentor de Carreira SRE (Staff Level). (Digite 'sair' para encerrar)[/bold magenta]\n")
    mensagens = carregar_historico()
    
    while True:
        pergunta = console.input("[bold green]Você:[/bold green] ").strip()
        if pergunta.lower() == 'sair':
            break
            
        # --- BYPASS DE TEIMOSIA DO QWEN ---
        # Se você mandar só um oi/olá, o script força o contexto sem deixar o modelo responder o padrão
        saudacoes = ['oi', 'olá', 'ola', 'tudo bem', 'bom dia', 'boa tarde', 'boa noite']
        if pergunta.lower() in saudacoes:
            pergunta = "[SISTEMA: O usuário apenas disse um cumprimento simples. NÃO diga 'como posso ajudar'. Assuma as rédeas imediatamente e traga as 3 pautas de carreira: liderança na Camada Zero, LinkedIn e Certificações]."
        # ---------------------------------

        mensagens.append({'role': 'user', 'content': 'oi'}) # Salva o 'oi' limpo no histórico se quiser, ou a pergunta modificada
        
        resposta = ollama.chat(model=MODELO_LLM, messages=mensagens)
        conteudo = resposta['message']['content']
        
        padrao = r'\[ARQUIVO:\s*(.+?)\](.*?)\[/ARQUIVO\]'
        arquivos_encontrados = re.findall(padrao, conteudo, re.DOTALL)
        
        for nome_arquivo, conteudo_arquivo in arquivos_encontrados:
            nome_arquivo = nome_arquivo.strip()
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo_arquivo.strip())
            console.print(f"[bold yellow]💾 O Mentor gerou o documento: {nome_arquivo}[/bold yellow]")
        
        conteudo_limpo = re.sub(padrao, '', conteudo, flags=re.DOTALL).strip()
        
        console.print("\n[bold magenta]Mentor:[/bold magenta]")
        if conteudo_limpo:
            console.print(Markdown(conteudo_limpo))
        console.print("-" * 50)
        
        mensagens.append({'role': 'assistant', 'content': conteudo})
        salvar_historico(mensagens)

if __name__ == "__main__":
    iniciar_mentor()