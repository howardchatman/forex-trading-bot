"""
TradingView webhook receiver for processing trading signals.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any, Optional, Callable
import logging
import hashlib
import hmac

logger = logging.getLogger(__name__)


class TradingViewWebhook:
    """Webhook server for receiving TradingView alerts."""

    def __init__(
        self,
        port: int = 5000,
        webhook_secret: Optional[str] = None,
        allowed_ips: Optional[list] = None
    ):
        """
        Initialize webhook server.

        Args:
            port: Port to run webhook server on
            webhook_secret: Secret key for validating webhooks
            allowed_ips: List of allowed IP addresses (None = allow all)
        """
        self.port = port
        self.webhook_secret = webhook_secret
        self.allowed_ips = allowed_ips or []
        self.signal_handler: Optional[Callable] = None

        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)

        # Register routes
        self._register_routes()

        logger.info(f"TradingView webhook initialized on port {port}")

    def _register_routes(self):
        """Register Flask routes."""

        @self.app.route('/webhook', methods=['POST'])
        def webhook():
            """Handle incoming webhook requests."""
            try:
                # Check IP whitelist
                if self.allowed_ips and request.remote_addr not in self.allowed_ips:
                    logger.warning(f"Rejected webhook from {request.remote_addr}")
                    return jsonify({'error': 'Unauthorized IP'}), 403

                # Get webhook data
                data = request.get_json()

                if not data:
                    return jsonify({'error': 'No data provided'}), 400

                # Validate webhook signature if secret is set
                if self.webhook_secret:
                    if not self._validate_signature(data):
                        logger.warning("Invalid webhook signature")
                        return jsonify({'error': 'Invalid signature'}), 401

                # Process the signal
                logger.info(f"Received webhook: {data}")
                result = self._process_signal(data)

                return jsonify({'status': 'success', 'result': result}), 200

            except Exception as e:
                logger.error(f"Error processing webhook: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({'status': 'healthy'}), 200

    def _validate_signature(self, data: Dict[str, Any]) -> bool:
        """
        Validate webhook signature.

        Args:
            data: Webhook data

        Returns:
            True if signature is valid
        """
        if not self.webhook_secret:
            return True

        signature = data.get('signature')
        if not signature:
            return False

        # Create expected signature
        payload = str(data.get('timestamp', '')) + str(data.get('action', ''))
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def _process_signal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process trading signal from TradingView.

        Expected data format:
        {
            "action": "buy" or "sell" or "close",
            "instrument": "EUR_USD",
            "price": 1.0850,
            "sl": 1.0830,  # optional
            "tp": 1.0900,  # optional
            "quantity": 1000,  # optional
            "strategy": "trend_following",  # optional
            "timestamp": 1234567890,
            "signature": "..."  # optional for validation
        }

        Args:
            data: Signal data from TradingView

        Returns:
            Processing result
        """
        # Validate required fields
        required_fields = ['action', 'instrument']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Normalize the signal
        signal = {
            'action': data['action'].lower(),
            'instrument': data['instrument'].replace('/', '_'),  # Convert EUR/USD to EUR_USD
            'price': data.get('price'),
            'stop_loss': data.get('sl') or data.get('stop_loss'),
            'take_profit': data.get('tp') or data.get('take_profit'),
            'quantity': data.get('quantity'),
            'strategy': data.get('strategy', 'unknown'),
            'timestamp': data.get('timestamp'),
            'metadata': {
                'source': 'tradingview',
                'raw_data': data
            }
        }

        # Call the signal handler if registered
        if self.signal_handler:
            try:
                result = self.signal_handler(signal)
                return result
            except Exception as e:
                logger.error(f"Error in signal handler: {e}")
                raise
        else:
            logger.warning("No signal handler registered")
            return {'status': 'no_handler', 'signal': signal}

    def register_signal_handler(self, handler: Callable):
        """
        Register a callback function to handle trading signals.

        Args:
            handler: Callback function that takes a signal dict as argument
        """
        self.signal_handler = handler
        logger.info("Signal handler registered")

    def run(self, debug: bool = False):
        """
        Start the webhook server.

        Args:
            debug: Enable Flask debug mode
        """
        logger.info(f"Starting webhook server on port {self.port}")
        self.app.run(host='0.0.0.0', port=self.port, debug=debug)

    def run_async(self):
        """Run webhook server in a separate thread."""
        from threading import Thread
        thread = Thread(target=self.run, daemon=True)
        thread.start()
        logger.info("Webhook server started in background thread")


def create_tradingview_alert_template() -> str:
    """
    Generate a template for TradingView alert messages.

    Returns:
        JSON template string for TradingView alerts
    """
    template = '''{
    "action": "{{strategy.order.action}}",
    "instrument": "{{ticker}}",
    "price": {{close}},
    "sl": {{strategy.order.stop_loss}},
    "tp": {{strategy.order.take_profit}},
    "quantity": {{strategy.order.contracts}},
    "strategy": "My Strategy Name",
    "timestamp": {{timenow}},
    "signature": "your_signature_here"
}'''
    return template


# Example usage
if __name__ == '__main__':
    # Example signal handler
    def handle_signal(signal: Dict[str, Any]) -> Dict[str, Any]:
        """Example signal handler."""
        print(f"Received signal: {signal}")
        return {'processed': True}

    # Create and run webhook
    webhook = TradingViewWebhook(port=5000)
    webhook.register_signal_handler(handle_signal)
    webhook.run(debug=True)
