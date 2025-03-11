import yaml
import json
import sys
import re
import os

def generate_operation_id(method, path, operation, existing_ids):
    """
    Generate a unique operationId using method, tags, and summary when available.
    """
    tags = operation.get('tags', [])
    summary = operation.get('summary', '')
    
    method_map = {
        'get': 'get',
        'post': 'create',
        'put': 'update',
        'patch': 'modify',
        'delete': 'delete'
    }
    method_prefix = method_map.get(method.lower(), 'perform')
    
    if summary:
        base_name = ''.join(word.capitalize() for word in summary.split())
    elif tags:
        base_name = tags[0].capitalize()
    else:
        path_parts = [part.strip('{}') for part in path.split('/')]
        path_parts = [part for part in path_parts if part]
        base_name = ''.join(part.capitalize() for part in path_parts) if path_parts else 'root'
    
    operation_id = f"{method_prefix}{base_name}"
    operation_id = re.sub(r'[^a-zA-Z0-9]', '', operation_id)
    if operation_id:
        operation_id = operation_id[0].lower() + operation_id[1:]
    
    base_id = operation_id or 'unnamedOperation'
    if base_id in existing_ids:
        counter = 1
        while f"{base_id}{counter}" in existing_ids:
            counter += 1
        operation_id = f"{base_id}{counter}"
    
    return operation_id

def modify_operation_ids(file_path, n_operations):
    try:
        # Determine file format
        file_ext = os.path.splitext(file_path)[1].lower()
        is_yaml = file_ext in ('.yaml', '.yml')
        
        # Read the file
        with open(file_path, 'r') as f:
            if is_yaml:
                api_spec = yaml.safe_load(f)
            else:
                api_spec = json.load(f)
        
        # Verify OpenAPI spec
        if not isinstance(api_spec, dict) or not api_spec.get('openapi', '').startswith('3.'):
            print("Error: Not a valid OpenAPI 3.x.x specification")
            return False
        
        modified = False
        existing_ids = set()
        paths = api_spec.get('paths', {})
        
        # Step 1: Remove all existing operationIds and collect operations
        operations = []
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            for method in ['get', 'post', 'put', 'patch', 'delete']:
                if method in path_item:
                    operation = path_item[method]
                    if 'operationId' in operation:
                        del operation['operationId']
                        modified = True
                    operations.append((path, method, operation))
        
        # Step 2: Add operationIds to first N operations
        n_operations = min(n_operations, len(operations))  # Don't exceed available operations
        for i in range(n_operations):
            path, method, operation = operations[i]
            new_id = generate_operation_id(method, path, operation, existing_ids)
            operation['operationId'] = new_id
            existing_ids.add(new_id)
            modified = True
        
        if modified:
            with open(file_path, 'w') as f:
                if is_yaml:
                    yaml.dump(api_spec, f, default_flow_style=False, sort_keys=False)
                else:
                    json.dump(api_spec, f, indent=2)
            print(f"Updated {file_path}: removed all operationIds and added to first {n_operations} operations")
            return True
        else:
            print("No changes needed")
            return False
            
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <path_to_openapi_file.[json|yaml]> <number_of_operations>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    try:
        n_operations = int(sys.argv[2])
        if n_operations < 0:
            raise ValueError("Number of operations must be non-negative")
    except ValueError:
        print("Error: Second argument must be a non-negative integer")
        sys.exit(1)
    
    success = modify_operation_ids(file_path, n_operations)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
