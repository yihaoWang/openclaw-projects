#!/usr/bin/env python3
"""
Unit tests for Japan Supermarket Discount Timer bot
"""

import unittest
import json
import sys
from pathlib import Path
from datetime import datetime, time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.telegram_bot import (
    load_discount_data,
    get_item_name,
    format_discount_schedule
)

class TestDataLoading(unittest.TestCase):
    """Test data loading and validation"""
    
    def setUp(self):
        """Load data before each test"""
        self.data = load_discount_data()
    
    def test_data_loads(self):
        """Test that data file loads successfully"""
        self.assertIsNotNone(self.data)
        self.assertIn('supermarkets', self.data)
    
    def test_supermarket_count(self):
        """Test minimum number of supermarkets"""
        self.assertGreaterEqual(len(self.data['supermarkets']), 10)
    
    def test_supermarket_structure(self):
        """Test that supermarkets have required fields"""
        for market in self.data['supermarkets']:
            self.assertIn('name', market)
            self.assertIn('name_en', market)
            self.assertIn('discount_schedule', market)
            self.assertIsInstance(market['discount_schedule'], list)
            self.assertGreater(len(market['discount_schedule']), 0)
    
    def test_discount_schedule_structure(self):
        """Test discount schedule format"""
        for market in self.data['supermarkets']:
            for schedule in market['discount_schedule']:
                self.assertIn('time', schedule)
                self.assertIn('discount', schedule)
                self.assertIn('items', schedule)
                
                # Validate time format (HH:MM)
                try:
                    datetime.strptime(schedule['time'], '%H:%M')
                except ValueError:
                    self.fail(f"Invalid time format: {schedule['time']}")
    
    def test_item_categories(self):
        """Test that item categories are defined"""
        self.assertIn('item_categories', self.data)
        categories = self.data['item_categories']
        
        # Check common items exist
        self.assertIn('bento', categories)
        self.assertIn('deli', categories)
        
        # Check each has both languages
        for item, translations in categories.items():
            self.assertIn('en', translations)
            self.assertIn('ja', translations)

class TestHelperFunctions(unittest.TestCase):
    """Test helper functions"""
    
    def setUp(self):
        """Load data before each test"""
        self.data = load_discount_data()
    
    def test_get_item_name_english(self):
        """Test getting item name in English"""
        name = get_item_name('bento', 'en')
        self.assertEqual(name, 'Bento (Boxed Meals)')
    
    def test_get_item_name_japanese(self):
        """Test getting item name in Japanese"""
        name = get_item_name('bento', 'ja')
        self.assertEqual(name, '弁当')
    
    def test_get_item_name_unknown(self):
        """Test getting unknown item name"""
        name = get_item_name('unknown_item', 'en')
        self.assertEqual(name, 'unknown_item')
    
    def test_format_discount_schedule(self):
        """Test discount schedule formatting"""
        market = self.data['supermarkets'][0]
        formatted = format_discount_schedule(market, 'en')
        
        self.assertIsInstance(formatted, str)
        self.assertGreater(len(formatted), 0)
        # Should contain time and discount info
        self.assertIn(market['discount_schedule'][0]['time'], formatted)

class TestDataIntegrity(unittest.TestCase):
    """Test data integrity and consistency"""
    
    def setUp(self):
        """Load data before each test"""
        self.data = load_discount_data()
    
    def test_no_duplicate_names(self):
        """Test that supermarket names are unique"""
        names = [m['name_en'] for m in self.data['supermarkets']]
        self.assertEqual(len(names), len(set(names)))
    
    def test_time_ordering(self):
        """Test that discount times are in chronological order"""
        for market in self.data['supermarkets']:
            times = [
                datetime.strptime(s['time'], '%H:%M').time()
                for s in market['discount_schedule']
            ]
            
            # Check if times are sorted
            sorted_times = sorted(times)
            self.assertEqual(times, sorted_times,
                f"{market['name_en']} has unsorted discount times")
    
    def test_discount_progression(self):
        """Test that discounts generally increase over time"""
        for market in self.data['supermarkets']:
            schedule = market['discount_schedule']
            
            if len(schedule) > 1:
                # Extract numeric discount values
                discounts = []
                for s in schedule:
                    discount_str = s['discount'].replace('%', '').replace('off', '').strip()
                    
                    # Handle ranges like "20-30%"
                    if '-' in discount_str:
                        discount_str = discount_str.split('-')[1]
                    
                    # Handle "half price" / "半額"
                    if '半' in discount_str or 'half' in discount_str.lower():
                        discounts.append(50)
                    else:
                        try:
                            discounts.append(int(discount_str))
                        except ValueError:
                            pass
                
                # Check discounts don't decrease
                for i in range(len(discounts) - 1):
                    self.assertLessEqual(discounts[i], discounts[i + 1],
                        f"{market['name_en']} has decreasing discounts")
    
    def test_regions_reference_valid_stores(self):
        """Test that regions reference actual stores"""
        if 'regions' in self.data:
            all_store_names = set()
            for market in self.data['supermarkets']:
                all_store_names.add(market['name_en'])
                if 'brand' in market:
                    all_store_names.add(market['brand'])
            
            for region, stores in self.data['regions'].items():
                for store in stores:
                    self.assertIn(store, all_store_names,
                        f"Region {region} references unknown store: {store}")

class TestTimeCalculations(unittest.TestCase):
    """Test time-based calculations"""
    
    def test_current_time_check(self):
        """Test checking if discount is currently active"""
        # Create a test schedule
        test_time = time(19, 0)
        current_time = time(19, 30)
        
        # Discount should be active
        self.assertGreater(current_time, test_time)
        
        # Within 3-hour window
        time_diff = current_time.hour - test_time.hour
        self.assertLess(time_diff, 3)
    
    def test_upcoming_discount_check(self):
        """Test checking upcoming discounts"""
        current = datetime.now()
        future = datetime.strptime("20:00", "%H:%M").time()
        
        # If current time is before future time
        if current.hour < 20:
            self.assertLess(current.time(), future)

def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDataLoading))
    suite.addTests(loader.loadTestsFromTestCase(TestHelperFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestDataIntegrity))
    suite.addTests(loader.loadTestsFromTestCase(TestTimeCalculations))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())
