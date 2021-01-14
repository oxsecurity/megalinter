#!/usr/bin/env bash

# Generate HTML documentation from JSON schemas, using json-schema-for-humans

generate-schema-doc ../megalinter/descriptors/schemas/megalinter-descriptor.jsonschema.json \
                    ../docs/json-schemas/descriptor.html

generate-schema-doc ../megalinter/descriptors/schemas/megalinter-configuration.jsonschema.json \
                    ../docs/json-schemas/configuration.html