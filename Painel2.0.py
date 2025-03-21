import webbrowser
from pysnmp.hlapi import *
import customtkinter as ctk
from concurrent.futures import ThreadPoolExecutor
from functools import *
import atexit
import time
import itertools


cache_toner = {}  # Dicionário para armazenar os dados do toner temporariamente
cache_timeout = 300  # Tempo de expiração do cache em segundos (5 minutos)

# Função para obter dados SNMP com timeout
def get_snmp_data(ip, oid):
    try:
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData('public', mpModel=0),
                   UdpTransportTarget((ip, 161), timeout=5, retries=2),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid)))
        )

        if errorIndication:
            print(f"Erro SNMP {ip}: {errorIndication}")
            return None  
        if errorStatus:
            print(f"Erro SNMP {ip}: {errorStatus.prettyPrint()}")
            return None  

        return int(varBinds[0][1])  

    except Exception as e:
        print(f"Erro ao obter SNMP de {ip}: {e}")
        return None

def get_snmp_cached(ip, oid):
    global cache_toner

    # Se o dado já está no cache e ainda é válido, retorna ele
    if (ip, oid) in cache_toner:
        valor, timestamp = cache_toner[(ip, oid)]
        if time.time() - timestamp < cache_timeout:
            return valor  # Retorna o dado sem fazer nova consulta

    # Se o dado não estiver no cache ou estiver expirado, faz a consulta SNMP
    valor = get_snmp_data(ip, oid)

    # Salva o valor no cache com um novo timestamp
    cache_toner[(ip, oid)] = (valor, time.time())

    return valor  


# OIDs de Toner para Ricoh
oids_toner_ricoh = {
    "Preto": "1.3.6.1.2.1.43.11.1.1.9.1.4",
    "Ciano": "1.3.6.1.2.1.43.11.1.1.9.1.1",
    "Magenta": "1.3.6.1.2.1.43.11.1.1.9.1.2",
    "Amarelo": "1.3.6.1.2.1.43.11.1.1.9.1.3"
}

# OIDs de Toner para impressoras monocromáticas
oid_toner_preto = "1.3.6.1.2.1.43.11.1.1.9.1.1"
oid_toner_maximo = "1.3.6.1.2.1.43.11.1.1.8.1.1"

