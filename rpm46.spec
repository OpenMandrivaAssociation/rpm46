# Do not change this spec directly but in the svn
# $Id: rpm.spec 134789 2007-03-27 15:13:43Z nanardon $

%define lib64arches	x86_64 ppc64 sparc64

%ifarch %lib64arches
    %define _lib lib64
%else
    %define _lib lib
%endif

%if %{?apply_patches:0}%{?!apply_patches:1}
%define apply_patches %(for p in `grep '^Patch.*:' "%{_specdir}/rpm.spec" | cut -d':' -f2-`; do echo "patch -p1 -F0 -i %{_sourcedir}/$p"; done )
%endif

# Define directory which holds rpm config files, and some binaries actually
# NOTE: it remains */lib even on lib64 platforms as only one version
#       of rpm is supported anyway, per architecture
%define rpmdir %{_prefix}/lib/rpm46

%if %{?mips:0}%{?!mips:1}
%define mips		mips mipsel mips32 mips32el mips64 mips64el
%endif

%if %{?pyver:0}%{?!pyver:1}
%define pyver %(python -V 2>&1 | cut -f2 -d" " | cut -f1,2 -d".")
%endif

%if %_vendor == Mandriva
#%%define __find_requires %{rpmdir}/mandriva/find-requires %{?buildroot:%{buildroot}} %{?_target_cpu:%{_target_cpu}}
#%%define __find_requires %{rpmdir}/mandriva/find-requires %{?buildroot:%{buildroot}} %{?_target_cpu:%{_target_cpu}}
%define __find_provides /usr/lib/rpm//mandriva/find-provides
%define __find_provides /usr/lib/rpm//mandriva/find-provides
%endif

%define rpmversion 4.6.0
%define srcver %rpmversion
%define libver 4.6
%define librpmname   %mklibname rpm46_  %{libver}
%define librpmnamedevel   %mklibname -d rpm46

%define buildpython 0

%if %_vendor == Mandriva
# MDV 2007.1 builds with --hash-style=gnu by default
%define rpmsetup_version 1.34
%endif

%define builddebug 0
%{?_with_debug:%define builddebug 1}

%{?_with_python:%define buildpython 1}
%{?_without_python:%define buildpython 0}

