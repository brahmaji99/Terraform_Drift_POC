#!/bin/bash

ENV=$1

cd environments/$ENV || exit 1

terraform init -input=false
terraform plan -detailed-exitcode -out=tfplan

EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
  mkdir -p ../../reports/drift
  terraform show -json tfplan > ../../reports/drift/${ENV}.json
fi

exit $EXIT_CODE