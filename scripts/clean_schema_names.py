#!/usr/bin/env python3
import json
import sys

def clean_name(name):
    # Strip the .jsonschema.json suffix
    if name.endswith(".jsonschema.json"):
        name = name[:-16]
    # Strip the primary package namespace
    if name.startswith("lf.a2a.v1."):
        name = name[len("lf.a2a.v1."):]

    if name.startswith("google.protobuf."):
        name = name[len("google.protobuf."):]
    return name

def replace_refs(obj, mapping):
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str):
                if v.startswith("#/$defs/"):
                    old_def = v[len("#/$defs/"):]
                    if old_def in mapping:
                        new_obj[k] = f"#/$defs/{mapping[old_def]}"
                    else:
                        new_obj[k] = v
                else:
                    new_obj[k] = v
            else:
                new_obj[k] = replace_refs(v, mapping)
        return new_obj
    elif isinstance(obj, list):
        return [replace_refs(item, mapping) for item in obj]
    else:
        return obj

def main():
    if len(sys.argv) < 3:
        print("Usage: python clean_schema_names.py <input.json> <output.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, 'r') as f:
        schema = json.load(f)

    defs = schema.get("$defs", {})
    mapping = {}

    # 1. Create mapping and new defs
    new_defs = {}
    for old_name, val in defs.items():
        new_name = clean_name(old_name)
        mapping[old_name] = new_name

        # Strip $schema from child schemas to comply with Draft 2020-12
        if isinstance(val, dict):
            val_clean = val.copy()
            val_clean.pop("$schema", None)
            new_defs[new_name] = val_clean
        else:
            new_defs[new_name] = val

    schema["$defs"] = new_defs


    # 2. Update references in the entire schema
    schema = replace_refs(schema, mapping)

    with open(output_file, 'w') as f:
        json.dump(schema, f, indent=2)
        f.write('\n')

if __name__ == "__main__":
    main()
