# TODO
# - see if it uses system files for ettercap and geoip, ieee-oui files we did not package
# - see where plugins are needed in plugin dir or in system dir
# - unpackaged
#        /etc/ntop/GeoIPASNum.dat
#        /etc/ntop/GeoLiteCity.dat
#        /usr/lib64/libntop.a
#        /usr/lib64/libntopreport.a
# NOTE: can read oui.txt.xz if MAKE_WITH_ZLIB enabled

Summary:	Network monitoring tool
Summary(pl.UTF-8):	Narzędzie do monitorowania sieci
Name:		ntop
Version:	5.0.1
Release:	9
License:	GPL v3+
Group:		Networking
Source0:	http://downloads.sourceforge.net/ntop/%{name}-%{version}.tar.gz
# Source0-md5:	01710b6925a8a5ffe1a41b8b512ebd69
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
Patch8:		%{name}-rrdtool-1.6.0.patch
Patch9:		ac-am.patch
URL:		http://www.ntop.org/
BuildRequires:	GeoIP-devel
BuildRequires:	autoconf >= 2.52
BuildRequires:	automake >= 1.6
BuildRequires:	gawk
BuildRequires:	gdbm-devel >= 1.8.3
BuildRequires:	libpcap-devel
BuildRequires:	libtool
BuildRequires:	net-snmp-devel
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	perl-devel
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	rrdtool-devel >= 1.1.0
BuildRequires:	sed >= 4.0
BuildRequires:	zlib-devel
Requires(post,postun):	/sbin/ldconfig
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	hwdata >= 0.243-2
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
%patch -P0 -p1
%patch -P1 -p1
%patch -P2 -p1
%patch -P3 -p1
%patch -P4 -p1
%patch -P5 -p1
%patch -P6 -p1
%patch -P7 -p1
%patch -P8 -p1
%patch -P9 -p1

gzip -9c %{SOURCE3} >etter.finger.os.gz

# taken from autogen.sh
cp -f %{_aclocaldir}/libtool.m4 libtool.m4.in
cat acinclude.m4.in libtool.m4.in acinclude.m4.ntop > acinclude.m4

%{__sed} -i -e '1s,/usr/bin/env python$,%{__python},' python/sankey.py

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}

cd nDPI
%configure
%{__make}
cd ..

# "verified.awk -u" calls require gawk
%configure \
	AWK=gawk \
	--disable-static \
	--with-gnu-ld \
	--with-ossl-root=%{_prefix} \
	--enable-snmp

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

# read by checkForInputFile() scanning various dirs and extensions
ln -s /lib/hwdata/oui.txt $RPM_BUILD_ROOT%{_sysconfdir}/ntop/oui.txt

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
