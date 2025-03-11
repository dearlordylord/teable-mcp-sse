import yaml
import json
import sys
import re
import os

def generate_operation_id(method, path, operation, existing_ids):
    """
    Generate a unique operationId using method, tags, and summary when available.
    Example: GET /table/{tableId}/record/{recordId} with tag "record" and summary "Get record"
    -> getRecord
    """
    # Get useful components
    tags = operation.get('tags', [])
    summary = operation.get('summary', '')

    # Method prefix
    method_map = {
        'get': 'get',
        'post': 'create',
        'put': 'update',
        'patch': 'modify',
        'delete': 'delete'
    }
    method_prefix = method_map.get(method.lower(), 'perform')

    # Base name preference: summary > tag > path
    if summary:
        base_name = ''.join(word.capitalize() for word in summary.split())
    elif tags:
        base_name = tags[0].capitalize()
    else:
        path_parts = [part.strip('{}') for part in path.split('/')]
        path_parts = [part for part in path_parts if part]
        base_name = ''.join(part.capitalize() for part in path_parts) if path_parts else 'root'

    # Clean up and combine
    operation_id = f"{method_prefix}{base_name}"
    operation_id = re.sub(r'[^a-zA-Z0-9]', '', operation_id)
    if operation_id:
        operation_id = operation_id[0].lower() + operation_id[1:]

    # Ensure uniqueness
    base_id = operation_id or 'unnamedOperation'
    if base_id in existing_ids:
        counter = 1
        while f"{base_id}{counter}" in existing_ids:
            counter += 1
        operation_id = f"{base_id}{counter}"

    return operation_id

def add_operation_ids(file_path):
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

        # Rewrite all operationIds
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            for method in ['get', 'post', 'put', 'patch', 'delete']:
                if method in path_item:
                    operation = path_item[method]
                    new_id = generate_operation_id(method, path, operation, existing_ids)
                    # Always rewrite operationId
                    if 'operationId' not in operation or operation['operationId'] != new_id:
                        operation['operationId'] = new_id
                        modified = True
                    existing_ids.add(new_id)

        if modified:
            with open(file_path, 'w') as f:
                if is_yaml:
                    yaml.dump(api_spec, f, default_flow_style=False, sort_keys=False)
                else:
                    json.dump(api_spec, f, indent=2)
            print(f"Updated {file_path} with rewritten operationIds")
            return True
        else:
            print("No changes needed - all operationIds already match the new format")
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