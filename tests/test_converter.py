import pytest
from unittest.mock import patch, Mock
import sys
import os

# Add parent directory to path so we can import our module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from currency_converter import CurrencyConverter


class TestCurrencyConverter:
    """Test suite for CurrencyConverter class"""
    
    @pytest.fixture
    def converter(self):
        """Create a converter instance for testing"""
        return CurrencyConverter()
    
    @pytest.fixture
    def mock_api_response(self):
        """Mock API response data"""
        return {
            "base": "USD",
            "date": "2024-01-01",
            "rates": {
                "EUR": 0.85,
                "GBP": 0.73,
                "JPY": 110.0,
                "CAD": 1.25,
                "AUD": 1.35,
                "CHF": 0.92,
                "CNY": 6.37,
                "INR": 74.5
            }
        }
    
    def test_converter_initialization(self, converter):
        """Test converter initializes correctly"""
        assert converter.base_url == "https://api.exchangerate-api.com/v4/latest"
        assert converter.cache == {}
        assert converter.cache_timeout == 3600
    
    @patch('requests.get')
    def test_get_exchange_rates_success(self, mock_get, converter, mock_api_response):
        """Test successful API call"""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call method
        result = converter.get_exchange_rates("USD")
        
        # Assertions
        assert result == mock_api_response
        mock_get.assert_called_once_with("https://api.exchangerate-api.com/v4/latest/USD")
    
    @patch('requests.get')
    def test_get_exchange_rates_api_error(self, mock_get, converter):
        """Test API error handling"""
        # Setup mock to raise an exception
        mock_get.side_effect = Exception("API Error")
        
        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            converter.get_exchange_rates("USD")
        
        assert "API Error" in str(exc_info.value)
    
    @patch('requests.get')
    def test_convert_success(self, mock_get, converter, mock_api_response):
        """Test successful currency conversion"""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test conversion
        result = converter.convert(100, "USD", "EUR")
        
        # Should be 100 * 0.85 = 85.0
        assert result == 85.0
    
    @patch('requests.get')
    def test_convert_with_decimals(self, mock_get, converter, mock_api_response):
        """Test conversion with decimal amounts"""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test conversion with decimals
        result = converter.convert(99.99, "USD", "GBP")
        
        # Should be 99.99 * 0.73 = 72.99 (rounded to 2 decimals)
        assert result == 72.99
    
    @patch('requests.get')
    def test_convert_invalid_currency(self, mock_get, converter, mock_api_response):
        """Test conversion with invalid currency"""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Should raise ValueError for invalid currency
        with pytest.raises(ValueError) as exc_info:
            converter.convert(100, "USD", "INVALID")
        
        assert "Currency INVALID not supported" in str(exc_info.value)
    
    @patch('requests.get')
    def test_caching_mechanism(self, mock_get, converter, mock_api_response):
        """Test that caching prevents duplicate API calls"""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # First call
        result1 = converter.get_exchange_rates("USD")
        # Second call (should use cache)
        result2 = converter.get_exchange_rates("USD")
        
        # Both results should be the same
        assert result1 == result2
        # API should only be called once due to caching
        assert mock_get.call_count == 1
    
    @patch('requests.get')
    def test_different_base_currencies(self, mock_get, converter):
        """Test using different base currencies"""
        # Setup different responses for different currencies
        def side_effect(url):
            mock_response = Mock()
            if "EUR" in url:
                mock_response.json.return_value = {
                    "base": "EUR",
                    "rates": {"USD": 1.18, "GBP": 0.86}
                }
            else:
                mock_response.json.return_value = {
                    "base": "USD",
                    "rates": {"EUR": 0.85, "GBP": 0.73}
                }
            mock_response.raise_for_status.return_value = None
            return mock_response
        
        mock_get.side_effect = side_effect
        
        # Test different base currencies
        usd_rates = converter.get_exchange_rates("USD")
        eur_rates = converter.get_exchange_rates("EUR")
        
        assert usd_rates["base"] == "USD"
        assert eur_rates["base"] == "EUR"
        assert mock_get.call_count == 2
    
    @patch('requests.get')
    def test_get_supported_currencies(self, mock_get, converter, mock_api_response):
        """Test getting list of supported currencies"""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Get supported currencies
        currencies = converter.get_supported_currencies()
        
        # Should return list of currency codes
        assert isinstance(currencies, list)
        assert "EUR" in currencies
        assert "GBP" in currencies
        assert "JPY" in currencies
        assert len(currencies) == 8  # Based on our mock data
    
    def test_convert_zero_amount(self, converter):
        """Test converting zero amount"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "base": "USD",
                "rates": {"EUR": 0.85}
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = converter.convert(0, "USD", "EUR")
            assert result == 0.0
    
    def test_convert_large_amount(self, converter):
        """Test converting large amounts"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "base": "USD",
                "rates": {"EUR": 0.85}
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = converter.convert(1000000, "USD", "EUR")
            assert result == 850000.0


# Additional tests for edge cases
class TestEdgeCases:
    """Test edge cases and error scenarios"""
    
    @pytest.fixture
    def converter(self):
        return CurrencyConverter()
    
    def test_same_currency_conversion(self, converter):
        """Test converting to the same currency"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "base": "USD",
                "rates": {"USD": 1.0}
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = converter.convert(100, "USD", "USD")
            assert result == 100.0
    
    @patch('requests.get')
    def test_network_timeout(self, mock_get, converter):
        """Test handling network timeout"""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Connection timeout")
        
        with pytest.raises(requests.exceptions.Timeout):
            converter.get_exchange_rates("USD")
    
    @patch('requests.get')
    def test_invalid_json_response(self, mock_get, converter):
        """Test handling invalid JSON response"""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError):
            converter.get_exchange_rates("USD")


if __name__ == "__main__":
    # Run tests if this file is executed directly
    pytest.main([__file__, "-v"])

    