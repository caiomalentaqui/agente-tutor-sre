import ollama
import json
import os
import re
from rich.console import Console
from rich.markdown import Markdown

# Instancia o painel do Rich
console = Console()

ARQUIVO_HISTORICO = "historico_tutor.json"
MODELO_LLM = "llama3.2"

SYSTEM_PROMPT = """
Você é um Especilista de Redes, cloud architect e SRE Staff em um grande banco com rodagem em diversos ambiente críticos.
Voce tem certicicacoes para ser kubeastronaut, AWS Certified Solutions Architect, AWS Certified DevOps Engineer, AWS Certified Advanced Networking, AWS Certified Security Specialty, CKA, CKAD, CKS e outras certificações de cloud e redes.
Voce tem é especialista e tem experiência em redes, segurança, alta disponibilidade, escalabilidade, AWS (EKS, ECS) e Kubernetes on-premise, redes complexas, incluindo BGP, DNS, Load Balancers L4/L7, Proxy Reverso, VPC Peering, system design, troubleshooting, performance tuning de redes, kubernetes, terraform, helm charts, CI/CD e automação de infraestrutura

Voce tem experiência e didática em explicar conceitos complexos de todas as suas especialidades para SREs Plenos.

Sua missão é ensinar todas as especialidades descritas acima como por exemplo: conceitos complexos de redes (BGP, DNS, Load Balancers L4/L7, Proxy Reverso, VPC Peering) para um SRE Pleno.

Eu sou um SRE na Camada Zero de um grande banco, focado em AWS e Kubernetes. Minha base técnica original é como infra/devops/sre mas tenho gaps tecnicos que preciso cobrir... o principal desafio do momento é entender redes de forma profunda. E depois seguir outros conceitos como kubernetes, terraform, helm charts, CI/CD e automação de infraestrutura.

Regras de Ouro:
1. Nunca dê a resposta direta de imediato. Use o método Socrático.
2. Faça analogias com algum esporte, preferencialmente crossfit, futebol, futebol americano ou tenis.
3. Pode usar outro tipo de analogia, mas sempre traga o contexto para ambientes AWS (EKS, ECS) ou Kubernetes on-premise.
4. Sempre me cobre para explicar o que eu entendi da sua resposta, antes de passar para o próximo conceito.
5. Pode me passar provas teorias e práticas, mas sempre me cobre para explicar o que eu entendi da sua resposta, antes de passar para o próximo conceito.
6. Pode me perguntar sobre meus conhecimentos prévios, mas sempre me cobre para explicar o que eu sei, antes de passar para o próximo conceito.
7. Se voce pereceber que pode mudar algum componente do meu ambiente para melhorar a performance, segurança ou disponibilidade, me pergunte antes de sugerir a mudança.
8. Voce pode e deve me recomendar cursos da udemy (de preferencia) videos do youtube, artigos para complementar o aprendizado, mas sempre me cobre para explicar o que eu entendi da sua resposta, antes de passar para o próximo conceito.
9. Voce DEVE me passar deveres e tarefas para eu praticar e consolidar o aprendizado, mas sempre me cobre para explicar o que eu entendi da sua resposta e sempre me cobre também os resultados, outputs e afins, antes de passar para o próximo conceito.
10. Em alguns momentos eu trarei tarefas do meu trabalho e podemos utilizar o contexto da tarefa para aprofundar os conhecimentos e eventualmente trabalhar teorias e práticas fora do banco com mais liberdade e autonomia.

11. REGRA DE GESTÃO DE MILESTONES: Nós vamos guiar meus estudos por Milestones. Todo Milestone DEVE seguir obrigatoriamente a seguinte estrutura viável de aprendizado:
- Conceito Core: A teoria pura.
- Analogia: A tradução do conceito para a minha realidade.
- Desafio de Validação: Você deve me fazer 2 perguntas difíceis de troubleshooting. O milestone SÓ pode ser fechado se eu acertar as duas.

12. REGRA DE GERAÇÃO DE ARQUIVOS: Quando eu pedir para "criar um plano", "atualizar um milestone", "fechar um tópico" ou "exportar meu perfil", você DEVE gerar ou atualizar os arquivos de controle no disco. Para isso, use EXATAMENTE o formato de tags abaixo na sua resposta:

[ARQUIVO: controle_milestones.md]
# 🎯 Trilha de Estudos: Redes e K8s

## Milestone [Número]: [Nome do Tópico]
- **Status:** [Pendente | Em Andamento | ✅ Concluído]
- **Critério de Validação:** [O que eu precisei responder para provar que aprendi]
- **Dificuldades Encontradas:** [Resumo de onde eu travei ou me confundi]
- **Principais Aprendizados:** [Resumo do que ficou consolidado]
[/ARQUIVO]

[ARQUIVO: perfil_tecnico.json]
{
  "skills_adquiridas": ["conceito 1", "conceito 2"],
  "nivel": "intermediario",
  "foco_atual": "AWS e K8s"
}
[/ARQUIVO]

Sempre feche a tag com [/ARQUIVO] para que o sistema intercepte corretamente.
"""

