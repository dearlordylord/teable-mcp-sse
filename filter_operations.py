#!/usr/bin/env python3

import json
import sys

def filter_operations(input_path, output_path, allowed_ops):
    """
    Filter the OpenAPI spec to only include operations with specified operationIds
    """
    with open(input_path, 'r') as f:
        spec = json.load(f)
    
    # Create a set of allowed operation IDs for faster lookup
    allowed_operation_ids = set(allowed_ops)
    removed_count = 0
    
    # Filter operations in the paths object
    for path, path_item in list(spec['paths'].items()):
        for method, operation in list(path_item.items()):
            # Skip non-operation properties
            if method.startswith('x-') or method == 'parameters':
                continue
                
            operation_id = operation.get('operationId')
            if operation_id and operation_id not in allowed_operation_ids:
                # Remove this operation
                del path_item[method]
                removed_count += 1
        
        # If no operations left in this path, remove the path
        if not any(not k.startswith('x-') and k != 'parameters' for k in path_item):
            del spec['paths'][path]
    
    # Write the filtered spec
    with open(output_path, 'w') as f:
        json.dump(spec, f, indent=2)
    
    print(f"Removed {removed_count} operations. Kept operations with the following IDs: {', '.join(allowed_operation_ids)}")
    print(f"Filtered OpenAPI spec saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python filter_operations.py <input_file> <output_file>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    # List of allowed operation IDs
    allowed_ops = [
        "getListRecords",
        "getGetRecord",
        "createCreateRecords",
        "modifyUpdateRecord",
        "modifyUpdateMultipleRecords",
        "deleteDeleteRecord",
        "deleteDeleteRecords",
        "createDuplicateRecord",
        "getListTables",
        "getGetTableDetails",
        "createCreateTable",
        "updateUpdateTableName",
        "deleteDeleteTable",
        "getListFields",
        "getGetAField",
        "createCreateField",
        "modifyUpdateField",
        "deleteDeleteField",
        "updateConvertFieldType",
        "getGetViewList",
        "getView1",
        "createView",
        "deleteView"
    ]
    
    filter_operations(input_path, output_path, allowed_ops)