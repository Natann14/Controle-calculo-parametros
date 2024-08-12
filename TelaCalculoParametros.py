import flet as ft
#import CalcularParametros
import matplotlib
import matplotlib.pyplot as plt
from flet.matplotlib_chart import MatplotlibChart


def calcular_parametros(tempo_amostragem, degrau, caminho_txt):

    assentamento = None
    tempo_amostragem = float(tempo_amostragem)
    degrau = float(degrau)
    
    with open(rf"{caminho_txt}", "r") as arquivo:
        saida = [float(linha.strip()) for linha in arquivo.readlines()]

    entrada = [round(tempo_amostragem * i, 4) for i in range(1, len(saida)+1)]

    # Criando relação entre as duas listas
    comparacao = list(zip(entrada, saida))
    
    # Verificando se o sistema é subamortecido ou sobreamortecido
    # supondo um degrau/setpoint de 1000
    # degrau = 1000
    pico = max(saida)
    if pico > degrau:
        tempo_pico = comparacao[saida.index(pico)][0]
        #erro_est = abs((saida[-1::][0])-degrau)/degrau
        erro_est = abs((max(saida[-20:]))-degrau)/degrau
        overshoot = (pico/degrau) - 1

        # Calculo do Ts
        percent = degrau * 0.02
        margem_sup = degrau + percent
        margem_inf = degrau - percent


        for i in range(len(saida) - 18):
            if all(valor>=margem_inf and valor<=margem_sup for valor in saida[i:i+19]):
                assentamento = saida[i:i+19]
                break
        # Tempo de assentamento
        if assentamento == None:
            ts = "Não assenta em 2%"
        else:
            ts = entrada[saida.index(assentamento[0])]
        
        
        resposta = """
                        Sistema Subamortecido\n
                        Valor Maximo: {}
                       Tempo de pico: {}
                   Erro Estacionario: {} %
                             Overshoot: {} %
       Tempo de assentamento: {}
                   """.format(pico, tempo_pico, round(erro_est, 4)*100, round(overshoot, 4)*100, ts)

 
    else:
        overshoot = 0
        tempo_pico = comparacao[saida.index(pico)][0]
        erro_est = abs((max(saida[-20:]))-degrau)/degrau
        
        resposta = """      
                Sistema Sobreamortecido\n
                    Tempo de pico: {}
                 Erro Estacionario: {} %
                           Overshoot: 0 %
                   """.format(tempo_pico, round(erro_est, 4)*100)
                   
                   
    return resposta


def obter_array(tempo_amostragem, caminho_txt):
    
    tempo_amostragem = float(tempo_amostragem)
    
    with open(rf"{caminho_txt}", "r") as arquivo:
        saida = [float(linha.strip()) for linha in arquivo.readlines()]

    entrada = [round(tempo_amostragem * i, 4) for i in range(1, len(saida)+1)]

    return entrada, saida




matplotlib.use("svg")

# Variável para armazenar a referência ao gráfico anterior
grafico_anterior = None

def main(page: ft.Page):
    page.title = "Transient Response Parameters  (By: Silas Souza)"
    page.window_width = 450
    page.window_height = 790
    page.window_maximizable = False
    page.window_resizable = False

    def pick_files_result(e: ft.FilePickerResultEvent):
        selected_files.value = (
           ", ".join(map(lambda f: f.path, e.files)) if e.files else "Nenhum arquivo selecionado!"
        )
        
        # nome_arquivo.value = (
        #    ", ".join(map(lambda f: f.name, e.files)) if e.files else "Nenhum arquivo selecionado!"
        # )
        
        page.update()

    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    selected_files = ft.Text()
    
    
    page.overlay.append(pick_files_dialog)
    
    botao_pesquisar = ft.ElevatedButton("Escolher Arquivo", icon=ft.icons.UPLOAD_FILE, on_click=lambda _: pick_files_dialog.pick_files(
                        allow_multiple=False,
                        allowed_extensions=["txt"]
                        ),
                        )
    
    def button_clicked(e):
        global grafico_anterior
        if grafico_anterior:
            page.remove(grafico_anterior)
            
        try:
            resposta_planta.value = calcular_parametros(label1.value, label2.value, selected_files.value)
        except:
            pass
        
        try:
            arrays = obter_array(label1.value, selected_files.value)
            
            tempo = arrays[0]
            saida = arrays[1]
            
            fig, ax = plt.subplots()
            ax.plot(tempo, saida)

            ax.set_ylabel("Saída")
            ax.set_xlabel("Tempo de Amostragem")
            ax.set_title("Resultados")
            ax.grid()
            
            grafico = ft.ResponsiveRow([MatplotlibChart(fig, isolated=True, original_size=10)], alignment=ft.MainAxisAlignment.START)
            
            page.add(grafico)
            
            grafico_anterior = grafico

            page.update()
        
        except:
            pass
            
                
    resposta_planta = ft.Text()
    label1 = ft.TextField(label="Tempo de Amostragem (segundos)", border_color='white', width=250, height=60, max_length=8)
    label2 = ft.TextField(label="Valor do Setpoint", border_color='white', width=250, height=60, max_length=8)
    botao_start = ft.ElevatedButton(text="Iniciar", on_click=button_clicked)
    
    page.add(
        ft.ResponsiveRow([label1, label2]),
        ft.ResponsiveRow([botao_pesquisar, botao_start], alignment=ft.MainAxisAlignment.START),
        ft.ResponsiveRow([resposta_planta], alignment=ft.MainAxisAlignment.CENTER),
    )

ft.app(target=main)