# Impressoras
impressoras = {
    "FAT SUS": {"ip": "172.16.4.143", "colorida": False},
    "FAT CONVENIO": {"ip": "172.16.4.144", "colorida": False},
    "FINANCEIRO": {"ip": "172.16.4.145", "colorida": False},
    "DIRETORIA": {"ip": "172.16.4.213", "colorida": False},
    "ALMOXARIFADO": {"ip": "172.16.4.112", "colorida": False},
    "OPME": {"ip": "172.16.4.116", "colorida": False},
    "FARMACIA CENTRAL": {"ip": "172.16.4.114", "colorida": False},
    "SCIH": {"ip": "172.16.4.113", "colorida": False},
    "P.A NOVO POSTO ENF": {"ip": "172.16.4.139", "colorida": False},
    "P.A NOVO CONSULTORIO": {"ip": "172.16.87.112", "colorida": False},
    "P.A NOVO TRIAGEM": {"ip": "172.16.4.147", "colorida": False},
    "AQUARIO": {"ip": "172.16.4.118", "colorida": False},
    "SALA AMARELA": {"ip": "172.16.4.111", "colorida": False},
    "FARMACIA URG SUS": {"ip": "172.16.8.124", "colorida": False},
    "URG SUS POSTO ENF": {"ip": "172.16.4.106", "colorida": False},
    "RECEPCAO CONVENIO": {"ip": "172.16.4.117", "colorida": False},
    "NIR": {"ip": "172.16.4.142", "colorida": False},
    "COORD. ENFERMAGEM": {"ip": "172.16.4.97", "colorida": False},
    "SERVICO SOCIAL": {"ip": "172.16.4.88", "colorida": False},
    "RECEPCAO SUS": {"ip": "172.16.7.73", "colorida": False},
    "P.A ANTIGO": {"ip": "172.16.4.121", "colorida": False},
    "UI TERREO": {"ip": "172.16.4.146", "colorida": False},
    "UI SUBSOLO": {"ip": "172.16.4.131", "colorida": False},
    "HEMODINAMICA": {"ip": "172.16.9.12", "colorida": False},
    "RECEPCAO CDI": {"ip": "172.16.4.141", "colorida": False},
    "ENVELOPAMENTO CDI": {"ip": "172.16.8.123", "colorida": False},
    "AGENDAMENTO CDI": {"ip": "172.16.8.101", "colorida": False},
    "TOMOGRAFIA": {"ip": "172.16.8.60", "colorida": False},
    "COZINHA": {"ip": "172.16.4.108", "colorida": False},
    "MANUTENCAO": {"ip": "172.16.80.137", "colorida": False},
    "BANCO DE SANGUE": {"ip": "172.16.6.223", "colorida": False},
    "AMBULATORIO CORREDOR": {"ip": "172.16.4.107", "colorida": False},
    "AMBULATORIO RECEPCAO": {"ip": "172.16.4.125", "colorida": False},
    "FAT UTI 2": {"ip": "172.16.218.13", "colorida": False},
    "SPP": {"ip": "172.16.4.109", "colorida": False},
    "RECEPCAO ONCOLOGIA": {"ip": "172.16.4.100", "colorida": False},
    "RADIOLOGIA FISICOS": {"ip": "172.16.4.184", "colorida": False},
    "POS CONSULTA": {"ip": "172.16.60.215", "colorida": False},
    "QUIMIOTERAPIA": {"ip": "172.16.4.185", "colorida": False},
    "UI CONVENIO": {"ip": "172.16.4.188", "colorida": False},
    "CC RECEPCAO": {"ip": "172.16.4.129", "colorida": False},
    "CC CORREDOR": {"ip": "172.16.4.130", "colorida": False},
    "CC SALA RECUPERACAO": {"ip": "172.16.8.77", "colorida": False},
    "UTI 2": {"ip": "172.16.4.133", "colorida": False},
    "UTI 1": {"ip": "172.16.4.137", "colorida": False},
    "FARMACIA UTI": {"ip": "172.16.4.115", "colorida": False},
    "ENGENHARIA CLINICA": {"ip": "172.16.90.12", "colorida": False},
    "PEDIATRIA": {"ip": "172.16.4.189", "colorida": False},
    "QUALIDADE": {"ip": "172.16.4.159", "colorida": False},
    "UI 2 ANDAR": {"ip": "172.16.4.134", "colorida": False},
    "UI 3 ANDAR": {"ip": "172.16.4.135", "colorida": False},
    "SALA DE LAUDOS": {"ip": "172.16.8.213", "colorida": False},
    "RH": {"ip": "172.16.4.127", "colorida": False},
    "RH CORREDOR": {"ip": "172.16.4.128", "colorida": False},
    "CORREDOR CLINICA SCA": {"ip": "172.16.22.11", "colorida": False},
    "RECEPCAO CLINICA SCA": {"ip": "172.16.22.12", "colorida": False},
    "ORTOPEDIA": {"ip": "172.16.218.23", "colorida": False},
    "CONSULTORIO RADIOTERAPIA": {"ip": "172.16.218.24", "colorida": False},
    "ONCOLOGIA CONSULTORIO 2": {"ip": "172.16.218.25", "colorida": False},
    "ONCOLOGIA CONSULTORIO 3": {"ip": "172.16.218.26", "colorida": False},
    "ONCOLOGIA CONSULTORIO 1": {"ip": "172.16.218.27", "colorida": False},
    "ECOCARDIOGRAMA": {"ip": "172.16.218.28", "colorida": False},
    "FARMACIA URG 2": {"ip": "172.16.218.72", "colorida": False},
    "POSTO ENFERMAGEM URG 2": {"ip": "172.16.218.73", "colorida": False},
    "SALA PRESCRICAO URG 2": {"ip": "172.16.218.74", "colorida": False},
    "SALA ARIANE URG 2": {"ip": "172.16.218.120", "colorida": False},
    "FARMACIA C.C": {"ip": "172.16.218.176", "colorida": False},
    "RICOH RADIOLOGIA": {"ip": "172.16.30.88", "colorida": True},
}


# Configuração da interface
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Monitoramento de Toner")

# Obtendo a resolução da tela
largura_tela = root.winfo_screenwidth()
altura_tela = root.winfo_screenheight()

# Definir tamanho da janela para ocupar toda a tela
root.geometry(f"{largura_tela}x{altura_tela}+0+0")

# Criando um frame principal ajustável
main_frame = ctk.CTkFrame(root)
main_frame.pack(expand=True, fill="both", padx=10, pady=10)

# Criando um título
titulo = ctk.CTkLabel(main_frame, text="Monitoramento de Impressoras", font=("Arial", 18, "bold"))
titulo.pack(pady=10)

def atualizar_todas_impressoras():
    print("🔄 Iniciando atualização das impressoras...")  # Log de depuração
    for nome, dados in impressoras.items():
        executor.submit(atualizar_impressora, nome, dados)
    print("✅ Atualização enviada para todas as impressoras.")  # Confirmação
    root.after(300000, atualizar_todas_impressoras)  # Atualiza a cada 5 minutos