Summary:	The RPM package management system
Name:		rpm46
Version:	%{rpmversion}
%define subrel 2
Release:	%mkrel 0
Group:		System/Configuration/Packaging
Source:		http://www.rpm.org/releases/rpm-%{libver}.x/rpm-%{srcver}.tar.bz2
# Add some undocumented feature to gendiff
Patch17:	rpm-4.4.2.2-gendiff-improved.patch
# if %post of foo-2 fails,
# or if %preun of foo-1 fails,
# or if %postun of foo-1 fails,
# => foo-1 is not removed, so we end up with both packages in rpmdb
# this patch makes rpm ignore the error in those cases
# failing %pre must still make the rpm install fail (#23677)
#
# (nb: the exit code for pretrans/posttrans & trigger/triggerun/triggerpostun
#       scripts is ignored with or without this patch)
Patch22:        rpm-4.6.0-rc1-non-pre-scripts-dont-fail.patch
# (fredl) add loging facilities through syslog
Patch31:	rpm-4.6.0-rc1-syslog.patch
# part of Backport from 4.2.1 provides becoming obsoletes bug (fpons)
# (is it still needed?)
Patch49:	rpm-4.6.0-rc1-provides-obsoleted.patch
# - force /usr/lib/rpm/manbo/rpmrc instead of /usr/lib/rpm/<vendor>/rpmrc
# - read /usr/lib/rpm/manbo/rpmpopt (not only /usr/lib/rpm/rpmpopt)
Patch64:    rpm-4.6.0-rc2-manbo-rpmrc-rpmpopt.patch
# In original rpm, -bb --short-circuit does not work and run all stage
# From popular request, we allow to do this
# http://qa.mandriva.com/show_bug.cgi?id=15896
Patch70:	rpm-4.6.0-rc1-bb-shortcircuit.patch
# http://www.redhat.com/archives/rpm-list/2005-April/msg00131.html
# http://www.redhat.com/archives/rpm-list/2005-April/msg00132.html
# is this useful? "at least erasure ordering is just as non-existent as it was in 4.4.x" says Panu
Patch71:    rpm-4.6.0-ordererase.patch
# don't conflict for doc files
# (to be able to install lib*-devel together with lib64*-devel even if they have conflicting manpages)
Patch83: rpm-4.6.0-no-doc-conflicts.patch
# Fix http://qa.mandriva.com/show_bug.cgi?id=19392
# (is this working??)
Patch84: rpm-4.4.2.2-rpmqv-ghost.patch
# Fix diff issue when buildroot contains some "//"
Patch111: rpm-check-file-trim-double-slash-in-buildroot.patch
# [Dec 2008] macrofiles from rpmrc does not overrides MACROFILES anymore
Patch114: rpm-4.6.0-rc1-read-macros_d-dot-macros.patch
# remove unused skipDir functionality that conflicts with patch124 below
Patch1124: rpm-4.6.0-rc1-revert-unused-skipDir-functionality.patch
# [pixel] without this patch, "rpm -e" or "rpm -U" will need to stat(2) every dirnames of
# files from the package (eg COPYING) in the db. This is quite costly when not in cache 
# (eg on a test here: >300 stats, and so 3 seconds after a "echo 3 > /proc/sys/vm/drop_caches")
# this breaks urpmi test case test_rpm_i_fail('gd') in superuser--file-conflicts.t,
# but this is bad design anyway
Patch124: rpm-4.6.0-rc1-speedup-by-not-checking-same-files-with-different-paths-through-symlink.patch
# [from SuSE] handle "Suggests" via RPMTAG_SUGGESTSNAME
Patch133: rpm-4.6.0-rc1-weakdeps.patch
# (from Turbolinux) remove a wrong check in case %_topdir is /RPM (ie when it is short)
Patch135: rpm-4.4.2.3-rc1-fix-debugedit.patch
# convert data in the header to a specific encoding which used in the selected locale.
Patch137: rpm-4.6.0-rc1-headerIconv.patch
Patch140: rpm-russian-translation.patch
# Mandriva does not need the (broken) ldconfig hack since it uses filetriggers
Patch141: rpm-4.6.0-rc1-drop-skipping-ldconfig-hack.patch
# without this patch, "#%define foo bar" is surprisingly equivalent to "%define foo bar"
# with this patch, "#%define foo bar" is a fatal error
Patch145: rpm-forbid-badly-commented-define-in-spec.patch
# cf http://wiki.mandriva.com/en/Rpm_filetriggers
Patch146: rpm-4.6.0-rc1-filetriggers.patch
# add two fatal errors (during package build)
Patch147: rpm-rpmbuild-check-useless-tags-in-non-existant-binary-packages.patch
# (nb: see the patch for more info about this issue)
Patch151: rpm-4.6.0-rc1-protect-against-non-robust-futex.patch
Patch152: rpm-4.6.0-rc1-fix-nss-detection.patch
Patch157: introduce-_after_setup-which-is-called-after-setup.patch
Patch158: introduce-_patch-and-allow-easy-override-when-the-p.patch
Patch159: introduce-apply_patches-and-lua-var-patches_num.patch
# fixes backported from 4.7.1, see patch files for full changelog entries
# fixes ignored Requires(pre) and (post) when they have a plain Requires counterpart
Patch161: rpm-fix-corequisites.patch
Patch162: rpm-fix-islegacyprereq.patch
# map PreReq into Requires(pre,preun) at build
Patch163: rpm-map-prereq.patch
#Patch1001: rpm-4.6.0-rc1-new-liblzma.patch
# default behaviour in rpm-jbj >= 4.4.6
Patch1005: rpm-allow-conflicting-ghost-files.patch
# (nb: see the patch for more info about this issue)
Patch1006: rpm-4.6.0-rc1-compat-PayloadIsLzma.patch
Patch1007: rpm-4.6.0-rc3-xz-support.patch
# Prevents $DOCDIR from being wiped out when using %%doc <fileinbuilddir>,
# as this breaks stuff that installs files to $DOCDIR during %%install
Patch1008: rpm-4.6.0-rc3-no_rm_-rf_DOCDIR.patch
# Exposes packagecolor tag and adds new tags from rpm5 as it otherwise will
# break when these unknown tags might be found in the rpmdb. Notice that this
# will only make rpm recognize these, not implement actual support for them..
Patch1009: rpm-4.6.0-rpm5-tags.patch
# Avoid adding Lua sources/patches twice when recursing. (backport from upstream git)
Patch1010: rpm-4.6.0-lua-add-sources-and-patches-only-once.patch
# Check chroot return code before running lua script
Patch1011: rpm-4.6.0-do-not-run-lua-scripts-when-chroot-fails.patch
# Check chroot return code before running external script
Patch1012: rpm-4.6.0-do-not-run-scripts-when-chroot-fails.patch
# Make sure files in debug packages have good default perms, fixes bug #57758
Patch1013: rpm-4.6.0-fix-debug-info-default-permissions.patch
# Remove BDB XA support to fix compilation with db 4.8 (upstream)
Patch1014: rpm-4.6.0-bdb-xa-removal.patch
# Turbolinux patches
Patch2000: rpm-4.6.0-rc1-serial-tag.patch
# re-enable "copyright" tag (Kiichiro, 2005)
Patch2001: rpm-4.6.0-rc1-copyright-tag.patch
# add writeHeaderListTofile function into rpm-python (needed by "buildman" build system) (Toshihiro, 2003)
Patch2002: rpm-4.6.0-rc1-python-writeHdlist.patch
# Crusoe CPUs say that their CPU family is "5" but they have enough features for i686.
Patch2003: rpm-4.4.2.3-rc1-transmeta-crusoe-is-686.patch
Patch2004: rpm-4.6.0-no_docs.diff
# The following patch isn't needed for Mandriva, but Turbolinux has it and it can't hurt much
#
# This patch fixes the problem when the post-scripts launched by rpm-build. 
# The post-scripts launched by rpm-build works in LANG environment. If LANG is
# other locale except C, then some commands launched by post-scripts will not
# display characters which you expected.
Patch2005: rpm-4.6.0-rc1-buildlang.patch
Patch3000: mips_macros.patch
Patch3001: fix_stack_protector_check.patch
Patch3002: mips_define_isa_macros.patch
Patch3003: rpm_arm_mips_isa_macros.patch
Patch3004: rpm_add_armv5tl.patch
Patch3005: rpm-4.6.0-CVE-2011-3378.diff

