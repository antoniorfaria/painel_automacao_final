# -*- coding: utf-8 -*-
# server.py - Servidor Backend para o Painel de Automação Residencial

# Importa os módulos necessários
from http.server import BaseHTTPRequestHandler, HTTPServer # Para criar o servidor HTTP
import os # Para lidar com caminhos de arquivos

# --- Variável Global de Estado do Relé ---
# Esta variável simula o estado de um relé físico (ligado ou desligado).
# 'False' significa desligado, 'True' significa ligado.
relay_state = False

# --- Classe para Lidar com Requisições HTTP ---
# BaseHTTPRequestHandler é a classe base para lidar com requisições HTTP.
class RequestHandler(BaseHTTPRequestHandler):

    # --- Método do_GET: Lida com Requisições GET ---
    # Este método é chamado toda vez que o navegador faz uma requisição GET (ex: ao carregar uma página ou clicar em um link).
    def do_GET(self):
        global relay_state # Permite que este método altere a variável global 'relay_state'.

        # Pega o caminho da URL (ex: "/RELE/ON", "/", "/style.css").
        # O .split('?')[0] remove quaisquer parâmetros de consulta (ex: "?v=123").
        path = self.path.split('?')[0]

        # --- Tratamento de Arquivos Estáticos (CSS) ---
        # Se a requisição for para o arquivo CSS, lê e envia o conteúdo CSS.
        if path == "/style.css":
            try:
                # Constrói o caminho completo para o arquivo style.css.
                # os.path.dirname(__file__) obtém o diretório do script Python atual.
                css_file_path = os.path.join(os.path.dirname(__file__), 'style.css')

                # Abre e lê o conteúdo do arquivo CSS com codificação UTF-8.
                with open(css_file_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()

                # Envia o status HTTP 200 (OK) ao navegador.
                self.send_response(200)
                # Informa ao navegador que o conteúdo é CSS e usa UTF-8.
                self.send_header("Content-type", "text/css; charset=utf-8")
                # Adiciona cabeçalhos para instruir o navegador a não armazenar o CSS em cache.
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.send_header("Pragma", "no-cache")
                self.send_header("Expires", "0")
                self.send_header("Connection", "close") # Fecha a conexão após enviar a resposta.
                self.end_headers() # Finaliza o envio dos cabeçalhos HTTP.

                # Escreve o conteúdo CSS (codificado em UTF-8) para o corpo da resposta.
                self.wfile.write(css_content.encode('utf-8'))
                return # Termina a execução do método aqui, pois o CSS foi servido.

            except FileNotFoundError:
                # Se style.css não for encontrado, envia um erro 404.
                self.send_error(404, "Arquivo CSS não encontrado.")
                print(f"ERRO: style.css não encontrado em {css_file_path}. Verifique se o arquivo existe na mesma pasta do server.py.")
                return
            except Exception as e:
                # Lida com outros erros que possam ocorrer ao ler o CSS.
                self.send_error(500, f"Erro ao ler style.css: {e}")
                print(f"ERRO: Falha ao ler style.css: {e}")
                return

        # --- Lógica de Controle do Relé e Mensagens ---
        # Inicializa a mensagem que será exibida na página.
        display_message = "Bem-vindo ao Painel de Automação!"

        if path == "/RELE/ON":
            # Se a requisição for para ligar o relé, muda o estado e a mensagem.
            relay_state = True
            display_message = "Relé Ligado com sucesso!"
        elif path == "/RELE/OFF":
            # Se a requisição for para desligar o relé, muda o estado e a mensagem.
            relay_state = False
            display_message = "Relé Desligado com sucesso!"
        elif path == "/" or path == "/index.html":
            # Se a requisição for a página inicial, mantém a mensagem padrão ou a última de status.
            pass
        else:
            # Para qualquer outra URL não reconhecida, envia um erro 404.
            display_message = "Página não encontrada ou comando inválido."
            self.send_error(404, display_message)
            return

        # --- Leitura do Arquivo HTML ---
        html_content = ""
        try:
            # Constrói o caminho completo para o arquivo index.html.
            html_file_path = os.path.join(os.path.dirname(__file__), 'index.html')

            # Abre e lê o conteúdo do arquivo HTML com codificação UTF-8.
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except FileNotFoundError:
            # Se index.html não for encontrado, envia um erro 500.
            self.send_error(500, f"Erro Interno: O arquivo HTML '{html_file_path}' não foi encontrado.")
            print(f"ERRO: index.html não encontrado em {html_file_path}. Verifique a pasta.")
            return
        except Exception as e:
            # Lida com outros erros que possam ocorrer ao ler o HTML.
            self.send_error(500, f"Erro Interno ao ler index.html: {e}")
            print(f"ERRO: Falha ao ler index.html: {e}")
            return

        # --- Preparação dos Dados para o HTML ---
        # Define o texto do status e a classe CSS com base no estado atual do relé.
        relay_status_text = 'Ligado' if relay_state else 'Desligado'
        status_css_class = 'status-on' if relay_state else 'status-off'

        # --- Renderização do HTML (Substituição de Placeholders) ---
        try:
            # Usa o método .format() para inserir os dados dinâmicos no HTML.
            # Removido o placeholder 'timestamp' para evitar o erro.
            rendered_html = html_content.format(
                message=display_message,
                relay_status_text=relay_status_text,
                status_class=status_css_class
            )
        except KeyError as e:
            # Captura erros se um placeholder no HTML não for fornecido no .format().
            self.send_error(500, f"Erro no template HTML: Placeholder '{e}' faltando ou mal formatado.")
            print(f"ERRO: Placeholder '{e}' faltando ou mal formatado no index.html. Verifique se há algum '{'{'}placeholder{'}'}' não mapeado.")
            return
        except Exception as e:
            # Captura outros erros inesperados durante a formatação.
            self.send_error(500, f"Erro inesperado ao renderizar HTML: {e}")
            print(f"ERRO: Falha na renderização do HTML: {e}")
            return

        # --- Envio da Resposta HTTP ao Navegador ---
        self.send_response(200) # Status HTTP 200 (OK).
        self.send_header("Content-type", "text/html; charset=utf-8") # Tipo de conteúdo e codificação.
        # Adiciona cabeçalhos para instruir o navegador a não armazenar o HTML em cache.
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Connection", "close")
        self.end_headers() # Finaliza os cabeçalhos.

        # Envia o conteúdo HTML renderizado (convertido para bytes UTF-8) ao navegador.
        self.wfile.write(rendered_html.encode('utf-8'))

        # --- Log no Console do Servidor ---
        # Imprime informações da requisição no console do servidor para depuração.
        print(f"Requisição: {self.client_address[0]}:{self.client_address[1]} -> {self.path} | Relé: {relay_status_text}")

    # --- log_message: Desativa Logs Padrão do Servidor ---
    # Sobrescreve o método padrão para evitar logs excessivos no console.
    def log_message(self, format, *args):
        return

# --- Função Principal para Iniciar o Servidor ---
def run_server():
    # Porta 80 para permitir acesso via neto.dev sem ':8080'
    server_address = ('', 80)  # O servidor escutará em todas as interfaces de rede na porta 80.
    httpd = HTTPServer(server_address, RequestHandler) # Cria a instância do servidor HTTP.

    print("\n" + "="*50)
    print("Servidor HTTP do Painel de Automação Iniciado!")
    print(f"Acesse no seu navegador: http://neto.dev") # Sugere o novo endereço
    print(f"Para LIGAR o relé: http://neto.dev/RELE/ON")
    print(f"Para DESLIGAR o relé: http://neto.dev/RELE/OFF")
    print("Pressione Ctrl+C no terminal para parar o servidor.")
    print("="*50 + "\n")

    try:
        httpd.serve_forever() # Mantém o servidor rodando indefinidamente até ser interrompido.
    except KeyboardInterrupt:
        # Permite parar o servidor com a combinação de teclas Ctrl+C.
        print("\nServidor parado manualmente.")
        httpd.server_close() # Fecha a conexão do servidor.

# --- Ponto de Entrada do Script ---
# Garante que a função run_server() seja chamada apenas quando o script for executado diretamente.
if __name__ == '__main__':
    run_server()