def limpar_cache():
    global cache_toner
    print("🧹 Limpando cache...")  # Log de depuração
    cache_toner.clear()
    print("✅ Cache limpo!")  # Confirmação
    root.after(600000, limpar_cache)  # Limpa a cada 10 minutos

# Criando um rótulo para a mensagem de status
status_label = ctk.CTkLabel(
    main_frame, 
    text="",  # Começa vazio
    font=("Arial", 12, "bold"),
    text_color="white"
)
status_label.pack(pady=5)  # Posiciona abaixo do botão

def atualizar_e_limpar_cache():
    print("🚀 Iniciando limpeza de cache e atualização...")  # Log de depuração
    limpar_cache()  # Limpa o cache primeiro
    atualizar_todas_impressoras()  # Atualiza as impressoras

    # Exibir mensagem de sucesso
    status_label.configure(text="✅ Atualização concluída!", text_color="lightgreen")

    # Remover a mensagem após 3 segundos
    root.after(3000, lambda: status_label.configure(text=""))

# Criando um botão para atualizar e limpar cache juntos
botao_atualizar_limpar = ctk.CTkButton(
    main_frame,
    text="🔄🧹 Atualizar e Limpar Cache",
    command=atualizar_e_limpar_cache,  # Chama a função combinada ao clicar
    fg_color="#32CD32",  # Verde claro
    hover_color="#228B22",  # Verde mais escuro ao passar o mouse
    font=("Arial", 14, "bold")
)
botao_atualizar_limpar.pack(pady=10)

# Criando um frame rolável para impressoras
scrollable_printer_frame = ctk.CTkScrollableFrame(main_frame)
scrollable_printer_frame.pack(expand=True, fill="both", padx=20, pady=10)

# Criando labels dinâmicos para impressoras dentro do frame rolável
labels = {}

