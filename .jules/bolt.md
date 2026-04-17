## 2024-04-17 - Added TYPE_MAP mapping cache to .mkdocs/macros.py
**Learning:** Found an opportunity to improve .mkdocs/macros.py by caching or preventing redundant string splits on proto_type in _format_type_for_docs. Every time _format_type_for_docs is called, if the proto_type is not in TYPE_MAP, it does a split.
**Action:** Can memoize or optimize _format_type_for_docs to not do redundant operations.
## 2024-04-17 - Added _parse_proto caching to .mkdocs/macros.py
**Learning:** `_parse_proto` in `.mkdocs/macros.py` reads and parses `.proto` files (like `specification/a2a.proto`). This is called multiple times when rendering pages using macros like `proto_to_table`, `proto_enum_to_table`, and `proto_service_to_table`. This leads to redundant file reads and parsing of the same `.proto` file.
**Action:** Adding a cache (using `@functools.lru_cache`) to `_parse_proto` will prevent redundant parsing and speed up the documentation build process.
