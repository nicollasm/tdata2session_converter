import sys
import asyncio
import argparse
import logging
import os
from opentele.td import TDesktop
from opentele.api import UseCurrentSession
from pathlib import Path

# Configurar o loop de eventos para evitar problemas no Windows com asyncio e ProactorEventLoop
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Configurar o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def load_tdesktop_client(tdata_folder):
    """
    Carrega o cliente TDesktop a partir da pasta tdata e tenta diferentes métodos de carregamento com base na estrutura detectada.
    :param tdata_folder: Caminho para a pasta tdata.
    :return: Cliente TDesktop carregado ou None se falhar.
    """
    try:
        logging.info(f"Carregando o cliente TDesktop da pasta: {tdata_folder}")

        # Tentar carregar o cliente TDesktop da forma padrão
        try:
            tdesk = TDesktop(tdata_folder)
            assert tdesk.isLoaded(), "Nenhuma conta carregada. Verifique a pasta tdata."
            logging.info(f"Cliente TDesktop carregado com sucesso. Contas carregadas: {len(tdesk.accounts)}")
            return tdesk
        except AssertionError as e:
            logging.warning(f"Falha ao carregar usando o método padrão: {e}")

        # Tentativa de método alternativo de carregamento
        try:
            # Inserir aqui outra tentativa de carregamento caso disponível (exemplo fictício)
            tdesk = TDesktop(tdata_folder, forceLegacy=True)  # Apenas um exemplo
            if tdesk.isLoaded():
                logging.info(
                    f"Cliente TDesktop carregado usando método alternativo. Contas carregadas: {len(tdesk.accounts)}")
                return tdesk
        except Exception as e:
            logging.warning(f"Falha ao carregar usando o método alternativo: {e}")

        # Adicionar mais tentativas se houver outros métodos conhecidos para diferentes versões

        logging.error("Nenhum método conseguiu carregar o cliente TDesktop. Verifique a compatibilidade do tdata.")
        return None
    except Exception as e:
        logging.error(f"Erro ao carregar o cliente TDesktop: {e}", exc_info=True)
        return None


# Funções adicionais permanecem as mesmas...

async def convert_to_telethon_session(tdesk, session_file):
    """
    Converte a sessão do TDesktop para uma sessão Telethon usando a sessão atual.
    :param tdesk: Cliente TDesktop carregado.
    :param session_file: Caminho para salvar o arquivo de sessão do Telethon.
    :return: Cliente Telethon inicializado.
    """
    try:
        logging.info("Convertendo TDesktop para Telethon usando a sessão atual...")

        # Converte TDesktop para Telethon usando a sessão atual com a API Key original
        client = await tdesk.ToTelethon(
            session=session_file,
            flag=UseCurrentSession
        )

        await client.connect()
        logging.info("Sessão Telethon criada e conectada com sucesso.")

        # Imprime informações sobre a sessão
        me = await client.get_me()
        logging.info(f"Usuário conectado: {me.first_name} ({me.id})")

        # Verifica se o arquivo de sessão foi salvo corretamente
        if not os.path.exists(session_file):
            logging.error(f"Falha ao salvar o arquivo de sessão: {session_file}")
            return None

        logging.info(f"Arquivo de sessão salvo com sucesso: {session_file}")
        return client
    except Exception as e:
        logging.error(f"Erro ao converter para sessão Telethon: {e}", exc_info=True)
        return None


def ensure_output_directory():
    """
    Garante que o diretório 'output' exista. Se não existir, ele será criado.
    """
    output_dir = os.path.join(os.getcwd(), 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Pasta 'output' criada em: {output_dir}")
    return output_dir


def check_duplicate_session(session_path):
    """
    Verifica se já existe um arquivo de sessão com o mesmo nome.
    :param session_path: Caminho do arquivo de sessão.
    :return: Verdadeiro se o arquivo já existir, caso contrário Falso.
    """
    if os.path.exists(session_path):
        logging.warning(f"Arquivo de sessão já existe: {session_path}")
        return True
    return False


async def main():
    parser = argparse.ArgumentParser(description='Converter sessão do TDesktop para sessão do Telethon.')
    parser.add_argument('phone_number_directory', help='Diretório contendo o número de telefone e o tdata.')
    args = parser.parse_args()

    # Define o caminho do tdata e o arquivo de sessão com base no diretório do número de telefone
    tdata_folder = os.path.join(args.phone_number_directory, "tdata")
    phone_number = os.path.basename(args.phone_number_directory)

    # Garante que o diretório de saída exista
    output_dir = ensure_output_directory()
    session_file = os.path.join(output_dir, f"{phone_number}.session")

    # Verifica se o diretório tdata existe
    if not os.path.exists(tdata_folder):
        logging.error(f"Diretório tdata não encontrado: {tdata_folder}")
        return

    # Verifica se o arquivo de sessão já existe
    if check_duplicate_session(session_file):
        logging.info(f"Arquivo de sessão '{session_file}' já existe. Por favor, verifique e remova se necessário.")
        return

    # Carrega o cliente TDesktop
    tdesk = await load_tdesktop_client(tdata_folder)
    if tdesk is None:
        logging.error("Falha ao carregar o cliente TDesktop. Verifique a pasta tdata e tente novamente.")
        return

    # Converte para sessão Telethon usando a sessão atual
    client = await convert_to_telethon_session(tdesk, session_file)
    if client is None:
        logging.error("Falha ao converter para sessão Telethon.")
        return

    # Opcional: desconectar o cliente Telethon
    await client.disconnect()
    logging.info("Processo concluído com sucesso.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Erro fatal: {e}", exc_info=True)
