%define	snap	03-02-13
Summary:	Network monitoring tool
Summary(pl):	Narzêdzie do monitorowania sieci
Name:		ntop
Version:	2.2
Release:	0.2
License:	GPL
Group:		Networking
Source0:	http://snapshot.ntop.org/tgz/%{name}-%{version}.tgz
# Source0-md5:	4586e4173fcab64d2394502603fc73aa
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.conf
Patch0:		%{name}-acam.patch
Patch1:		%{name}-externallib.patch
Patch2:		%{name}-perl.patch
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
BuildRequires:	openssl-devel >= 0.9.7c
BuildRequires:	readline-devel >= 4.2
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

%description
ntop is a tool that shows the network usage, similar to what the
popular top Unix command does.

%description -l pl
ntop to narzêdzie, które pokazuje u¿ycie sieci w podobny sposób jak
robi to popularna Unixowa komenda top.

%prep
%setup -q
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
#%%{__libtoolize}
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
install -d	$RPM_BUILD_ROOT{%{_var}/lib/%{name},/etc/{rc.d/init.d,sysconfig}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

#mv $RPM_BUILD_ROOT%{_bindir}/*.pem $RPM_BUILD_ROOT%{_datadir}/%{name}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ntop
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/ntop
install %{SOURCE3} $RPM_BUILD_ROOT/etc/ntop.conf

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
%doc ntop/AUTHORS ntop/NEWS ntop/README ntop/THANKS ntop/docs/1STRUN.TXT ntop/docs/FAQ
%dir %{_var}/lib/%{name}
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_libdir}/lib*
#%attr(755,root,root) /usr/share/ntop/*
%attr(755,root,root) %{_datadir}/%{name}
#%%{_libdir}/lib*.la
#%dir %{_libdir}/%{name}
#%dir %{_libdir}/%{name}/plugins
%attr(755,root,root) %{_libdir}/%{name}/plugins
%{_mandir}/man*/*
%attr(754,root,root) /etc/rc.d/init.d/ntop
%attr(640,root,root) /etc/sysconfig/ntop
%attr(644,ntop,ntop) /etc/ntop.conf
