Summary:	Network monitoring tool
Summary(pl):	Narzêdzie do monitorowania sieci
Name:		ntop
Version:	2.2.95
Release:	0.1
License:	GPL
Group:		Networking
Source0:	http://dl.sourceforge.net/ntop/%{name}-%{version}.tgz
# Source0-md5:	d2748c4b5be0393495ea4dd839513dc1
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.conf
Patch0:		%{name}-rrd.patch
Patch1:		%{name}-opt.patch
URL:		http://www.ntop.org/
BuildRequires:	autoconf >= 2.52
BuildRequires:	automake >= 1.6
BuildRequires:	gd-devel >= 2.0.1
BuildRequires:	gdbm-devel >= 1.8.3
BuildRequires:	libpcap-devel
BuildRequires:	libpng-devel
BuildRequires:	libtiff-devel
BuildRequires:	libwrap-devel
BuildRequires:	libtool
BuildRequires:	ncurses-devel >= 5.2
BuildRequires:	openssl-devel >= 0.9.7c
BuildRequires:	readline-devel >= 4.2
BuildRequires:	rrdtool-devel >= 1.1.0
BuildRequires:	zlib-devel
PreReq:		rc-scripts
Requires(pre):	/usr/bin/getgid
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Requires(post,postun):	/sbin/ldconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_localstatedir		%{_var}/lib/%{name}

%description
ntop is a tool that shows the network usage, similar to what the
popular top Unix command does.

%description -l pl
ntop to narzêdzie, które pokazuje u¿ycie sieci w podobny sposób jak
robi to popularna Unixowa komenda top.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

cp -f acinclude.m4.ntop acinclude.m4

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--disable-static \
	--enable-i18n \
	--enable-tcpwrap \
	--with-gnu-ld \
	--with-ossl-root=/usr

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_var}/lib/%{name}/rrd,/etc/{rc.d/init.d,sysconfig}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

#mv $RPM_BUILD_ROOT%{_bindir}/*.pem $RPM_BUILD_ROOT%{_datadir}/%{name}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ntop
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/ntop
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/ntop.conf

# these files belong to %{_libdir}/ntop/plugins
rm -f $RPM_BUILD_ROOT%{_libdir}/lib*Plugin*
# useless - there is no public headers now
rm -f $RPM_BUILD_ROOT%{_libdir}/libntop{,report}.{la,so}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`getgid ntop`" ]; then
        if [ "`getgid ntop`" != "120" ]; then
                echo "Error: group ntop doesn't have gid=120. Correct this before installing ntop." 1>&2
                exit 1
        fi
else
        /usr/sbin/groupadd -g 120 -r -f ntop
fi
if [ -n "`id -u ntop 2>/dev/null`" ]; then
        if [ "`id -u ntop`" != "120" ]; then
                echo "Error: user ntop doesn't have uid=120. Correct this before installing ntop." 1>&2
                exit 1
        fi
else
        /usr/sbin/useradd -u 120 -r -d /var/lib/ntop -s /bin/false -c "ntop User" -g ntop ntop 1>&2
fi

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
        /usr/sbin/userdel ntop
        /usr/sbin/groupdel ntop
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS NEWS README THANKS docs/{1STRUN.txt,FAQ}
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_libdir}/lib*.so
%attr(755,root,root) %{_datadir}/%{name}
%dir %{_libdir}/%{name}
%attr(755,root,root) %{_libdir}/%{name}/plugins
%attr(750,root,ntop) %dir %{_var}/lib/%{name}
%attr(770,root,ntop) %dir %{_var}/lib/%{name}/rrd
%{_mandir}/man*/*
%attr(754,root,root) /etc/rc.d/init.d/ntop
%attr(640,root,root) /etc/sysconfig/ntop
%attr(660,root,ntop) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/ntop.conf
