#
# Conditional build:
%bcond_with	mysql	# with mysql support
#
Summary:	Network monitoring tool
Summary(pl.UTF-8):	Narzędzie do monitorowania sieci
Name:		ntop
Version:	3.3.8
Release:	0.1
License:	GPL
Group:		Networking
Source0:	http://dl.sourceforge.net/ntop/%{name}-%{version}.tar.gz
# Source0-md5:	19c6a582c285ffae18bf0c3b599d184e
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-conf.patch
Patch1:		%{name}-config.patch
Patch2:		%{name}-am.patch
URL:		http://www.ntop.org/
BuildRequires:	autoconf
BuildRequires:	automake >= 1.6
BuildRequires:	gawk
BuildRequires:	gd-devel >= 2.0.1
BuildRequires:	gdbm-devel >= 1.8.3
BuildRequires:	gdome2-devel
BuildRequires:	glib2-devel
BuildRequires:	libpcap-devel
BuildRequires:	libpng-devel
BuildRequires:	libtiff-devel
BuildRequires:	libtool
BuildRequires:	libwrap-devel
BuildRequires:	ncurses-devel >= 5.2
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	readline-devel >= 4.2
BuildRequires:	rpmbuild(macros) >= 1.202
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	rrdtool-devel >= 1.1.0
BuildRequires:	zlib-devel
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

%define		_localstatedir		/var/lib

%description
ntop is a tool that shows the network usage, similar to what the
popular top Unix command does.

%description -l pl.UTF-8
ntop to narzędzie, które pokazuje użycie sieci w podobny sposób jak
robi to popularna uniksowa komenda top.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

# taken from autogen.sh 
cp -f /usr/share/aclocal/libtool.m4 libtool.m4.in
cat acinclude.m4.in libtool.m4.in acinclude.m4.ntop > acinclude.m4

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
# "verified.awk -u" calls require gawk
%configure \
	AWK=gawk \
	--disable-static \
	--with-gnu-ld \
	--with-ossl-root=%{_prefix} \
	--with-tcpwrap \
	%{?with_mysql:--enable-mysql}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_localstatedir}/ntop/rrd,/etc/{rc.d/init.d,sysconfig},%{_sbindir}}

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
%useradd -u 120 -d %{_localstatedir}/ntop -s /bin/false -c "ntop User" -g ntop ntop

%post
/sbin/ldconfig
/sbin/chkconfig --add ntop
%service ntop restart "ntop daemon"

%preun
if [ "$1" = "0" ]; then
	%service ntop stop
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
%doc AUTHORS ChangeLog NEWS README THANKS docs/{1STRUN.txt,FAQ}
%attr(770,root,ntop) %dir %{_localstatedir}/ntop
%attr(770,root,ntop) %dir %{_localstatedir}/ntop/rrd
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
%attr(660,root,ntop) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ntop.conf
