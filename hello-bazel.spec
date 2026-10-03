# This is a demonstration package: a trivial C++ program built with Bazel to
# prove that the Fedora-packaged Bazel can run a fully offline build under
# Fedora's no-network build policy.
#
# Bazel normally downloads its external modules (rules_cc, protobuf, and their
# transitive dependencies) from the Bazel Central Registry on the first build.
# That is not allowed during an RPM build, so the modules are vendored ahead of
# time with "bazel vendor" and shipped as a second source archive. During the
# build Bazel is pointed at that vendored tree and told never to download, so
# the whole build runs with no network access.

# Bazel compiles with its own toolchain flags, not Fedora's build flags, so the
# resulting binary carries no separable debug information. Disable the debuginfo
# subpackage, which would otherwise fail extraction.
%global debug_package %{nil}

Name:           hello-bazel
Version:        1.0
Release:        1%{?dist}
Summary:        Minimal C++ program built offline with Bazel

License:        MIT
URL:            https://bazel.build/
Source0:        hello-bazel-%{version}.tar.gz
# The external Bazel modules this build depends on, captured with
# "bazel vendor --vendor_dir=vendor //:hello" so the build needs no network.
Source1:        hello-bazel-vendor-%{version}.tar.gz

# bazel-rpm-macros provides the %%bazel macro and pulls in Bazel and a JDK.
BuildRequires:  bazel-rpm-macros
BuildRequires:  gcc
BuildRequires:  gcc-c++

%description
A "hello world" C++ program whose only purpose is to demonstrate that the
Fedora Bazel package can build a project offline. The Bazel modules it depends
on are vendored into the source RPM, and the build is run with downloads
disabled so that it works inside Fedora's network-isolated build environment.

%prep
%autosetup -n hello-bazel-%{version}
# Unpack the vendored Bazel modules into the workspace so the offline build can
# find them under the vendor/ directory referenced below.
tar -xf %{SOURCE1}

%build
# The %%bazel macro (from bazel-rpm-macros) runs Bazel offline against the
# vendored modules under vendor/, using the host JDK and Fedora's build flags.
%bazel build //:hello --verbose_failures

%install
# bazel-bin is a convenience symlink into Bazel's output tree.
install -Dpm 0755 bazel-bin/hello %{buildroot}%{_bindir}/hello-bazel

%check
%{buildroot}%{_bindir}/hello-bazel

%files
%license LICENSE
%{_bindir}/hello-bazel

%changelog
* Fri Oct 02 2026 bazel-hello-demo <noreply@example.com> - 1.0-1
- Initial demonstration package built offline with Fedora's Bazel.
