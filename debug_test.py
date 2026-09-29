from error_classifier import ErrorClassifier
from transport import MockTransport
from llmapi_router import LLMAPIRouter, ProviderRoute

class QuotaTransport(MockTransport):
    def send_request(self, payload, timeout):
        raise Exception('HTTP Error 413: {"error": {"type": "daily_quota_exhausted", "message": "Daily quota exhausted"}}')

# Test error classification
error = Exception('HTTP Error 413: {"error": {"type": "daily_quota_exhausted", "message": "Daily quota exhausted"}}')
print('Error classification:', ErrorClassifier.classify_exception(error))
print('Should failover:', ErrorClassifier.should_failover(ErrorClassifier.DAILY_QUOTA_EXHAUSTED))

# Test router behavior
transport1 = QuotaTransport()
transport2 = MockTransport()
route1 = ProviderRoute('groq', 'llama-3.1-70b', transport1, weight=10.0)
route2 = ProviderRoute('groq', 'llama-3.1-8b', transport2, weight=1.0)
router = LLMAPIRouter([route1, route2])

result = router.send_request('Short task')
print('Result status:', result['status'])
print('Router attempt:', result.get('router_attempt'))
print('Error type:', result.get('error_type'))