License:	GPL
BuildRequires:	autoconf >= 2.57
BuildRequires:	zlib-devel
BuildRequires:  bzip2-devel
BuildRequires:	liblzma-devel >= 4.999.6-0.alpha.5
BuildRequires:	automake >= 1.8
BuildRequires:	elfutils-devel
BuildRequires:	sed >= 4.0.3
BuildRequires:	libbeecrypt-devel
BuildRequires:	ed, gettext-devel
BuildRequires:  libsqlite3-devel
BuildRequires:  db4.8-devel
BuildRequires:  neon-devel
BuildRequires:	popt-devel
BuildRequires:	nss-devel
BuildRequires:	magic-devel
%if %_vendor == Mandriva
BuildRequires:  rpm-mandriva-setup-build %{?rpmsetup_version:>= %{rpmsetup_version}}
%endif
BuildRequires:  readline-devel
BuildRequires:	ncurses-devel
BuildRequires:  openssl-devel >= 0.9.8
BuildRequires:  lua-devel
Requires:	popt
BuildRequires:	popt-devel
# Need for doc
#BuildRequires:	graphviz
BuildRequires:	tetex
%if %buildpython
BuildRequires:	python-devel
%endif
Requires:	bzip2 >= 0.9.0c-2
Requires:	lzma
Requires:	cpio
Requires:	gawk
Requires:	glibc >= 2.1.92
Requires:	mktemp
Requires:	setup >= 2.2.0-8mdk
Requires:	rpm-manbo-setup
%if %_vendor == Mandriva
Requires:	rpm-mandriva-setup >= 1.85
%endif
Requires:	update-alternatives
Requires:	%librpmname >= %version-%release
Conflicts:	patch < 2.5
Conflicts:	menu < 2.1.5-29mdk
Conflicts:	locales < 2.3.1.1
Conflicts:	man-pages-fr < 0.9.7-16mdk
Conflicts:	man-pages-pl < 0.4-9mdk
Conflicts:	perl-URPM < 1.63-3mdv2008.0
# rpm 4.6.0 dropped support for --repackage, so urpmi-recover can not work anymore:
Conflicts:	urpmi-recover
URL:            http://rpm.org/
%define         git_url        http://rpm.org/git/rpm.git
Requires(pre):		rpm-helper >= 0.8
Requires(pre):		coreutils
Requires(postun):	rpm-helper >= 0.8
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
RPM is a powerful command line driven package management system capable of
installing, uninstalling, verifying, querying, and updating software packages.
Each software package consists of an archive of files along with information
about the package like its version, a description, etc.

