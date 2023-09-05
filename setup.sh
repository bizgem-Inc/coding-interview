#!/bin/sh

# .envが存在する場合は、コピーしない
if [ ! -f .env ]; then
  cp .env.sample .env
fi

# cp pre-commit .git/hooks/pre-commit
# chmod +x .git/hooks/pre-commit
