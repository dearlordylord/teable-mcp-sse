#!/usr/bin/env python3

import json
import sys
from pathlib import Path

def extract_operations(input_path, output_path):
    """
    Extract operation IDs, descriptions, and paths from an OpenAPI spec
    """
    with open(input_path, 'r') as f:
        spec = json.load(f)
    
    operations = []
    
    for path, path_item in spec['paths'].items():
        for method, operation in path_item.items():
            if 'operationId' in operation:
                operations.append({
                    'operationId': operation.get('operationId'),
                    'description': operation.get('description', ''),
                    'summary': operation.get('summary', ''),
                    'path': path,
                    'method': method
                })
    
    result = {
        'info': {
            'title': spec.get('info', {}).get('title', ''),
            'version': spec.get('info', {}).get('version', ''),
            'description': spec.get('info', {}).get('description', '')
        },
        'operations': operations
    }
    
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Extracted {len(operations)} operations to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_operations.py <input_file> <output_file>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    extract_operations(input_path, output_path)