%package -n %librpmname
Summary: Library used by rpm
Group:		System/Libraries

%description -n %librpmname
RPM is a powerful command line driven package management system capable of
installing, uninstalling, verifying, querying, and updating software packages.
This package contains common files to all applications based on rpm.

%package -n %librpmnamedevel
Summary:	Development files for applications which will manipulate RPM packages
Group:		Development/C
Requires:	%{name} >= %{version}-%{release}
Provides:	librpm46-devel = %version-%release
Provides:   	%{name}-devel = %version-%release

%description -n %librpmnamedevel
This package contains the RPM C library and header files.  These
development files will simplify the process of writing programs
which manipulate RPM packages and databases and are intended to make
it easier to create graphical package managers or any other tools
that need an intimate knowledge of RPM packages in order to function.

This package should be installed if you want to develop programs that
will manipulate RPM packages and databases.

%package build
Summary:	Scripts and executable programs used to build packages
Group:		System/Configuration/Packaging
Requires:	autoconf
Requires:	automake
Requires:	file
Requires:	gcc-c++
# We need cputoolize & amd64-* alias to x86_64-* in config.sub
Requires:	libtool-base >= 1.4.3-5mdk
Requires:	patch >= 2.5.9-7mdv2009.1
Requires:	make
Requires:	tar
Requires:	unzip
Requires:	elfutils
Requires:	%{name} >= %{version}-%{release}
%if %_vendor == Mandriva
Requires:	rpm-mandriva-setup-build %{?rpmsetup_version:>= %{rpmsetup_version}}
%endif

%description build
This package contains scripts and executable programs that are used to
build packages using RPM.

%if %buildpython
%package -n python-rpm
Summary:	Python bindings for apps which will manipulate RPM packages
Group:		Development/Python
Requires:	python >= %{pyver}
Requires:	%{name} >= %{version}-%{release}
Obsoletes:	rpm-python
Provides:	rpm-python = %version-%release

%description -n python-rpm
The rpm-python package contains a module which permits applications
written in the Python programming language to use the interface
supplied by RPM (RPM Package Manager) libraries.

This package should be installed if you want to develop Python
programs that will manipulate RPM packages and databases.
%endif

%prep

%setup -q -n rpm-%srcver
%apply_patches

