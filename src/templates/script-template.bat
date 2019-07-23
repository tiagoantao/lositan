@echo off
rem Application launcher wrapper script: Windows version

set APP_HOME=%~dp0
set DEFAULT_VM_OPTS=${defaultJvmOpts}

java -splash:title.gif %DEFAULT_VM_OPTS% -jar "%APP_HOME%\\lib\\${name}-${version}.jar"
