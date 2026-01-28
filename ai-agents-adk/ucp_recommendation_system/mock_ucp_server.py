# mock_ucp_server.py
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/.well-known/ucp.json')
def capabilities():
    return jsonify({
        "capabilities": ["Checkout", "Catalog"],
        "protocol_version": "1.0"
    })

@app.route('/ucp/catalog/search', methods=['POST'])
def search():
    return jsonify({
        "products": [
            {
                "id": "P001",
                "name": "Test Product",
                "price": {"amount": 29.99, "currency": "USD"}
            }
        ]
    })

if __name__ == '__main__':
    app.run(port=8080)