# hardcoded crap!
for i in `find . -type f -name "*"`; do
    perl -pi -e "s|/etc/rpm/|/etc/%{name}/|g" $i
    perl -pi -e "s|/etc/rpm\b|/etc/%{name}|g" $i
    perl -pi -e "s|\\\$\\{prefix\\}/lib/rpm/|\\\$\\{prefix\\}/lib/%{name}/|g" $i
    perl -pi -e "s|\\$\\{prefix\\}/lib/rpm\b|\\$\\{prefix\\}/lib/%{name}|g" $i
    perl -pi -e "s|\\$\\(prefix\\)/src/rpm|\\$\\(prefix\\)/src/%{name}|g" $i
    perl -pi -e "s|\\$\\(varprefix\\)/lib/rpm/|\\$\\(varprefix\\)/lib/%{name}/|g" $i
    perl -pi -e "s|\\$\\(varprefix\\)/lib/rpm\b|\\$\\(varprefix\\)/lib/%{name}|g" $i
    perl -pi -e "s|\\$\\(libdir\\)/rpm/|\\$\\(libdir\\)/%{name}/|g" $i
    perl -pi -e "s|\\$\\(libdir\\)/rpm\b|\\$\\(libdir\\)/%{name}|g" $i
    perl -pi -e "s|\\$\\(includedir\\)/rpm\b|\\$\\(includedir\\)/%{name}|g" $i
    perl -pi -e "s|\@prefix@\/lib/rpm|\@prefix@\/lib/%{name}/|g" $i
    perl -pi -e "s|\\\$\\{usrprefix\\}/lib/rpm\b|\\\$\\{usrprefix\\}/lib/%{name}|g" $i
    perl -pi -e "s|\%\{_var\}/lib/rpm\"|\%\{_var\}/lib/%{name}\"|g" $i
    perl -pi -e "s|/var/lib/rpm\b|/var/lib/%{name}|g" $i
    perl -pi -e "s|/usr/lib/rpm/|/usr/lib/%{name}/|g" $i
    perl -pi -e "s|/etc/rpm/|/etc/%{name}/|g" $i
    perl -pi -e "s|/var/lock/rpm/|/var/lock/%{name}/|g" $i
    perl -pi -e "s|/lib/rpm/|/lib/%{name}/|g" $i
    perl -pi -e "s|/lib/rpm\b|/lib/%{name}|g" $i
    perl -pi -e "s|/usr/lib/rpm\b|/usr/lib/%{name}|g" $i
done

for i in `find . -type f -name "Makefile*"`; do
    # rename the libs
    for lib in librpm librpmbuild librpmdb librpmio; do
        perl -pi -e "s|${lib}\.la|${lib}46\.la|g" $i
        perl -pi -e "s|${lib}\.a|${lib}46\.a|g" $i
	perl -pi -e "s|${lib}_la_|${lib}46_la_|g" $i
    done
done

# grr...
perl -pi -e "s|\\$\\(includedir\\)/\@PACKAGE\@|\\$\\(includedir\\)/%{name}|g" Makefile*

# hmm...
mkdir -p zlib

# try to use system popt
rm -rf popt

%build

libtoolize --copy --force
aclocal
autoheader
automake --foreign --copy --force-missing
autoconf

%if %builddebug
RPM_OPT_FLAGS=-g
%endif
CFLAGS="$RPM_OPT_FLAGS -fPIC" CXXFLAGS="$RPM_OPT_FLAGS -fPIC" \
%configure \
    --disable-nls \
    --enable-sqlite3 \
    --without-javaglue \
%if %builddebug
    --enable-debug \
%endif
    --with-external-db \
%if %buildpython
    --with-python=%{pyver} \
%else
    --disable-python \
    --without-python \
%endif
    --with-glob \
    --without-selinux \
    --without-apidocs

%make

%install
rm -rf %{buildroot}

make DESTDIR=%buildroot install

%ifarch ppc powerpc
ln -sf ppc-mandriva-linux %{buildroot}%{rpmdir}/powerpc-mandriva-linux
%endif

#mv -f %{buildroot}/%{rpmdir}/rpmdiff %{buildroot}/%{_bindir}

mkdir -p %{buildroot}/var/lib/%{name}
for dbi in \
	Basenames Conflictname Dirnames Group Installtid Name Providename \
	Provideversion Removetid Requirename Requireversion Triggername \
	Packages __db.001 __db.002 __db.003 __db.004
do
    touch %{buildroot}/var/lib/%{name}/$dbi
