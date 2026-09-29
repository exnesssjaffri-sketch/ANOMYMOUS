from error_classifier import ErrorClassifier
from transport import MockTransport
from llmapi_router import LLMAPIRouter, ProviderRoute

class AllModelsLimitedTransport(MockTransport):
    def send_request(self, payload, timeout):
        raise Exception('HTTP Error 429: {"error": {"type": "all_models_rate_limited", "message": "All models rate limited"}}')

# Test error classification
error = Exception('HTTP Error 429: {"error": {"type": "all_models_rate_limited", "message": "All models rate limited"}}')
print('Error classification:', ErrorClassifier.classify_exception(error))
print('Should failover:', ErrorClassifier.should_failover(ErrorClassifier.ALL_MODELS_RATE_LIMITED))

# Test router behavior
transport1 = AllModelsLimitedTransport()
transport2 = MockTransport()
route1 = ProviderRoute('groq', 'llama-3.1-70b', transport1, weight=10.0)
route2 = ProviderRoute('cerebras', 'llama-3.1-8b', transport2, weight=1.0)
router = LLMAPIRouter([route1, route2])

result = router.send_request('Short task')
print('Result status:', result['status'])
print('Router attempt:', result.get('router_attempt'))
print('Error type:', result.get('error_type'))
print('Error:', result.get('error'))