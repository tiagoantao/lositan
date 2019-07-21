#!/usr/bin/env sh
# Application launcher wrapper script: *nix version

APP_HOME=\$(dirname \$0)
DEFAULT_VM_OPTS="${defaultJvmOpts}"
EXTRA_OPTS=

# For Darwin, add options to specify how the application appears in the dock
if [ "Darwin" = "\$(uname)" ]; then
    EXTRA_OPTS="\${EXTRA_OPTS} -Xdock:name=${app.title}"
fi

java -splash:title.gif \${DEFAULT_VM_OPTS} \${EXTRA_OPTS} -jar "\${APP_HOME}/lib/${name}-${version}.jar"
