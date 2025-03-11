import yaml
import json
import sys
import re
import os

def generate_operation_id(method, path):
    """
    Generate a meaningful operationId from HTTP method and path.
    Example: GET /users/{id} -> getUserById
    """
    # Convert path to camelCase
    path_parts = [part.strip('{}') for part in path.split('/')]
    path_parts = [part for part in path_parts if part]  # Remove empty parts
    
    if not path_parts:
        base_name = 'root'
    else:
        base_name = ''.join(part.capitalize() for part in path_parts)
    
    method_map = {
        'get': 'get',
        'post': 'create',
        'put': 'update',
        'patch': 'modify',
        'delete': 'delete'
    }
    
    method_prefix = method_map.get(method.lower(), 'perform')
    operation_id = f"{method_prefix}{base_name}"
    operation_id = re.sub(r'[^a-zA-Z0-9]', '', operation_id)
    
    if operation_id:
        operation_id = operation_id[0].lower() + operation_id[1:]
    
    return operation_id or 'unnamedOperation'

def add_operation_ids(file_path):
    try:
        # Determine file format based on extension
        file_ext = os.path.splitext(file_path)[1].lower()
        is_yaml = file_ext in ('.yaml', '.yml')
        
        # Read the file
        with open(file_path, 'r') as f:
            if is_yaml:
                api_spec = yaml.safe_load(f)
            else:  # Assume JSON
                api_spec = json.load(f)
        
        # Verify it's an OpenAPI spec
        if not isinstance(api_spec, dict) or not api_spec.get('openapi', '').startswith('3.'):
            print("Error: Not a valid OpenAPI 3.x.x specification")
            return False
        
        modified = False
        paths = api_spec.get('paths', {})
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
                
            for method in ['get', 'post', 'put', 'patch', 'delete']:
                if method in path_item:
                    operation = path_item[method]
                    if 'operationId' not in operation:
                        operation['operationId'] = generate_operation_id(method, path)
                        modified = True
                    elif not isinstance(operation['operationId'], str) or not operation['operationId']:
                        operation['operationId'] = generate_operation_id(method, path)
                        modified = True
        
        if modified:
            with open(file_path, 'w') as f:
                if is_yaml:
                    yaml.dump(api_spec, f, default_flow_style=False, sort_keys=False)
                else:
                    json.dump(api_spec, f, indent=2)
            print(f"Updated {file_path} with operationIds")
            return True
        else:
            print("No changes needed - all operations already have operationIds")
            return False
            
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_openapi_file.[json|yaml]>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    success = add_operation_ids(file_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