done

test -d doc-copy || mkdir doc-copy
rm -rf doc-copy/*
ln -f doc/manual/* doc-copy/
rm -f doc-copy/Makefile*

mkdir -p %buildroot%_sysconfdir/%{name}/macros.d
cat > %buildroot%_sysconfdir/%{name}/macros <<EOF
# Put your own system macros here
# usually contains 

# Set this one according your locales
# %%_install_langs

EOF

# Get rid of unpackaged files
(cd %{buildroot};
  rm -rf .%{_includedir}/beecrypt/
  rm -f  .%{_libdir}/libbeecrypt.{a,la,so*}
  rm -f  .%{_libdir}/python*/site-packages/rpmmodule.{a,la}
  rm -f  .%{rpmdir}/{Specfile.pm,cpanflute2,cpanflute,sql.prov,sql.req,tcl.req}
  rm -f  .%{rpmdir}/{config.site,cross-build,rpmdiff.cgi}
  rm -f  .%{rpmdir}/trpm
  rm -f  .%{_bindir}/rpmdiff
  rm -rf .%{_mandir}
  rm -f  .%{_libdir}/*.a
)

# renaming voodoo magic...
mv %{buildroot}/bin/rpm %{buildroot}/bin/%{name}

pushd %{buildroot}%{_bindir}
    mv gendiff gendiff46
    mv rpm2cpio rpm2cpio46
    mv rpmgraph rpmgraph46
    mv rpmbuild rpmbuild46
    ln -snf ../../bin/rpm46 rpmdb46
    ln -snf ../../bin/rpm46 rpmquery46
    ln -snf ../../bin/rpm46 rpmsign46
    ln -snf ../../bin/rpm46 rpmverify46
    rm -f rpmdb rpmquery rpmsign rpmverify
popd

# plan b
mv %{buildroot}%{_includedir}/rpm %{buildroot}%{_includedir}/rpm46

# more renaming...
perl -pi -e "s|\<rpm/|\<rpm46/|g" %{buildroot}%{_includedir}/rpm46/*.h

rm -f %{buildroot}%{_libdir}/pkgconfig/rpm.pc
cat > %{buildroot}%{_libdir}/pkgconfig/%{name}.pc << EOF
prefix=%{_prefix}
exec_prefix=%{_prefix}
libdir=%{_libdir}
includedir=%{_includedir}
rpmhome=%{_prefix}/lib/rpm46

Cflags: -I${includedir}
Libs: -L${libdir} -lrpm46 -lrpmio46
Libs.private: -lpopt -lrt -lpthread -lsqlite3 -ldb -lbz2 -lz -lssl3 -lsmime3 -lnss3 -lsoftokn3 -lnssutil3 -lplds4 -lplc4 -lnspr4 -lpthread -ldl -llua -lm
EOF

%pre
if [ -f /var/lib/%{name}/Packages -a -f /var/lib/%{name}/packages.rpm ]; then
    echo "
You have both
	/var/lib/%{name}/packages.rpm	db1 format installed package headers
	/var/lib/%{name}/Packages		db3 format installed package headers
Please remove (or at least rename) one of those files, and re-install.
"
    exit 1
fi

/usr/share/rpm-helper/add-user %{name} $1 %{name} /var/lib/%{name} /bin/false

rm -rf /usr/lib/%{name}/*-mandrake-*

%post
## nuke __db.00? when updating to this rpm
#rm -f /var/lib/%{name}/__db.00?
#
#if [ ! -e /etc/%{name}/macros -a -e /etc/rpmrc -a -f %{rpmdir}/convertrpmrc.sh ] 
#then
#	sh %{rpmdir}/convertrpmrc.sh 2>&1 > /dev/null
#fi
#
#if [ -f /var/lib/%{name}/packages.rpm ]; then
#    /bin/chown %{name}:%{name} /var/lib/%{name}/*.rpm
#elif [ ! -f /var/lib/%{name}/Packages ]; then
#    /bin/%{name} --initdb
#fi

%postun
/usr/share/rpm-helper/del-user %{name} $1 %{name}

%clean
rm -rf %{buildroot}

%define	rpmattr %attr(0755,%{name},%{name})

%files
%defattr(-,root,root)
%doc GROUPS CHANGES doc/manual/[a-z]*
%attr(0755,rpm,rpm) /bin/%{name}
%attr(0755,%{name},%{name}) %{_bindir}/rpm2cpio46
%attr(0755,%{name},%{name}) %{_bindir}/gendiff46
%attr(0755,%{name},%{name}) %{_bindir}/rpmdb46
%attr(0755,%{name},%{name}) %{_bindir}/rpmgraph46
%attr(0755,%{name},%{name}) %{_bindir}/rpmsign46
%attr(0755,%{name},%{name}) %{_bindir}/rpmquery46
%attr(0755,%{name},%{name}) %{_bindir}/rpmverify46

%dir %{rpmdir}
%dir /etc/%{name}
%config(noreplace) /etc/%{name}/macros
%dir /etc/%{name}/macros.d
%attr(0755,%{name},%{name}) %{rpmdir}/config.guess
%attr(0755,%{name},%{name}) %{rpmdir}/config.sub
#%attr(0755,%{name},%{name}) %{rpmdir}/convertrpmrc.sh
%attr(0755,%{name},%{name}) %{rpmdir}/rpmdb_*
%attr(0644,%{name},%{name}) %{rpmdir}/macros
%attr(0755,%{name},%{name}) %{rpmdir}/mkinstalldirs
%attr(0755,%{name},%{name}) %{rpmdir}/rpm.*
%attr(0644,%{name},%{name}) %{rpmdir}/rpmpopt*
%attr(0644,%{name},%{name}) %{rpmdir}/rpmrc

%rpmattr %{rpmdir}/rpm2cpio.sh
%rpmattr %{rpmdir}/tgpg

%dir %attr(-,%{name},%{name}) %{rpmdir}/platform/
%ifarch %{ix86} x86_64
%attr(-,%{name},%{name}) %{rpmdir}/platform/i*86-*
%attr(-,%{name},%{name}) %{rpmdir}/platform/athlon-*
%attr(-,%{name},%{name}) %{rpmdir}/platform/pentium*-*
%attr(-,%{name},%{name}) %{rpmdir}/platform/geode-*
%endif
%ifarch alpha
%attr(-,%{name},%{name}) %{rpmdir}/platform/alpha*
%endif
%ifarch %{sunsparc}
%attr(-,%{name},%{name}) %{rpmdir}/platform/sparc*
%endif
%ifarch ppc powerpc
%attr(-,%{name},%{name}) %{rpmdir}/platform/ppc-*
%attr(-,%{name},%{name}) %{rpmdir}/platform/ppc32-*
%attr(-,%{name},%{name}) %{rpmdir}/platform/ppc64-*
%attr(-,%{name},%{name}) %{rpmdir}/platform/powerpc-*
%endif
%ifarch ppc powerpc ppc64
%attr(-,%{name},%{name}) %{rpmdir}/platform/ppc*series-*
%endif
%ifarch ppc64
%attr(-,%{name},%{name}) %{rpmdir}/platform/ppc-*
%attr(-,%{name},%{name}) %{rpmdir}/platform/ppc32-*
%attr(-,%{name},%{name}) %{rpmdir}/platform/ppc64-*
%endif
%ifarch ia64
%attr(-,%{name},%{name}) %{rpmdir}/platform/ia64-*
%endif
%ifarch x86_64
%attr(-,%{name},%{name}) %{rpmdir}/platform/amd64-*
%attr(-,%{name},%{name}) %{rpmdir}/platform/x86_64-*
%attr(-,%{name},%{name}) %{rpmdir}/platform/ia32e-*
%endif
%ifarch %arm
%attr(-,%{name},%{name}) %{rpmdir}/platform/armv*
%endif
%ifarch %mips
%attr(-,%{name},%{name}) %{rpmdir}/platform/mips*
%endif
%attr(-,%{name},%{name}) %{rpmdir}/platform/noarch*

%attr(0755,%{name},%{name}) %dir /var/lib/%{name}

%define	rpmdbattr %attr(0644,%{name},%{name}) %verify(not md5 size mtime) %ghost %config(missingok,noreplace)

%rpmdbattr /var/lib/%{name}/Basenames
%rpmdbattr /var/lib/%{name}/Conflictname
%rpmdbattr /var/lib/%{name}/__db.0*
%rpmdbattr /var/lib/%{name}/Dirnames
%rpmdbattr /var/lib/%{name}/Group
%rpmdbattr /var/lib/%{name}/Installtid
%rpmdbattr /var/lib/%{name}/Name
%rpmdbattr /var/lib/%{name}/Packages
%rpmdbattr /var/lib/%{name}/Providename
%rpmdbattr /var/lib/%{name}/Provideversion
%rpmdbattr /var/lib/%{name}/Removetid
%rpmdbattr /var/lib/%{name}/Requirename
%rpmdbattr /var/lib/%{name}/Requireversion
%rpmdbattr /var/lib/%{name}/Triggername

%files build
%defattr(-,root,root)
%doc CHANGES
%doc doc-copy/*
%rpmattr %{_bindir}/rpmbuild46
%rpmattr %{_prefix}/lib/%{name}/brp-*
%rpmattr %{_prefix}/lib/%{name}/check-files
%rpmattr %{_prefix}/lib/%{name}/debugedit
%rpmattr %{_prefix}/lib/%{name}/find-debuginfo.sh
%rpmattr %{_prefix}/lib/%{name}/find-lang.sh
%rpmattr %{_prefix}/lib/%{name}/find-provides
%rpmattr %{_prefix}/lib/%{name}/find-requires
%rpmattr %{_prefix}/lib/%{name}/perldeps.pl
%rpmattr %{_prefix}/lib/%{name}/perl.prov
%rpmattr %{_prefix}/lib/%{name}/perl.req
%rpmattr %{_prefix}/lib/%{name}/check-buildroot
%rpmattr %{_prefix}/lib/%{name}/check-prereqs
%rpmattr %{_prefix}/lib/%{name}/check-rpaths
%rpmattr %{_prefix}/lib/%{name}/check-rpaths-worker
%rpmattr %{_prefix}/lib/%{name}/javadeps
%rpmattr %{_prefix}/lib/%{name}/libtooldeps.sh
%rpmattr %{_prefix}/lib/%{name}/macros.perl
%rpmattr %{_prefix}/lib/%{name}/macros.php
%rpmattr %{_prefix}/lib/%{name}/macros.python
%rpmattr %{_prefix}/lib/%{name}/mono-find-provides
%rpmattr %{_prefix}/lib/%{name}/mono-find-requires
%rpmattr %{_prefix}/lib/%{name}/osgideps.pl
%rpmattr %{_prefix}/lib/%{name}/pkgconfigdeps.sh
%rpmattr %{_prefix}/lib/%{name}/rpmdiff
%rpmattr %{_prefix}/lib/%{name}/rpmdeps
#%rpmattr	%{_prefix}/lib/%{name}/trpm
%rpmattr %{_prefix}/lib/%{name}/pythondeps.sh

%if %buildpython
%files -n python-rpm
%defattr(-,root,root)
%{_libdir}/python*/site-packages/rpm
%endif

%files -n %librpmname
%defattr(-,root,root)
%{_libdir}/librpm46-%{libver}.so
%{_libdir}/librpmio46-%{libver}.so
%{_libdir}/librpmbuild46-%{libver}.so

%files -n %librpmnamedevel
%defattr(-,root,root)
%{_includedir}/rpm46
%{_libdir}/librpm46.la
%{_libdir}/librpm46.so
%{_libdir}/librpmio46.la
%{_libdir}/librpmio46.so
%{_libdir}/librpmbuild46.la
%{_libdir}/librpmbuild46.so
%{_libdir}/pkgconfig/%{name}.pc

