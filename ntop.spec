%define	snap	03-02-13
Summary:	Network monitoring tool
Summary(pl):	Narzêdzie do monitorowania sieci
Name:		ntop
Version:	2.1
Release:	0.7.%(echo %{snap} | sed -e "s/-//g")
License:	GPL
Group:		Networking
Source0:	http://snapshot.ntop.org/tgz/%{name}-%{snap}.tgz
Patch0:		%{name}-acam.patch
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
BuildRequires:	openssl-devel >= 0.9.7
BuildRequires:	readline-devel >= 4.2
BuildRequires:	net-snmp-devel
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
#%%patch0 -p1
cd %{name}*
%patch2 -p1
cd ../gdchart*
%patch1 -p1

%build
cd gdchart*
rm -rf gd-* zlib-*
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%configure
%{__make}

cd ../%{name}*
#mv -f acinclude.m4.in acinclude.m4
#rm -f missing
#%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--with-ossl-root=%{_prefix} \
	--with-gdchart-root=`pwd`/../gdchart0.94c \
	--enable-tcpwrap \
	--with-gnu-ld \
	--localstatedir=%{_var}/lib/%{name} || true

%configure \
	--with-ossl-root=%{_prefix} \
	--with-gdchart-root=`pwd`/../gdchart0.94c \
	--enable-tcpwrap \
	--with-gnu-ld \
	--localstatedir=%{_var}/lib/%{name}


%{__make}
cd plugins
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
cd %{name}*
install -d	$RPM_BUILD_ROOT%{_var}/lib/%{name}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

#mv $RPM_BUILD_ROOT%{_bindir}/*.pem $RPM_BUILD_ROOT%{_datadir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc ntop/AUTHORS ntop/NEWS ntop/README ntop/THANKS
%dir %{_var}/lib/%{name}
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_libdir}/lib*
#%attr(755,root,root) /usr/share/ntop/*
%attr(755,root,root) %{_datadir}/%{name}
#%{_libdir}/lib*.la
#%dir %{_libdir}/%{name}
#%dir %{_libdir}/%{name}/plugins
%attr(755,root,root) %{_libdir}/%{name}/plugins
%{_mandir}/man*/*
