%define	snap	01-03-26
Summary:	Network monitoring tool
Summary(pl):	Narzêdzie do monitorowania sieci
Name:		ntop
Version:	1.3.2
Release:	3.%(echo %{snap} | sed -e "s/-//g")
License:	GPL
Group:		Networking
Group(de):	Netzwerkwesen
Group(pl):	Sieciowe
Source0:	http://snapshot.ntop.org/tgz/%{name}-%{snap}.tgz
Patch0:		%{name}-configure.patch
Patch1:		%{name}-externallib.patch
Patch2:		%{name}-perl.patch
URL:		http://www.ntop.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	gd-devel >= 2.0.1
BuildRequires:	gdbm-devel
BuildRequires:	libpcap-devel
BuildRequires:	libpng-devel
BuildRequires:	libwrap-devel
BuildRequires:	libtool
BuildRequires:	ncurses-devel >= 5.2
BuildRequires:	openssl-devel >= 0.9.6a
BuildRequires:	readline-devel >= 4.2
BuildRequires:	ucd-snmp-devel
BuildRequires:	zlib-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
ntop is a tool that shows the network usage, similar to what the
popular top Unix command does.

%description -l pl
ntop to narzêdzie, które pokazuje u¿ycie sieci w podobny sposób jak
robi to popularna Unixowa komenda top.

%prep
%setup -q -n %{name}-current
cd %{name}*
rm -f missing ltconfig
%patch0 -p1
%patch2 -p1
cd ../gdchart*
%patch1 -p1

%build
cd gdchart*
rm -rf gd-* zlib-*
libtoolize --copy --force
aclocal
autoconf
%configure
%{__make}

cd ../%{name}*
mv -f acinclude.m4.in acinclude.m4
libtoolize --copy --force
aclocal
autoconf
automake -a -c -i
%configure \
	--with-gdchart-root=../gdchart0.94c \
	--with-ossl-root=%{_prefix} \
	--enable-tcpwrap \
	--with-gnu-ld \
	--localstatedir=%{_var}/%{ntop}
	
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
cd %{name}*
install -d	$RPM_BUILD_ROOT%{_var}/%{name}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT
	
mv $RPM_BUILD_ROOT%{_bindir}/*.pem	$RPM_BUILD_ROOT%{_datadir}/%{name}

gzip -9nf AUTHORS NEWS README THANKS

%clean
rm -rf $RPM_BUILD_ROOT

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc */*.gz
%dir %{_var}/%{name}
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_libdir}/lib*.so.*.*.*
%attr(755,root,root) %{_libdir}/lib*.la
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/plugins
%attr(755,root,root) %{_libdir}/%{name}/plugins/*.so*
%attr(755,root,root) %{_libdir}/%{name}/plugins/*.la
%{_datadir}/%{name}
%{_mandir}/man*/*
