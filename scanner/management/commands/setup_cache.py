from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.core.cache import cache
from django.db import connection
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Setup cache table and verify cache functionality'

    def handle(self, *args, **options):
        self.stdout.write('Setting up cache system...')
        
        try:
            # Create cache table
            self.stdout.write('Creating cache table...')
            call_command('createcachetable', verbosity=0)
            self.stdout.write(self.style.SUCCESS('Cache table created successfully'))
            
            # Test cache functionality
            self.stdout.write('Testing cache functionality...')
            test_key = 'cache_test_key'
            test_value = 'cache_test_value'
            
            # Set a test value
            cache.set(test_key, test_value, 60)
            
            # Get the test value
            retrieved_value = cache.get(test_key)
            
            if retrieved_value == test_value:
                self.stdout.write(self.style.SUCCESS('Cache is working correctly'))
                # Clean up test key
                cache.delete(test_key)
            else:
                self.stdout.write(self.style.WARNING('Cache test failed - using fallback'))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Cache setup failed: {e}')
            )
            self.stdout.write(
                self.style.WARNING('Application will use memory cache as fallback')
            )
            
        self.stdout.write('Cache setup completed')
