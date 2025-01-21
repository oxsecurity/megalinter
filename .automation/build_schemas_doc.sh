#!/usr/bin/env bash

# Generate HTML documentation from JSON schemas, using json-schema-for-humans :)

generate-schema-doc ../megalinter/descriptors/schemas/megalinter-descriptor.jsonschema.json \
  ../docs/json-schemas/descriptor.html \
  --config minify=false \
  --config expand_buttons=false \
  --config link_to_reused_ref=false

generate-schema-doc ../megalinter/descriptors/schemas/megalinter-configuration.jsonschema.json \
  ../docs/json-schemas/configuration.html \
  --config minify=false \
  --config expand_buttons=false \
  --config link_to_reused_ref=false
