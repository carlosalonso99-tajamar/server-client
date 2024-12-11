import socket
import json
import logging
import os
import time
from azure.eventhub import EventHubProducerClient, EventData
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from dotenv import load_dotenv

# Cargar variables desde el archivo .env
load_dotenv()

# Variables de entorno
EVENT_HUB_CONNECTION_STRING = os.getenv("EVENT_HUB_CONNECTION_STRING")
EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME")
RESOURCE_GROUP = os.getenv("RESOURCE_GROUP")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
SUBSCRIPTION_ID = os.getenv("SUBSCRIPTION_ID")

# Configuración del servidor socket
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info(HOST)
    logging.info("Starting continuous socket client in ACI...")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            logging.info(f"Connected to server at {HOST}:{PORT}")

            logging.info(client_socket)
            while True:
                # Enviar el comando "NEXT"
                command = "NEXT"
                client_socket.sendall(command.encode('utf-8'))

                # Recibir respuesta
                data = client_socket.recv(1024)
                logging.info(f"Data: {data}")
                response = json.loads(data.decode('utf-8'))
                logging.info(f"Response from server: {response}")

                # Verificar si el servidor respondió con un error
                if isinstance(response, dict) and response.get("status") == 400:
                    logging.error("Server responded with status 400. Shutting down container.")
                    stop_container()
                    break

                # Enviar datos al Event Hub
                send_to_event_hub(response)

                # Evitar sobrecargar el servidor
                time.sleep(1)

    except Exception as e:
        logging.error(f"Error in continuous socket client: {e}")


def send_to_event_hub(data: dict):
    """
    Enviar datos al Event Hub.
    """
    try:
        producer = EventHubProducerClient.from_connection_string(
            conn_str=EVENT_HUB_CONNECTION_STRING,
            eventhub_name=EVENT_HUB_NAME
        )
        with producer:
            partition_key = str(data.get('car_id'))  # Usar el user_id como partitionKey
            # Crear un lote de eventos
            event_data_batch = producer.create_batch(partition_key=partition_key)
            # Añadir el evento (convertir a cadena JSON)
            event_data_batch.add(EventData(json.dumps(data)))

            # Enviar el lote con el partition_key
            producer.send_batch(event_data_batch)
            logging.info("Data sent to Event Hub successfully.")
    except Exception as e:
        logging.error(f"Error sending data to Event Hub: {e}")


def stop_container():
    """
    Detener el contenedor de Azure Container Instances.
    """
    try:
        # Autenticación con Azure
        credential = DefaultAzureCredential()
        client = ContainerInstanceManagementClient(credential, SUBSCRIPTION_ID)

        # Detener el contenedor
        client.containers.stop(resource_group_name=RESOURCE_GROUP, container_group_name=CONTAINER_NAME)
        logging.info(f"Container {CONTAINER_NAME} stopped successfully.")
    except Exception as e:
        logging.error(f"Error stopping container: {e}")

if __name__ == "__main__":
    main()
