# TODO:
#  - duplicate configure. remove or write down reason.
#  - configure appears to need gawk
#  - service ntop init steals terminal (it doesnt finish nor background)
#  - paths wrong somewhere /var/lib/ntop/ntop is expected (should be without last path component)
#  - /var/lib/ntop/* should be %ghost
#  - .la files should be in -devel
#  - ntop apperars to be daemon, so it should be in _sbindir not in _bindir
#
Summary:	Network monitoring tool
Summary(pl):	Narzêdzie do monitorowania sieci
Name:		ntop
Version:	3.1
Release:	0.2
License:	GPL
Group:		Networking
Source0:	http://dl.sourceforge.net/ntop/%{name}-%{version}.tgz
# Source0-md5:	1c9b4097c2e464b84f2fe8f6626d2b06
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch1:		%{name}-plugins_makefile.patch
Patch2:		%{name}-conf.patch
Patch3:		%{name}-DESTDIR.patch
URL:		http://www.ntop.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	gd-devel >= 2.0.1
BuildRequires:	gdbm-devel >= 1.8.3
BuildRequires:	libpcap-devel
BuildRequires:	libpng-devel
BuildRequires:	libtiff-devel
BuildRequires:	libwrap-devel
BuildRequires:	libtool
BuildRequires:	ncurses-devel >= 5.2
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	readline-devel >= 4.2
BuildRequires:	rpmbuild(macros) >= 1.202
BuildRequires:	zlib-devel
PreReq:		rc-scripts
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Requires(post,postun):	/sbin/ldconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Provides:	group(ntop)
Provides:	user(ntop)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
ntop is a tool that shows the network usage, similar to what the
popular top Unix command does.

%description -l pl
ntop to narzêdzie, które pokazuje u¿ycie sieci w podobny sposób jak
robi to popularna uniksowa komenda top.

%prep
%setup -q -n %{name}
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
#mv -f acinclude.m4.in acinclude.m4
#rm -f missing
#%%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--with-ossl-root=%{_prefix} \
	--with-gdchart-root=`pwd`/../gdchart0.94c \
	--enable-tcpwrap \
	--with-gnu-ld \
	--enable-i18n \
	--enable-showoses \
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
install -d	$RPM_BUILD_ROOT{%{_var}/lib/%{name},/etc/{rc.d/init.d,sysconfig}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ntop
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/ntop
install packages/RedHat/ntop.conf.sample $RPM_BUILD_ROOT/etc/ntop.conf

mv $RPM_BUILD_ROOT%{_libdir}/lib*Plugin*.so $RPM_BUILD_ROOT%{_libdir}/%{name}/plugins
rm $RPM_BUILD_ROOT%{_libdir}/*.a

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 120 ntop
%useradd -u 120 -d /var/lib/ntop -s /bin/false -c "ntop User" -g ntop ntop

%post
/sbin/ldconfig
/sbin/chkconfig --add ntop
if [ -f /var/lock/subsys/ntop ]; then
	/etc/rc.d/init.d/ntop restart >&2
else
	echo "Run \"/etc/rc.d/init.d/ntop start\" to start ntop daemon." >&2
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/ntop ]; then
		/etc/rc.d/init.d/ntop stop 1>&2
	fi
	/sbin/chkconfig --del ntop
fi

%postun
/sbin/ldconfig
if [ "$1" = "0" ]; then
	%userremove ntop
	%groupremove ntop
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS README THANKS
%attr(770,root,ntop) %dir %{_var}/lib/%{name}
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_libdir}/lib*
%attr(755,root,root) %{_datadir}/%{name}
%dir %{_libdir}/%{name}
%attr(755,root,root) %{_libdir}/%{name}/plugins
%{_mandir}/man*/*
%attr(754,root,root) /etc/rc.d/init.d/ntop
%attr(640,root,root) /etc/sysconfig/ntop
%attr(750,root,ntop) %dir /etc/ntop
%attr(640,root,ntop) %config(noreplace) %verify(not size mtime md5) /etc/ntop/*
%attr(644,root,ntop) %config(noreplace) %verify(not size mtime md5) /etc/ntop.conf
