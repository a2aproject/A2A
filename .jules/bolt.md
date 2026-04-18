## 2024-04-18 - MkDocs Macro Parsing Redundancy
**Learning:** MkDocs plugins and macros are executed for each invocation on a page. In `docs/specification.md`, `proto_to_table` and other custom macros were parsing the main `a2a.proto` file dozens of times per build. This unoptimized repeated disk reading and AST construction accounted for ~65% of the `mkdocs build` time (about 10 seconds).
**Action:** Always wrap expensive, repeatable I/O and parsing logic within `define_env` with `@functools.lru_cache(maxsize=None)` or similar memoization when executing MkDocs macros.
