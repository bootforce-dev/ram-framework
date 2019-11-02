%{!?scm_version: %global scm_version %version}

Name:		ram-framework
Version:	0.4.10
Release:	1%{?dist}
Summary:	Framework to manage product state and configuration

License:	MIT
URL:		https://ram-framework.readthedocs.io/en/latest/
Source0:	https://github.com/bootforce-dev/ram-framework/archive/%{scm_version}/%{name}-%{scm_version}.tar.gz

BuildRequires:	python2-devel
BuildRequires:	python2-setuptools
#Requires:	python-iniparse
#Requires:	newt-python

BuildArch:	noarch

%description
Framework to manage product state and configuration

%prep
%autosetup -n %{name}-%{scm_version}

%build
%py2_build

%install
%py2_install

%post
install -d %{_sysconfdir}/ram
test -e %{_sysconfdir}/ram/ram.conf || touch %{_sysconfdir}/ram/ram.conf
test -e %{_sysconfdir}/ram/location.list || touch %{_sysconfdir}/ram/location.list

if [ "$1" -eq "1" ]; then
	ram paths insert %{_exec_prefix}/lib/ram >/dev/null
fi

%preun
if [ "$1" -eq "0" ]; then
	ram paths remove %{_exec_prefix}/lib/ram >/dev/null
fi

test -s %{_sysconfdir}/ram/location.list || rm -f %{_sysconfdir}/ram/location.list
test -s %{_sysconfdir}/ram/ram.conf || rm -f %{_sysconfdir}/ram/ram.conf
rmdir %{_sysconfdir}/ram || :

%files
%defattr(-,root,root,-)
%license LICENSE
%doc README.md
%{_sysconfdir}/bash_completion.d/ram
%{_bindir}/*
%{python2_sitelib}/ram/
%{python2_sitelib}/ram_framework-%{version}-py?.?.egg-info/
%{_exec_prefix}/lib/ram/
%{_datadir}/ram/

%changelog
* Tue Nov 5 2019 Roman Valov <roman.valov@gmail.com> - 0.4.10-1
- initial package
