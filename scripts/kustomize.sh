#!/bin/bash

kustomize build \
  --enable-alpha-plugins \
  --enable-helm \
  --load-restrictor LoadRestrictionsNone \
  $@
