#!/bin/sh
# Assemble the two source archives that hello-bazel.spec references but that are
# not published online, so they cannot be fetched with spectool:
#
#   hello-bazel-VERSION.tar.gz         the project sources
#   hello-bazel-vendor-VERSION.tar.gz  the external Bazel modules, vendored
#
# rpm-build-assist's src-get runs this in the checkout directory while preparing
# the src.rpm. The vendored modules are regenerated here with "bazel vendor",
# which needs network access and a bazel on PATH; the tree it produces then lets
# the RPM build itself run with no network at all.
set -eu

name=hello-bazel
version=1.0

srcdir=$(cd "$(dirname "$0")" && pwd)
proj="$srcdir/$name"

# Source0: the project tree, rooted at hello-bazel-VERSION/ to match the
# "%autosetup -n hello-bazel-%{version}" in the spec. The vendor directory is a
# generated artifact and ships separately as Source1, so exclude it here.
tar --exclude=vendor \
    --transform="s,^$name,$name-$version," \
    -czf "$srcdir/$name-$version.tar.gz" \
    -C "$srcdir" "$name"

# Source1: the external Bazel modules. "bazel vendor" resolves them from the
# Bazel Central Registry (pinned by the checked-in MODULE.bazel.lock) into
# vendor/; the RPM build consumes this with downloads disabled.
rm -rf "$proj/vendor"
( cd "$proj" && bazel vendor //:hello --vendor_dir=vendor )
tar -czf "$srcdir/$name-vendor-$version.tar.gz" -C "$proj" vendor
rm -rf "$proj/vendor"
