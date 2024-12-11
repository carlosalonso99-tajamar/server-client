import json
import socket
import threading
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Cargar los datos desde el archivo JSON
def load_car_data():
    try:
        with open('data.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error("data.json not found. Make sure the file is in the correct location.")
        return []
    except json.JSONDecodeError:
        logging.error("Error decoding data.json. Ensure it is a valid JSON file.")
        return []

car_data = load_car_data()

# Configuración del servidor
HOST = '127.0.0.1'  # Dirección IP del servidor
PORT = 65432        # Puerto en el que escuchará el servidor

def handle_client(conn, addr):
    """Gestiona la conexión de un cliente."""
    logging.info(f"Conexión establecida con {addr}")
    
    try:
        # Índice del cliente para simular el "streaming" de datos
        client_index = 0
        
        while True:
            # Recibir el mensaje del cliente
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            
            # Interpreta el mensaje del cliente (por simplicidad, esperamos "NEXT")
            if data.strip().upper() == "NEXT":
                if client_index >= len(car_data):
                    response = {"message": "No more data available"}
                else:
                    response = car_data[client_index]
                    client_index += 1
            else:
                response = {"message": "Invalid command. Use 'NEXT'."}
            
            # Enviar la respuesta al cliente
            conn.sendall(json.dumps(response).encode('utf-8'))
    except Exception as e:
        logging.error(f"Error gestionando el cliente {addr}: {e}")
    finally:
        conn.close()
        logging.info(f"Conexión cerrada con {addr}")

def start_server():
    """Inicia el servidor."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        logging.info(f"Servidor escuchando en {HOST}:{PORT}")
        logging.info(car_data)
        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            logging.info(f"Conexiones activas: {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()
