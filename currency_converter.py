""" 
Currency Converter Automation Script
Author: Felipe Silva Jiron
Description: Automated Currency Conversion tool with API Integration 
This script fetches exchange rates from an API and converts amounts between different currencies.
Version: 1.0
Date: 7/7/2025
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('currency_converter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CurrencyConverter:
    """A class to handle currency conversion operations"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the currency converter
        
        Args:
            api_key: API key for the exchange rate service
        """
        self.api_key = api_key or os.getenv('EXCHANGE_API_KEY')
        self.base_url = "https://api.exchangerate-api.com/v4/latest"
        self.cache = {}
        self.cache_timeout = 3600  # 1 hour in seconds
        
    def get_exchange_rates(self, base_currency: str = "USD") -> Dict:
        """
        Fetch current exchange rates
        
        Args:
            base_currency: The base currency code (default: USD)
            
        Returns:
            Dictionary of exchange rates
        """
        try:
            # Check cache first
            cache_key = f"{base_currency}_{datetime.now().hour}"
            if cache_key in self.cache:
                logger.info(f"Using cached rates for {base_currency}")
                return self.cache[cache_key]
            
            # Make API request
            response = requests.get(f"{self.base_url}/{base_currency}")
            response.raise_for_status()
            
            data = response.json()
            self.cache[cache_key] = data
            logger.info(f"Successfully fetched rates for {base_currency}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching exchange rates: {e}")
            raise
            
    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """
        Convert amount from one currency to another
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Converted amount
        """
        try:
            # Get exchange rates
            rates_data = self.get_exchange_rates(from_currency)
            rates = rates_data.get('rates', {})
            
            if to_currency not in rates:
                raise ValueError(f"Currency {to_currency} not supported")
                
            converted_amount = amount * rates[to_currency]
            
            logger.info(
                f"Converted {amount} {from_currency} to "
                f"{converted_amount:.2f} {to_currency}"
            )
            
            return round(converted_amount, 2)
            
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            raise
            
    def get_supported_currencies(self) -> list:
        """Get list of supported currencies"""
        try:
            data = self.get_exchange_rates()
            return list(data.get('rates', {}).keys())
        except Exception as e:
            logger.error(f"Error fetching supported currencies: {e}")
            return []


def main():
    """Main function to demonstrate the currency converter"""
    converter = CurrencyConverter()
    
    # Example conversions
    conversions = [
        (100, "USD", "EUR"),
        (50, "GBP", "JPY"),
        (1000, "EUR", "USD")
    ]
    
    print("Currency Converter Automation Script")
    print("=" * 40)
    
    for amount, from_curr, to_curr in conversions:
        try:
            result = converter.convert(amount, from_curr, to_curr)
            print(f"{amount} {from_curr} = {result} {to_curr}")
        except Exception as e:
            print(f"Error converting {from_curr} to {to_curr}: {e}")
    
    # Show supported currencies
    print("\nSupported currencies:")
    currencies = converter.get_supported_currencies()
    print(", ".join(currencies[:10]) + "...")


if __name__ == "__main__":
    main()
    
    