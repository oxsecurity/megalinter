#!/usr/bin/env bash

################################################################################
############# Generate architecture diagram of Mega-Linter #####################
#############  See how to do it at https://kroki.io/#how   #####################
################################################################################
shopt -s lastpipe

# Get live stats from YAML descriptor files
docker run --rm -v "${PWD}":/workdir mikefarah/yq eval '{.descriptor_id: .descriptor_type}' megalinter/descriptors/*.megalinter-descriptor.yml | descriptors=$(</dev/stdin)

grep -o "language" <<< "$descriptors" | wc -l | language=$(</dev/stdin)
grep -o " format" <<< "$descriptors" | wc -l | format=$(</dev/stdin)
grep -o "tooling_format" <<< "$descriptors" | wc -l | tooling_format=$(</dev/stdin)

cp docs/assets/archi.blockdiag.txt /tmp/ml_archi_diagram

sed -i "s/{language}/$language/" /tmp/ml_archi_diagram
sed -i "s/{format}/$format/" /tmp/ml_archi_diagram
sed -i "s/{tooling_format}/$tooling_format/" /tmp/ml_archi_diagram

# Build diagram in blockdiag format and encode diagram using deflate + base64
cat /tmp/ml_archi_diagram | python -c "import sys; import base64; import zlib; print(base64.urlsafe_b64encode(zlib.compress(sys.stdin.read(), 9)))" | diagram=$(</dev/stdin)

echo "https://kroki.io/blockdiag/svg/$diagram"
