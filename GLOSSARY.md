# Glossary

**no-silent-failures**: a tiny tasks API that cannot break without someone being told.

- **Task**: the one domain object the API stores (create, read, update, delete).
- **Chaos endpoint** (`/chaos`): an endpoint that fails or slows down on purpose, so each alert can be triggered by hand.
