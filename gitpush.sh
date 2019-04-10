#!/bin/bash
set -e

git add .
git commit -m'dev'
git push --set-upstream https://github.com/wencha/pyflaskapp.git master