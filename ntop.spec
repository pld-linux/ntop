Summary:	Network monitoring tool
Summary(pl):	Narzêdzie do monitorowania sieci
Name:		ntop
Version:	1.3.2
Release:	1
License:	GPL
Group:          Networking
Group(pl):      Sieciowe
Source0:	ftp://ftp.ntop.org/pub/local/ntop/snapshots/%{name}-src-Oct-26-2000.tar.gz
Patch0:		ntop-configure.patch
URL:		http://www.ntop.org/
BuildRequires:	libpcap-devel
BuildRequires:	libwrap-devel
BuildRequires:	ncurses-devel
BuildRequires:	readline-devel
BuildRequires:	openssl-devel
BuildRequires:	tar
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
ntop is a tool that shows the network usage, similar to what the
popular top Unix command does.

%description -l pl
ntop to narzêdzie, które pokazuje u¿ycie sieci w podobny sposób
jak robi to popularna Unixowa komenda top.

%prep
%setup -q -c
tar xzf %{name}-*.tar.gz
cd %{name}-%{version}
%patch0 -p1

%build
cd %{name}-%{version}
libtoolize --copy --force
aclocal && autoheader && automake --add-missing --gnu && autoconf
%configure \
	--enable-ssl \
	--enable-readline \
	--enable-curses \
	--enable-tcpwrap \
	--enable-plugins \
	--enable-intop \
	--enable-ri \
	--disable-mt
	
%{__make}

%install
cd %{name}-%{version}
rm -rf $RPM_BUILD_ROOT

%{__make} install DESTDIR=$RPM_BUILD_ROOT
gzip -9nf AUTHORS FAQ KNOWN_BUGS NEWS README THANKS TODO

%clean
#rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc *.gz
%attr(755,root,root) %{_bindir}/*
%{_mandir}/man*/*
