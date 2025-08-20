
from flask import Flask, render_template, request, jsonify
import socket
from datetime import datetime

app = Flask(__name__)

def scan_port(target, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)  # Further reduced timeout to 0.3 seconds
        result = sock.connect_ex((target, port))
        sock.close()
        return port, result == 0
    except socket.gaierror as e:
        print(f"Gaierror on port {port}: {e}")  # Log hostname resolution errors
        return port, "Error: Hostname could not be resolved."
    except socket.error as e:
        print(f"Socket error on port {port}: {e}")  # Log socket-specific errors
        return port, False
    except Exception as e:
        print(f"Unexpected error on port {port}: {e}")  # Catch any other errors
        return port, False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    target = request.form.get('target', '')
    print(f"Received target: {target}")  # Debug log
    try:
        start_port = int(request.form.get('start_port', '0'))
        end_port = int(request.form.get('end_port', '0'))
        print(f"Received ports: {start_port} to {end_port}")  # Debug log
    except ValueError:
        return jsonify({'error': 'Ports must be integers.'})

    # Limit port range to 50 for testing to avoid hangs
    max_ports = 50
    if end_port - start_port > max_ports:
        end_port = start_port + max_ports - 1
        print(f"Limited port range to {start_port} to {end_port}")

    if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535):
        return jsonify({'error': 'Ports must be between 1 and 65535.'})
    if start_port > end_port:
        return jsonify({'error': 'Start port must be less than or equal to end port.'})

    results = []
    open_ports = []
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        for port in range(start_port, end_port + 1):
            port, is_open = scan_port(target, port)
            if isinstance(is_open, str):
                return jsonify({'error': is_open})
            status = 'OPEN' if is_open else 'CLOSED'
            if is_open:
                open_ports.append(port)
            results.append(f"Port {port}: {status}")
    except Exception as e:
        print(f"Loop error: {e}")  # Catch loop-related errors
        return jsonify({'error': f"Scan failed: {e}"})

    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    summary = f"Open ports: {', '.join(map(str, open_ports))}" if open_ports else "No open ports found."
    print(f"Scan completed: {summary}")  # Debug log
    return jsonify({
        'results': results,
        'summary': summary,
        'start_time': start_time,
        'end_time': end_time
    })

if __name__ == '__main__':
    app.run(debug=True)
