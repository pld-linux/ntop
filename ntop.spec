%define	snap	02-10-03
Summary:	Network monitoring tool
Summary(pl):	Narzêdzie do monitorowania sieci
Name:		ntop
Version:	2.1
Release:	0.2.%(echo %{snap} | sed -e "s/-//g")
License:	GPL
Group:		Networking
Source0:	http://snapshot.ntop.org/tgz/%{name}-%{snap}.tgz
#Patch0:	%{name}-configure.patch
Patch1:		%{name}-externallib.patch
Patch2:		%{name}-perl.patch
Patch3:		%{name}-am.patch
#Patch4:		%{name}-plugins-Makefile.patch
Patch5:		%{name}-pep-Makefile.patch
Patch6:		%{name}-Makefile.patch
URL:		http://www.ntop.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	gd-devel >= 2.0.1
BuildRequires:	gdbm-devel
BuildRequires:	libpcap-devel
BuildRequires:	libpcap-static
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
#rm -f missing ltconfig
#%patch0 -p1
%patch2 -p1
%patch3 -p1
cd ../gdchart*
%patch1 -p1
cd ../%{name}*
%patch6 -p0

cd plugins
#%patch4 -p0
cd pep
%patch5 -p0

%build
cd gdchart*
rm -rf gd-* zlib-*
%{__libtoolize}
aclocal
%{__autoconf}
%configure
%{__make}

cd ../%{name}*
#mv -f acinclude.m4.in acinclude.m4
#rm -f missing
#%{__libtoolize}
aclocal
%{__autoconf}
%{__automake}
%configure \
	--with-gdchart-root=../gdchart0.94c \
	--with-ossl-root=%{_prefix} \
	--enable-tcpwrap \
	--with-gnu-ld \
	--localstatedir=%{_var}/lib/%{name}
	

%{__make}
cd plugins

%install
rm -rf $RPM_BUILD_ROOT
cd %{name}*
install -d	$RPM_BUILD_ROOT%{_var}/lib/%{name}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

mv $RPM_BUILD_ROOT%{_bindir}/*.pem $RPM_BUILD_ROOT%{_datadir}/%{name}

%clean
#rm -rf $RPM_BUILD_ROOT

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc ntop/AUTHORS ntop/NEWS ntop/README ntop/THANKS
%dir %{_var}/lib/%{name}
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_libdir}/lib*.so
%attr(755,root,root) %{_libdir}/lib*.la
#%dir %{_libdir}/%{name}
#%dir %{_libdir}/%{name}/plugins
#%attr(755,root,root) %{_libdir}/%{name}/plugins/
#%{_datadir}/%{name}
%{_mandir}/man*/*