# Definir um número de colunas adequado
num_colunas = min(6, max(2, largura_tela // 250))

def abrir_no_navegador(ip):
    url = f"http://{ip}"
    webbrowser.open(url)

def iniciar_letreiro(widget, texto_original):
    """Inicia a animação do letreiro quando o mouse entra no botão."""
    if len(texto_original) < 20:  # Só ativa para textos longos
        return  

    def animar():
        if getattr(widget, "letreiro_ativo", False):  # Só anima se ainda estiver ativo
            novo_texto = next(scroll_iter)
            widget.configure(text=novo_texto)
            widget.after(200, animar)  # Atualiza a cada 200ms

    # Cria um iterador que faz o texto rolar
    scroll_texto = f"   {texto_original}   "  # Espaços extras para suavizar
    scroll_iter = itertools.cycle([scroll_texto[i:] + scroll_texto[:i] for i in range(len(scroll_texto))])

    widget.scroll_iter = scroll_iter  # Armazena no widget para referência
    widget.letreiro_ativo = True  # Ativa o letreiro
    animar()

def parar_letreiro(widget, texto_original):
    """Para a animação e restaura o texto original."""
    widget.letreiro_ativo = False  # Desativa o letreiro
    widget.configure(text=texto_original)  # Restaura o nome original

for index, (nome, dados) in enumerate(sorted(impressoras.items())):
    row = index // num_colunas
    col = index % num_colunas

    frame = ctk.CTkFrame(scrollable_printer_frame)
    frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    texto_botao = f"{nome} ({dados['ip']})"

    botao_nome = ctk.CTkButton(
        frame, 
        text=texto_botao, 
        font=("Arial", 14, "bold"),
        command=lambda ip=dados['ip']: abrir_no_navegador(ip),
        text_color="white",
        fg_color="gray",
        corner_radius=8  
    )
    botao_nome.pack(pady=5)

    # Adicionando eventos do letreiro
    botao_nome.bind("<Enter>", lambda event, w=botao_nome, t=texto_botao: iniciar_letreiro(w, t))
    botao_nome.bind("<Leave>", lambda event, w=botao_nome, t=texto_botao: parar_letreiro(w, t))


    labels[nome] = {}
    
    if dados["colorida"]:
        for cor in ["Preto", "Ciano", "Magenta", "Amarelo"]:
            sub_frame = ctk.CTkFrame(frame)
            sub_frame.pack(pady=3, fill="x")

            # Label da cor
            labels[nome][cor] = ctk.CTkLabel(sub_frame, text=f"{cor}: ⏳", font=("Arial", 12))
            labels[nome][cor].pack(side="left", padx=5)

            # Barra de progresso para a cor
            labels[nome][f"progress_{cor}"] = ctk.CTkProgressBar(sub_frame, width=120)
            labels[nome][f"progress_{cor}"].pack(side="right", padx=5)
            labels[nome][f"progress_{cor}"].set(0.0)  # Inicializa como 0%
    else:
        sub_frame = ctk.CTkFrame(frame)
        sub_frame.pack(pady=3, fill="x")

        labels[nome]["Preto"] = ctk.CTkLabel(sub_frame, text="Preto: ⏳", font=("Arial", 12))
        labels[nome]["Preto"].pack(side="left", padx=5)

        labels[nome]["progress_Preto"] = ctk.CTkProgressBar(sub_frame, width=120)
        labels[nome]["progress_Preto"].pack(side="right", padx=5)
        labels[nome]["progress_Preto"].set(0.0)

# Ajusta colunas automaticamente para manter um layout organizado
for i in range(num_colunas):
    scrollable_printer_frame.columnconfigure(i, weight=1)

# Permite sair do modo fullscreen pressionando "Esc"
def sair_fullscreen(event):
    root.attributes('-fullscreen', False)

root.bind("<Escape>", sair_fullscreen)

# Criando um executor para threads
executor = ThreadPoolExecutor(max_workers=8)

def atualizar_impressora(nome, dados):
    ip = dados['ip']

    if dados["colorida"]:
        toners = {cor: get_snmp_cached(ip, oid) for cor, oid in oids_toner_ricoh.items()}
    
        for cor in ["Preto", "Ciano", "Magenta", "Amarelo"]:
            valor = toners.get(cor, None)

            if valor is None:
                texto, cor_fundo = f"{cor}: ❌ Erro", "#4B4B4B"
                progress = 0.0
                cor_barra = "#4B4B4B"
            else:
                progress = valor / 100  # Converte para escala de 0 a 1

                if valor <= 5:
                    texto, cor_fundo, cor_barra = f"{cor}: 🔴 {valor}%", "#8B0000", "#8B0000"
                elif valor <= 10:
                    texto, cor_fundo, cor_barra = f"{cor}: 🟠 {valor}%", "#FFA500", "#FFA500"
                else:
                    texto, cor_fundo, cor_barra = f"{cor}: 🟢 {valor}%", "#2E8B57", "#2E8B57"

            if cor in labels[nome]:
                root.after(0, lambda lbl=labels[nome][cor], txt=texto, cor_bg=cor_fundo: lbl.configure(text=txt, fg_color=cor_bg))
                root.after(0, lambda progress_bar=labels[nome][f"progress_{cor}"], value=progress: progress_bar.set(value))
                root.after(0, lambda progress_bar=labels[nome][f"progress_{cor}"], color=cor_barra: progress_bar.configure(progress_color=color))
    
    else:
        toner_atual = get_snmp_cached(ip, oid_toner_preto)
        toner_maximo = get_snmp_cached(ip, oid_toner_maximo)

        if toner_atual is None or toner_maximo is None or toner_maximo == 0:
            texto, cor_fundo = "⚫ Offline", "#4B4B4B"
            progress = 0.0
            cor_barra = "#4B4B4B"
        else:
            try:
                porcentagem = (toner_atual / toner_maximo) * 100
                progress = porcentagem / 100

                if porcentagem <= 5:
                    texto, cor_fundo, cor_barra = f"🔴 {porcentagem:.2f}%", "#8B0000", "#8B0000"
                elif porcentagem <= 10:
                    texto, cor_fundo, cor_barra = f"🟠 {porcentagem:.2f}%", "#FFA500", "#FFA500"
                else:
                    texto, cor_fundo, cor_barra = f"🟢 {porcentagem:.2f}%", "#2E8B57", "#2E8B57"
            except (ValueError, ZeroDivisionError):
                texto = "⚠️ Erro ao processar"
                cor_fundo = "#D2B200"
                progress = 0.0
                cor_barra = "#4B4B4B"

        if "Preto" in labels[nome]:
            root.after(0, lambda lbl=labels[nome]["Preto"], txt=texto, cor_bg=cor_fundo: lbl.configure(text=txt, fg_color=cor_bg))
            root.after(0, lambda progress_bar=labels[nome]["progress_Preto"], value=progress: progress_bar.set(value))
            root.after(0, lambda progress_bar=labels[nome]["progress_Preto"], color=cor_barra: progress_bar.configure(progress_color=color))

atexit.register(executor.shutdown)
atualizar_todas_impressoras()
limpar_cache()  # Inicia o ciclo de limpeza automática
root.mainloop()