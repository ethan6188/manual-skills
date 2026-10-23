#!/bin/bash
# Upload a static site directory to a server that only gives you a "run this command remotely" channel
# (no scp/rsync): tar it, push base64 chunks through the channel, verify SHA-256, extract.
#
#   RUN='ssh root@host' REMOTE_DIR=/opt/site ./publish-static.sh path/to/site
#
# RUN is any command that takes one argument (a shell string) and runs it on the server.
set -euo pipefail

: "${RUN:?set RUN to the remote-exec command, e.g. 'ssh root@host'}"
: "${REMOTE_DIR:?set REMOTE_DIR, e.g. /opt/site}"
site_dir=$(cd "${1:?usage: publish-static.sh SITE_DIR}" && pwd)

staging=$(mktemp -d)
trap 'rm -rf "$staging"' EXIT
remote=/tmp/site-upload.tar.gz

COPYFILE_DISABLE=1 tar -czf "$staging/site.tar.gz" --no-xattrs --exclude='.DS_Store' -C "$site_dir" .
local_sha=$(shasum -a 256 "$staging/site.tar.gz" | cut -d' ' -f1)
base64 < "$staging/site.tar.gz" | split -a 4 -b 100000 - "$staging/chunk."

$RUN "truncate -s 0 $remote.b64"
for chunk in "$staging"/chunk.*; do
  $RUN "printf '%s' '$(<"$chunk")' >> $remote.b64"
done
$RUN "base64 -d < $remote.b64 > $remote && unlink $remote.b64 && printf '%s  %s\n' '$local_sha' '$remote' | sha256sum -c -"
$RUN "mkdir -p $REMOTE_DIR && tar -xzf $remote --no-same-owner -C $REMOTE_DIR && unlink $remote && chmod -R a+rX $REMOTE_DIR"
echo "published $site_dir -> $REMOTE_DIR"
