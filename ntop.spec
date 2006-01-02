# TODO:
#  - service ntop init steals terminal (it doesn't finish nor background)
#  - paths wrong somewhere /var/lib/ntop/ntop is expected (should be without last path component)
#  - /var/lib/ntop/* should be %ghost
Summary:	Network monitoring tool
Summary(pl):	Narzêdzie do monitorowania sieci
Name:		ntop
Version:	3.2
Release:	0.6
License:	GPL
Group:		Networking
Source0:	http://dl.sourceforge.net/ntop/%{name}-%{version}.tgz
# Source0-md5:	cd29a876b34a7dd76555e9acd8f160bb
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-plugins_makefile.patch
Patch1:		%{name}-conf.patch
Patch2:		%{name}-nolibs.patch
Patch3:		%{name}-config.patch
Patch4:		%{name}-am.patch
URL:		http://www.ntop.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	gawk
BuildRequires:	gd-devel >= 2.0.1
BuildRequires:	gdbm-devel >= 1.8.3
BuildRequires:	libpcap-devel
BuildRequires:	libpng-devel
BuildRequires:	libtiff-devel
BuildRequires:	libtool
BuildRequires:	libwrap-devel
BuildRequires:	ncurses-devel >= 5.2
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	readline-devel >= 4.2
BuildRequires:	rpmbuild(macros) >= 1.202
BuildRequires:	zlib-devel
# for xmldump plugin (disabled as it's broken anyway - wants additional -I
# to enable, and then fails to build)
#BuildRequires:	gdome2-devel
#BuildRequires:	glib-devel
#BuildRequires:	libxml2-devel
Requires(post,postun):	/sbin/ldconfig
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	rc-scripts
Provides:	group(ntop)
Provides:	user(ntop)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_localstatedir		/var/lib/ntop

%description
ntop is a tool that shows the network usage, similar to what the
popular top Unix command does.

%description -l pl
ntop to narzêdzie, które pokazuje u¿ycie sieci w podobny sposób jak
robi to popularna uniksowa komenda top.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

# kill libtool.m4 copy
cp -f acinclude.m4.ntop acinclude.m4

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}
# "verified.awk -u" calls require gawk
%configure \
	AWK=gawk \
	--disable-static \
	--enable-i18n \
	--with-gnu-ld \
	--with-ossl-root=%{_prefix} \
	--with-tcpwrap

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_localstatedir},/etc/{rc.d/init.d,sysconfig},%{_sbindir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ntop
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/ntop
install packages/RedHat/ntop.conf.sample $RPM_BUILD_ROOT%{_sysconfdir}/ntop.conf

# no -devel
rm -f $RPM_BUILD_ROOT%{_libdir}{,/ntop/plugins}/*.la

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 120 ntop
%useradd -u 120 -d %{_localstatedir} -s /bin/false -c "ntop User" -g ntop ntop

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
%attr(770,root,ntop) %dir %{_localstatedir}
%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_libdir}/lib*.so
%attr(755,root,root) %{_datadir}/%{name}
%dir %{_libdir}/%{name}
%attr(755,root,root) %{_libdir}/%{name}/plugins
%{_mandir}/man*/*
%attr(754,root,root) /etc/rc.d/init.d/ntop
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/ntop
%attr(750,root,ntop) %dir %{_sysconfdir}/ntop
%attr(640,root,ntop) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ntop/*
%attr(644,root,ntop) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ntop.conf
