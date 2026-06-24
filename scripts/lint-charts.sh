#!/bin/bash

# From https://stackoverflow.com/a/4774063
REPO_DIR="$( cd -- "$(dirname "$0")/.." >/dev/null 2>&1 ; pwd -P )"

for CHART in $(find "$REPO_DIR/charts" -mindepth 1 -maxdepth 1 -type d); do
  # Not all charts have values.yaml, e.g. library charts.
  VALUES_PATH="$CHART/values.yaml"
  MAYBE_INCLUDE_VALUES=""
  if [ -s "$VALUES_PATH" ]; then
    MAYBE_INCLUDE_VALUES="--values $VALUES_PATH"
  fi

  # If a random required values file exists, we need to include those values
  # when linting and templating otherwise both will fail because required values
  # are missing.
  RANDOM_REQUIRED_VALUES_PATH="$CHART/random-required-values.yaml"
  MAYBE_INCLUDE_RANDOM_REQUIRED_VALUES=""
  if [ -s "$RANDOM_REQUIRED_VALUES_PATH" ]; then
    MAYBE_INCLUDE_RANDOM_REQUIRED_VALUES="--values $RANDOM_REQUIRED_VALUES_PATH"
  fi

  helm lint "$CHART" \
    $MAYBE_INCLUDE_VALUES \
    $MAYBE_INCLUDE_RANDOM_REQUIRED_VALUES

  # Only template application charts; skip library charts.
  if $(grep -qE '^type: application$' "$CHART/Chart.yaml"); then
    helm template "$CHART" \
      $MAYBE_INCLUDE_VALUES \
      $MAYBE_INCLUDE_RANDOM_REQUIRED_VALUES | \
      yamllint -
  fi
done
