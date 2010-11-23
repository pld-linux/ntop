# TODO
# - see if it uses system files for ettercap and geoip, ieee-oui files we did not package
# - see where plugins are needed in plugin dir or in system dir
# - fix init script (--redirdfs is bogus?)
#
# Conditional build:
%bcond_with	mysql	# with mysql support

Summary:	Network monitoring tool
Summary(pl.UTF-8):	Narzędzie do monitorowania sieci
Name:		ntop
Version:	4.0.3
Release:	0.1
License:	GPL v3+
Group:		Networking
Source0:	http://downloads.sourceforge.net/ntop/%{name}-%{version}.tgz
# Source0-md5:	f064393a2090e5bda102cd49c2707789
Source1:	%{name}.init
Source2:	%{name}.sysconfig
# http://ettercap.cvs.sourceforge.net/ettercap/ettercap_ng/share/etter.finger.os?rev=HEAD
Source3:	etter.finger.os
Patch0:		%{name}-conf.patch
Patch1:		%{name}-config.patch
Patch2:		%{name}-am.patch
Patch3:		%{name}-lua_wget.patch
Patch4:		%{name}-http_c.patch
Patch5:		%{name}-running-user.patch
Patch6:		ieee-oui.patch
Patch7:		%{name}-install.patch
Patch8:		%{name}-no_wget_etter.patch
URL:		http://www.ntop.org/
BuildRequires:	GeoIP-devel
BuildRequires:	autoconf
BuildRequires:	automake >= 1.6
BuildRequires:	gawk
BuildRequires:	gd-devel >= 2.0.1
BuildRequires:	gdbm-devel >= 1.8.3
BuildRequires:	gdome2-devel
BuildRequires:	glib2-devel
BuildRequires:	libdbi-devel
BuildRequires:	libevent-devel >= 1.4.0
BuildRequires:	libpcap-devel
BuildRequires:	libpng-devel
BuildRequires:	libtiff-devel
BuildRequires:	libtool
BuildRequires:	libwrap-devel
BuildRequires:	lua51-devel
BuildRequires:	ncurses-devel >= 5.2
BuildRequires:	net-snmp-devel
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	perl-devel
BuildRequires:	readline-devel >= 4.2
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
Requires:	ieee-oui
Requires:	rc-scripts >= 0.4.2.8
# maybe is optional, needs checking
Suggests:	GeoIP-db-City
Suggests:	GeoIP-db-IPASNum
Suggests:	ettercap
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
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1

gzip -9c %{SOURCE3} >etter.finger.os.gz

# taken from autogen.sh
cp -f %{_aclocaldir}/libtool.m4 libtool.m4.in
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
	--enable-snmp \
	%{?with_mysql:--enable-mysql}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_localstatedir}/ntop/rrd,/etc/{rc.d/init.d,sysconfig},%{_sbindir}}

%{__make} install \
	GEOIP_FILES= \
	OUI_FILES= \
	ETTER_PASSIVE= \
	DESTDIR=$RPM_BUILD_ROOT

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ntop
cp -a %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/ntop
cp -a packages/RedHat/ntop.conf.sample $RPM_BUILD_ROOT%{_sysconfdir}/ntop.conf

# these are identical files according to find-debuginfo
for p in icmpPlugin lastSeenPlugin netflowPlugin cpacketPlugin rrdPlugin sflowPlugin; do
	ln -snf ../../lib$p-%{version}.so $RPM_BUILD_ROOT%{_libdir}/ntop/plugins/$p.so
done

ln -s %{_datadir}/oui.txt $RPM_BUILD_ROOT%{_sysconfdir}/ntop/oui.txt

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
%attr(750,root,ntop) %dir %{_sysconfdir}/ntop
%attr(640,root,ntop) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ntop/ntop-cert.pem
%attr(640,root,ntop) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ntop/oui.txt
%attr(640,root,ntop) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ntop/specialMAC.txt.gz
%attr(660,root,ntop) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ntop.conf
%attr(754,root,root) /etc/rc.d/init.d/ntop
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/ntop
%attr(755,root,root) %{_sbindir}/ntop
%attr(755,root,root) %{_libdir}/lib*.so
%attr(755,root,root) %{_datadir}/%{name}
%dir %{_libdir}/%{name}
%attr(755,root,root) %{_libdir}/%{name}/plugins
%{_mandir}/man8/ntop.8*

%attr(770,root,ntop) %dir %{_localstatedir}/ntop
%attr(770,root,ntop) %dir %{_localstatedir}/ntop/rrd
