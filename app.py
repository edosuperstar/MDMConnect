import threading
from queue import Queue, Empty
from flask import Flask, render_template, request, jsonify
from Mdmconnect import MdmConnect

# Configurazione MDM
HOST = "10.232.10.6"  # Indirizzo IP del dispositivo MDM
PORT = 8234          # Porta di comunicazione con il dispositivo MDM

# Inizializzazione dell'app Flask
app = Flask(__name__)

# Connessione al dispositivo MDM tramite la classe MdmConnect
mdm = MdmConnect(HOST, PORT)

# Coda dei comandi per gestire le richieste in modo asincrono
command_queue = Queue()

# Lock per sincronizzare l'accesso ai comandi
lock = threading.Lock()

# Dizionario per gestire il throttling dei comandi, evitando richieste eccessive
last_command_time = {}

# Funzione per processare i comandi nella coda
def process_commands():
    """
    Processa i comandi presenti nella coda in ordine FIFO.
    Utilizza un lock per prevenire condizioni di race durante l'esecuzione.
    """
    while True:
        try:
            # Preleva un comando dalla coda, con timeout per evitare blocchi infiniti
            command = command_queue.get(timeout=1)
            with lock:  # Blocco sincronizzato
                command()  # Esegue il comando
            command_queue.task_done()  # Segnala che il comando è stato completato
        except Empty:
            # Nessun comando nella coda, riprendi il ciclo
            continue

# Avvia un thread separato per processare i comandi della coda
threading.Thread(target=process_commands, daemon=True).start()

@app.route('/')
def index():
    """
    Endpoint per la pagina principale.
    Recupera i guadagni e lo stato di mute dei fader e li passa al template HTML.
    """
    gains = [mdm.getGainOfInputFader(i) for i in range(1, 5)]
    mute_status = [mdm.getMuteStatusOfInputChannel(i) for i in range(1, 5)]
    return render_template('index.html', gains=gains, mute_status=mute_status)

@app.route('/update_volume', methods=['POST'])
def update_volume():
    """
    Endpoint per aggiornare il volume di un fader.
    Riceve i dati in formato JSON e mette il comando nella coda per essere processato.
    """
    data = request.json
    fader_id = data.get('fader_id') + 1  # Mappa l'indice locale (0-based) al range 1-16
    volume = float(data.get('volume'))

    # Definizione del comando per aggiornare il volume
    def set_volume():
        try:
            mdm.setGainOfInputFader(volume, fader_id)
        except Exception as e:
            print(f"Errore nell'aggiornare il volume del fader {fader_id}: {e}")

    # Aggiunge il comando alla coda
    command_queue.put(set_volume)
    return jsonify({'status': 'success', 'message': f'Volume aggiornato per fader {fader_id}'})

@app.route('/mute', methods=['POST'])
def mute():
    """
    Endpoint per attivare/disattivare il mute di un fader.
    Riceve i dati in formato JSON e aggiorna lo stato del mute.
    """
    data = request.json
    fader_id = data.get('fader_id') + 1  # Mappa l'indice locale (0-based) al range 1-16
    try:
        # Ottieni lo stato attuale di mute e inverti
        current_status = mdm.getMuteStatusOfInputChannel(fader_id)
        new_status = not current_status
        mdm.setMuteOfInputChannel(fader_id, new_status)
        return jsonify({'status': 'success', 'message': f'Mute toggled for fader {fader_id}', 'new_status': new_status})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# Punto di ingresso dell'applicazione
if __name__ == '__main__':
    app.config['DEBUG'] = False  # Disabilita il debug
    app.config['ENV'] = 'production'  # Imposta l'ambiente di produzione
    app.run(debug=False, host='0.0.0.0', port=5000)
    #app.run(debug=True, host='0.0.0.0', port=5000)