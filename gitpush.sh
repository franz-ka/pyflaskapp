#!/bin/bash
set -e

git push --set-upstream https://github.com/wencha/pyflaskapp.git master
git add .
git commit -m'dev'
git push master