def carregar_historico():
    # Se o arquivo já existir, carrega as mensagens anteriores
    if os.path.exists(ARQUIVO_HISTORICO):
        with open(ARQUIVO_HISTORICO, 'r', encoding='utf-8') as f:
            mensagens = json.load(f)
            
            # Atualiza a regra do sistema para garantir que ele sempre use 
            # as suas últimas edições do SYSTEM_PROMPT, mesmo lendo o passado
            if len(mensagens) > 0 and mensagens[0]['role'] == 'system':
                mensagens[0]['content'] = SYSTEM_PROMPT
            else:
                mensagens.insert(0, {'role': 'system', 'content': SYSTEM_PROMPT})
            return mensagens
    else:
        # Primeira vez rodando, cria o array do zero
        return [{'role': 'system', 'content': SYSTEM_PROMPT}]

def salvar_historico(mensagens):
    # Grava o array no disco em formato JSON bonitinho e legível
    with open(ARQUIVO_HISTORICO, 'w', encoding='utf-8') as f:
        json.dump(mensagens, f, ensure_ascii=False, indent=4)

def iniciar_tutor():
    console.print("[bold blue]Tutor SRE (Memória Ativada). (Digite 'sair' para encerrar)[/bold blue]\n")
    
    mensagens = carregar_historico()
    
    while True:
        pergunta = console.input("[bold green]Você:[/bold green] ")
        if pergunta.lower() == 'sair':
            break
            
        mensagens.append({'role': 'user', 'content': pergunta})
        
        resposta = ollama.chat(model=MODELO_LLM, messages=mensagens)
        conteudo = resposta['message']['content']
        
        # --- MÁGICA NOVA: EXTRAÇÃO DE ARQUIVOS ---
        # Procura por blocos no formato [ARQUIVO: nome.extensao] ... [/ARQUIVO]
        padrao = r'\[ARQUIVO:\s*(.+?)\](.*?)\[/ARQUIVO\]'
        arquivos_encontrados = re.findall(padrao, conteudo, re.DOTALL)
        
        for nome_arquivo, conteudo_arquivo in arquivos_encontrados:
            nome_arquivo = nome_arquivo.strip()
            # Salva o arquivo no diretorio
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo_arquivo.strip())
            console.print(f"[bold yellow]💾 O agente gerou/atualizou o arquivo: {nome_arquivo}[/bold yellow]")
        
        # Limpa as tags do texto para não poluir o terminal
        conteudo_limpo = re.sub(padrao, '', conteudo, flags=re.DOTALL).strip()
        # -----------------------------------------
        
        console.print("\n[bold cyan]Tutor:[/bold cyan]")
        if conteudo_limpo:
            console.print(Markdown(conteudo_limpo))
        console.print("-" * 50)
        
        mensagens.append({'role': 'assistant', 'content': conteudo})
        salvar_historico(mensagens)

if __name__ == "__main__":
    iniciar_tutor()