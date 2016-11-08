#!/bin/sh

export CATALINA_OPTS="$CATALINA_OPTS -server -d64 -Djava.awt.headless=true"
export CATALINA_OPTS="$CATALINA_OPTS -Xms2g"
export CATALINA_OPTS="$CATALINA_OPTS -Xmx2g"
export CATALINA_OPTS="$CATALINA_OPTS -XX:PermSize=256m"
export CATALINA_OPTS="$CATALINA_OPTS -XX:MaxPermSize=256m"
export CATALINA_OPTS="$CATALINA_OPTS -XX:NewSize=256m"
export CATALINA_OPTS="$CATALINA_OPTS -XX:MaxNewSize=256m"
export CATALINA_OPTS="$CATALINA_OPTS -XX:+UseParallelGC"

export CATALINA_OPTS="$CATALINA_OPTS -Djava.library.path=/opt/MacPatch/Server/lib/java"
export CATALINA_OPTS="$CATALINA_OPTS -Djavax.net.ssl.trustStore=/opt/MacPatch/Server/etc/jsseCerts/jssecacerts"
export JAVA_OPTS="$JAVA_OPTS -Djavax.net.ssl.trustStore=/opt/MacPatch/Server/etc/jsseCerts/jssecacerts"	

 
echo "Using CATALINA_OPTS:"
for arg in $CATALINA_OPTS
do
    echo ">> " $arg
done
echo ""
 
echo "Using JAVA_OPTS:"
for arg in $JAVA_OPTS
do
    echo ">> " $arg
done