#!/usr/bin/env python3
"""Test script for custom flavor generation"""

import os
import sys
import yaml

# Add the megalinter directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'megalinter'))

from megalinter import config
from megalinter.MegaLinter import Megalinter

def test_custom_flavor_generation():
    """Test custom flavor generation functionality"""
    print("Testing custom flavor generation...")
    
    # Set up environment
    os.environ['GENERATE_CUSTOM_FLAVOR'] = 'true'
    
    # Initialize config
    config.init_config('test')
    
    # Create a mock MegaLinter instance
    megalinter = Megalinter({'workspace': '/tmp/test'})
    megalinter.request_id = 'test'
    megalinter.github_workspace = 'c:/git/test-custom-flavor'
    megalinter.validate_all_code_base = True
    
    # Create mock linters with some active ones
    class MockLinter:
        def __init__(self, descriptor_id, linter_name, is_active=True, nb_files=1):
            self.descriptor_id = descriptor_id
            self.linter_name = linter_name
            self.is_active = is_active
            self.nb_files = nb_files
    
    megalinter.linters = [
        MockLinter('JAVASCRIPT', 'standard', True, 1),
        MockLinter('JSON', 'jsonlint', True, 1),
        MockLinter('JSON', 'prettier', True, 1),
        MockLinter('REPOSITORY', 'gitleaks', True, 0),  # This should be excluded due to nb_files=0
        MockLinter('SPELL', 'cspell', False, 1),  # This should be excluded due to is_active=False
    ]
    
    # Test the custom flavor generation
    try:
        megalinter.generate_custom_flavor_file()
        
        # Check if file was created
        custom_flavor_file = os.path.join(megalinter.github_workspace, "megalinter-custom-flavor.yml")
        if os.path.exists(custom_flavor_file):
            print(f"✅ Custom flavor file created successfully: {custom_flavor_file}")
            
            # Read and display the contents
            with open(custom_flavor_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                print("📄 Generated configuration:")
                print(yaml.dump(config_data, default_flow_style=False, sort_keys=False))
                
            return True
        else:
            print(f"❌ Custom flavor file was not created at: {custom_flavor_file}")
            return False
            
    except Exception as e:
        print(f"❌ Error during custom flavor generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_custom_flavor_generation()
