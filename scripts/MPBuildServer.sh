#!/bin/bash
#
# ----------------------------------------------------------------------------
# Script: MPBuildServer.sh
# Version: 3.0.0
#
# Description:
# This is a very simple script to demonstrate how to automate
# the build process of the MacPatch Server.
#
# Info:
# Simply modify the GITROOT and BUILDROOT variables
#
# History:
# 1.4: 		Remove Jetty Support
#			Added Tomcat 7.0.57
# 1.5:		Added Tomcat 7.0.63
# 1.6:		Variableized the tomcat config
#			removed all Jetty refs
# 1.6.1: 	Now using InstallPyMods.sh script to install python modules
# 1.6.2:	Fix cp paths
# 1.6.3:	Updated OpenJDK to 1.8.0
# 1.6.4:	Updated to install Ubuntu packages
# 1.6.5:	More ubuntu updates
# 2.0.0:	Apache HTTPD removed
#			Single Tomcat Instance, supports webservices and console
# 2.0.1:	Updated java version check
# 2.0.2:	Updated linux package requirements
# 2.0.3:	Added Mac PKG support
# 2.0.4:	Added compile for Mac MPServerAdmin.app
#			Removed create archive (aka zip)
# 2.0.5     Disabled the MPServerAdmin app build, having issue 
#			with the launch services.
# 3.0.0     Rewritten for new Python Env
#
#
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# How to use:
#
# sudo MPBuildServer.sh, will compile MacPatch server software
#
# sudo MPBuildServer.sh -p, will compile MacPatch server
# software, and create MacPatch server pkg installer. Only for
# Mac OS X.
#
# Linux requires MPBuildServer.sh, then run the buildLinuxPKG.sh
# locates in /Library/MacPatch/tmp/MacPatch/MacPatch PKG/Linux
#
# ----------------------------------------------------------------------------


# Make Sure User is root -----------------------------------------------------

if [ "`whoami`" != "root" ] ; then   # If not root user,
   # Run this script again as root
   echo
   echo "You must be an admin user to run this script."
   echo "Please re-run the script using sudo."
   echo
   exit 1;
fi

# Script Variables -----------------------------------------------------------

platform='unknown'
unamestr=`uname`
if [[ "$unamestr" == 'Linux' ]]; then
   platform='linux'
elif [[ "$unamestr" == 'Darwin' ]]; then
   platform='mac'
fi

USELINUX=false
USERHEL=false
USEUBUNTU=false
USEMACOS=false
USESSL=false
MACPROMPTFORXCODE=true

MPBASE="/opt/MacPatch"
MPSERVERBASE="/opt/MacPatch/Server"
BUILDROOT="${MPBASE}/.build/server"
TMP_DIR="${MPBASE}/.build/tmp"
SRC_DIR="${MPSERVERBASE}/conf/src/server"
TOMCAT_SW="NA"
OWNERGRP="79:70"

# PKG Variables
MP_MAC_PKG=false
MP_SERVER_PKG_VER="1.4.0.0"
CODESIGNIDENTITY="*"
CODESIGNIDENTITYPLIST="/Library/Preferences/mp.build.server.plist"

if [[ $platform == 'linux' ]]; then
	USELINUX=true
	OWNERGRP="www-data:www-data"
	LNXDIST=`python -c "import platform;print(platform.linux_distribution()[0])"`
	if [[ $LNXDIST == *"Red"*  || $LNXDIST == *"Cent"* ]]; then
		USERHEL=true
	else
		USEUBUNTU=true
	fi

	if ( ! $USERHEL && ! $USEUBUNTU ); then
		echo "Not running a supported version of Linux."
		exit 1;
	fi

elif [[ "$unamestr" == 'Darwin' ]]; then
	USEMACOS=true
	if [ -f "$CODESIGNIDENTITYPLIST" ]; then
		CODESIGNIDENTITYALT=`defaults read ${CODESIGNIDENTITYPLIST} name`
	fi
fi

# Script Input Args ----------------------------------------------------------

usage() { echo "Usage: $0 [-p Build Mac PKG]" 1>&2; exit 1; }

while getopts "ph" opt; do
	case $opt in
		p)
			MP_MAC_PKG=true
			;;
		h)
			echo
			usage
			exit 1
			;;
		\?)
			echo "Invalid option: -$OPTARG" >&2
			echo
			usage
			exit 1
			;;
		:)
			echo "Option -$OPTARG requires an argument." >&2
			echo 
			usage
			exit 1
			;;
	esac
done

# ----------------------------------------------------------------------------
# Requirements
# ----------------------------------------------------------------------------
clear

if $USEMACOS; then
	if JHOME="$(/usr/libexec/java_home -v 2>/dev/null)"; then
	    # Do this if you want to export JAVA_HOME
	    echo "Java JDK is installed"
	else
	    echo "Did not find any version of the Java JDK installed."
	    echo "Please install the Java JDK 1.8"
	    exit 1
	fi

	if $MACPROMPTFORXCODE; then
		clear
		echo
		echo "Server Build Requires Xcode Command line tools to be installed"
		echo "and the license agreement accepted. If you have not done this,"
		echo "parts of the install will fail."
		echo 
		echo "It is recommended that you run \"sudo xcrun --show-sdk-version\""
		echo "prior to continuing with this script."
		echo
		read -p "Would you like to continue (Y/N)? [Y]: " XCODEOK
		XCODEOK=${XCODEOK:-Y}
		if [ "$XCODEOK" == "Y" ] || [ "$XCODEOK" == "y" ] ; then
			echo
		else
			exit 1
		fi
	fi
fi

# ----------------------------------------------------------------------------
# Make Sure Linux has Right User 
# ----------------------------------------------------------------------------

# Check and set os type
if $USELINUX; then
	echo
	echo "* Checking for required user (www-data)."
	echo "-----------------------------------------------------------------------"

	getent passwd www-data > /dev/null 2>&1
	if [ $? -eq 0 ]; then
		echo "www-data user exists"
	else
    	echo "Create user www-data"
		useradd -r -M -s /dev/null -U www-data
	fi
fi

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
#clear
echo
echo "* Begin MacPatch Server build."
echo "-----------------------------------------------------------------------"

# Create Build Root
if [ -d "$BUILDROOT" ]; then
	rm -rf ${BUILDROOT}
else
	mkdir -p ${BUILDROOT}	
fi	

# Create TMP Dir for builds
if [ -d "$TMP_DIR" ]; then
	rm -rf ${TMP_DIR}
else
	mkdir -p ${TMP_DIR}	
fi	

# ------------------
# Create Skeleton Dir Structure
# ------------------
func mkdirP {
	if [ ! -n "$1" ]; then
		echo "Enter a directory name"
	elif [ -d $1 ]; then
		echo "\`$1' already exists"
	else
		echo "Make dir $1"
		mkdir -p $1
	fi
}

echo
echo "* Create MacPatch server directory structure."
echo "-----------------------------------------------------------------------"
mkdirP ${MPBASE}
mkdirP ${MPBASE}/Content
mkdirP ${MPBASE}/Content/Web
mkdirP ${MPBASE}/Content/Web/clients
mkdirP ${MPBASE}/Content/Web/patches
mkdirP ${MPBASE}/Content/Web/sav
mkdirP ${MPBASE}/Content/Web/sw
mkdirP ${MPBASE}/Content/Web/tools
mkdirP ${MPSERVERBASE}/InvData/files
mkdirP ${MPSERVERBASE}/lib
mkdirP ${MPSERVERBASE}/logs

# ------------------
# Copy compiled files
# ------------------
if $USEMACOS; then
	echo
	echo "* Uncompress source files needed for build"
	echo "-----------------------------------------------------------------------"
	#cp -R ${GITROOT}/MacPatch\ Server/Server ${MPBASE}
	#cp ${MPSERVERBASE}/conf/Content/Web/tools/MPAgentUploader.app.zip /Library/MacPatch/Content/Web/tools/

	#HTTP_SW=`find "${SRC_DIR}" -name "nginx"* -type f -exec basename {} \; | head -n 1`
	PCRE_SW=`find "${SRC_DIR}" -name "pcre-"* -type f -exec basename {} \; | head -n 1`
	OSSL_SW=`find "${SRC_DIR}" -name "openssl-"* -type f -exec basename {} \; | head -n 1`

	# PCRE
	echo " - Uncompress ${PCRE_SW}"
	mkdir ${TMP_DIR}/pcre
	tar xfz ${SRC_DIR}/${PCRE_SW} --strip 1 -C ${TMP_DIR}/pcre

	# NGINX Done else where in script
	#mkdir ${TMP_DIR}/nginx
	#tar xfz ${SRC_DIR}/${HTTP_SW} --strip 1 -C ${TMP_DIR}/nginx

	# OpenSSL
	echo " - Uncompress ${OSSL_SW}"
	mkdir ${TMP_DIR}/openssl
	tar xfz ${SRC_DIR}/${OSSL_SW} --strip 1 -C ${TMP_DIR}/openssl
fi

# ------------------
# Install required packages
# ------------------
if $USELINUX; then
	echo
	echo "* Install required linux packages"
	echo "-----------------------------------------------------------------------"
	if $USERHEL; then
		# Check if needed packges are installed or install
		# "mysql-connector-python" 
		pkgs=("gcc" "gcc-c++" "python-pip" "java-1.8.0-openjdk" "java-1.8.0-openjdk-devel" "zlib-devel" "pcre-devel" "openssl-devel" "python-devel")
	
		for i in "${pkgs[@]}"
		do
			p=`rpm -qa --qf '%{NAME}\n' | grep -e ${i}$ | head -1`
			if [ -z $p ]; then
				echo "Install $i"
				yum install -y -q -e 1 ${i}
			fi
		done
	fi
fi

# ------------------
# Upgrade Python Modules/Binaries
# ------------------
echo
echo "* Upgrade/Install required python tools."
echo "-----------------------------------------------------------------------"
pip_mods=( "pip" "setuptools" "virtualenv" "pycrypto" "argparse" "biplist" "python-crontab" "python-dateutil" "requests" "six" "wheel" "mysql-connector-python-rf")
for p in "${pip_mods[@]}"
do
	echo "Installing ${p}, python module." 
	if $USELINUX; then
		pip install --quiet --upgrade --trusted-host pypi.python.org ${p}
		if [ $? != 0 ] ; then
			echo "Error installing ${p}"
		fi
	else
		if [[ ${p} == *"python-crontab"* ]]; then
			continue
		fi
		pip install --egg --quiet --no-cache-dir --upgrade ${p}
		if [ $? != 0 ] ; then
			echo "Error installing ${p}"
		fi
	fi
done

sleep 1

# ------------------
# Setup Tomcat
# ------------------
echo
echo "* Uncompress and setup Tomcat."
echo "-----------------------------------------------------------------------"

TOMCAT_SW=`find "${SRC_DIR}" -name "apache-tomcat-"* -type f -exec basename {} \; | head -n 1`	
mkdir -p "${MPSERVERBASE}/apache-tomcat"
tar xfz ${SRC_DIR}/${TOMCAT_SW} --strip 1 -C ${MPSERVERBASE}/apache-tomcat
chmod +x ${MPSERVERBASE}/apache-tomcat/bin/*
rm -rf ${MPSERVERBASE}/apache-tomcat/webapps/docs
rm -rf ${MPSERVERBASE}/apache-tomcat/webapps/examples
rm -rf ${MPSERVERBASE}/apache-tomcat/webapps/ROOT

# ------------------
# Build NGINX
# ------------------
echo
echo "* Build and configure NGINX"
echo "-----------------------------------------------------------------------"
echo "See nginx build status in ${MPSERVERBASE}/logs/nginx-build.log"
echo
NGINX_SW=`find "${SRC_DIR}" -name "nginx-"* -type f -exec basename {} \; | head -n 1`

# APR
mkdir -p ${BUILDROOT}/nginx
tar xfz ${SRC_DIR}/${NGINX_SW} --strip 1 -C ${BUILDROOT}/nginx
cd ${BUILDROOT}/nginx

if $USELINUX; then
	./configure --prefix=${MPSERVERBASE}/nginx \
	--with-http_ssl_module \
	--with-pcre \
	--user=www-data \
	--group=www-data > ${MPSERVERBASE}/logs/nginx-build.log 2>&1
else
	export KERNEL_BITS=64
	./configure --prefix=${MPSERVERBASE}/nginx \
	--without-http_autoindex_module \
	--without-http_ssi_module \
	--with-http_ssl_module \
	--with-openssl=${TMP_DIR}/openssl \
	--with-pcre=${TMP_DIR}/pcre  > ${MPSERVERBASE}/logs/nginx-build.log 2>&1
fi

make  >> ${MPSERVERBASE}/logs/nginx-build.log 2>&1
make install >> ${MPSERVERBASE}/logs/nginx-build.log 2>&1

mv ${MPSERVERBASE}/nginx/conf/nginx.conf ${MPSERVERBASE}/nginx/conf/nginx.conf.orig
if $USEMACOS; then
	cp ${MPSERVERBASE}/conf/nginx/nginx.conf.mac ${MPSERVERBASE}/nginx/conf/nginx.conf
else
	cp ${MPSERVERBASE}/conf/nginx/nginx.conf ${MPSERVERBASE}/nginx/conf/nginx.conf
fi
cp -r ${MPSERVERBASE}/conf/nginx/sites ${MPSERVERBASE}/nginx/conf/sites

perl -pi -e "s#\[SRVBASE\]#$MPSERVERBASE#g" $MPSERVERBASE/nginx/conf/nginx.conf
FILES=$MPSERVERBASE/nginx/conf/sites/*.conf
for f in $FILES
do
	#echo "$f"
	perl -pi -e "s#\[SRVBASE\]#$MPSERVERBASE#g" $f
done

# ------------------
# Link & Set Permissions
# ------------------
ln -s ${MPSERVERBASE}/conf/Content/Doc ${MPBASE}/Content/Doc
chown -R $OWNERGRP ${MPSERVERBASE}

# Admin Site - App
echo
echo "* Configuring tomcat and console app"
echo "-----------------------------------------------------------------------"

mkdir -p "${MPSERVERBASE}/conf/app/war/site"
mkdir -p "${MPSERVERBASE}/conf/app/.site"
unzip -q "${MPSERVERBASE}/conf/src/server/openbd/openbd.war" -d "${MPSERVERBASE}/conf/app/.site"

rm -rf "${MPSERVERBASE}/conf/app/.site/index.cfm"
rm -rf "${MPSERVERBASE}/conf/app/.site/manual"
cp -r "${MPSERVERBASE}"/conf/app/site/* "${MPSERVERBASE}"/conf/app/.site
cp -r "${MPSERVERBASE}"/conf/app/mods/site/* "${MPSERVERBASE}"/conf/app/.site

chmod -R 0775 "${MPSERVERBASE}/conf/app/.site"
chown -R $OWNERGRP "${MPSERVERBASE}/conf/app/.site"

jar cf "${MPSERVERBASE}/conf/app/war/site/console.war" -C "${MPSERVERBASE}/conf/app/.site" .

# Tomcat Config
MPTCCONF="${MPSERVERBASE}/conf/tomcat/server"
MPTOMCAT="${MPSERVERBASE}/apache-tomcat"
cp "${MPSERVERBASE}/conf/app/war/site/console.war" "${MPTOMCAT}/webapps"
if $USEMACOS; then
	cp "${MPTCCONF}/bin/setenv.sh.sml" "${MPTOMCAT}/bin/setenv.sh"
	cp "${MPTCCONF}/bin/launchdTomcat.sh" "${MPTOMCAT}/bin/launchdTomcat.sh"
	cp -r "${MPTCCONF}/conf/server_mac.xml" "${MPTOMCAT}/conf/server.xml"
elif $USELINUX; then
	msize=`awk '{ printf "%.2f", $2/1024/1024 ; exit}' /proc/meminfo`
	if (( $(echo "$msize <= 4" | bc -l) )); then
		cp "${MPTCCONF}/bin/setenv.sh.sml" "${MPTOMCAT}/bin/setenv.sh"
	elif (( $(echo "$msize < 8" | bc -l) )); then
		cp "${MPTCCONF}/bin/setenv.sh.med" "${MPTOMCAT}/bin/setenv.sh"
	elif (( $(echo "$msize > 8" | bc -l) )); then
		echo "Config was undetermined, using small server tomcat config."
		"${MPTCCONF}/bin/setenv.sh.lrg" "${MPTOMCAT}/bin/setenv.sh"
	else
		cp "${MPTCCONF}/bin/setenv.sh.sml" "${MPTOMCAT}/bin/setenv.sh"
	fi
	cp -r "${MPTCCONF}/conf/server_lnx.xml" "${MPTOMCAT}/conf/server.xml"
fi
cp -r "${MPTCCONF}/conf/Catalina" "${MPTOMCAT}/conf/"
cp -r "${MPTCCONF}/conf/web.xml" "${MPTOMCAT}/conf/web.xml"
chmod -R 0775 "${MPTOMCAT}"
chown -R $OWNERGRP "${MPTOMCAT}"

# Set Permissions
if $USEMACOS; then
	chown -R $OWNERGRP ${MPSERVERBASE}/logs
	chmod 0775 ${MPSERVERBASE}
	chown root:wheel ${MPSERVERBASE}/conf/LaunchDaemons/*.plist
	chmod 0644 ${MPSERVERBASE}/conf/LaunchDaemons/*.plist
fi

# ------------------------------------------------------------
# Generate self signed certificates
# ------------------------------------------------------------
#clear
echo
echo "* Creating self signed SSL certificate"
echo "-----------------------------------------------------------------------"

certsDir="${MPSERVERBASE}/etc/apacheCerts"
if [ ! -d "${certsDir}" ]; then
	mkdir -p "${certsDir}"
fi

USER="MacPatch"
EMAIL="admin@localhost"
ORG="MacPatch"
DOMAIN=`hostname`
COUNTRY="NO"
STATE="State"
LOCATION="Country"

cd ${certsDir}
OPTS=(/C="$COUNTRY"/ST="$STATE"/L="$LOCATION"/O="$ORG"/OU="$USER"/CN="$DOMAIN"/emailAddress="$EMAIL")
COMMAND=(openssl req -new -sha256 -x509 -nodes -days 999 -subj "${OPTS[@]}" -newkey rsa:2048 -keyout server.key -out server.crt)

"${COMMAND[@]}"
if (( $? )) ; then
    echo -e "ERROR: Something went wrong!"
    exit 1
else
	echo "Done!"
	echo
	echo "NOTE: It's strongly recommended that an actual signed certificate be installed"
	echo "if running in a production environment."
	echo
fi

# ------------------------------------------------------------
# Create Virtualenv
# ------------------------------------------------------------
echo
echo "* Create Virtualenv for Web services app"
echo "-----------------------------------------------------------------------"

cd "${MPSERVERBASE}/apps"
virtualenv env
source env/bin/activate
python install.py
deactivate

# ------------------
# Clean up structure place holders
# ------------------
echo
echo "* Clean up Server dirtectory"
echo "-----------------------------------------------------------------------"
find ${MPBASE} -name ".mpRM" -print | xargs -I{} rm -rf {}
rm -rf ${BUILDROOT}

# ------------------
# Set Permissions
# ------------------
if $USEMACOS; then
	echo "Setting Permissions..."
	#/Library/MacPatch/Server/conf/scripts/Permissions.sh
fi

# ------------------------------------------------------------
# Create Mac OS X, MacPatch Server PKG
# ------------------------------------------------------------
if $MP_MAC_PKG; then
	#clear
	echo
	echo "* Begin creating MacPatch Server PKG for Mac OS X..."
	echo "-----------------------------------------------------------------------"
	echo
	echo
	# ------------------
	# Clean up, pre package
	# ------------------
	rm -rf "${MPSERVERBASE}/conf/app/.site"
	find "${MPSERVERBASE}/conf/src" -name apache-tomcat-* -print | xargs -I{} rm {}
	find "${MPSERVERBASE}/conf/src" -name apr* -print | xargs -I{} rm {}
	rm -rf "${MPSERVERBASE}/conf/src/openbd"
	rm -rf "${MPSERVERBASE}/conf/src/linux"
	rm -rf "${MPSERVERBASE}/conf/init"
	rm -rf "${MPSERVERBASE}/conf/init.d"
	rm -rf "${MPSERVERBASE}/conf/systemd"
	rm -rf "${MPSERVERBASE}/conf/tomcat"

	# ------------------
	# Move Files For Packaging
	# ------------------
	PKG_FILES_ROOT_MP="${BUILDROOT}/Server/Files/Library/MacPatch"

	cp -R ${GITROOT}/MacPatch\ PKG/Server ${BUILDROOT}

	mv "${MPSERVERBASE}" "${PKG_FILES_ROOT_MP}/"
	mv "${MPBASE}/Content" "${PKG_FILES_ROOT_MP}/"

	# ------------------
	# Clean up structure place holders
	# ------------------
	echo "Clean up place holder files"
	find ${PKG_FILES_ROOT_MP} -name ".mpRM" -print | xargs -I{} rm -rf {}

	# ------------------
	# Create the Server pkg
	# ------------------
	mkdir -p "${BUILDROOT}/PKG"

	# Create Server base package
	echo "Create Server base package"
	pkgbuild --root "${BUILDROOT}/Server/Files/Library" \
	--identifier gov.llnl.mp.server \
	--install-location /Library \
	--scripts ${BUILDROOT}/Server/Scripts \
	--version $MP_SERVER_PKG_VER \
	${BUILDROOT}/PKG/Server.pkg

	# Create the final package with scripts and resources
	echo "Run product build on MPServer.pkg"
	productbuild --distribution ${BUILDROOT}/Server/Distribution \
	--resources ${BUILDROOT}/Server/Resources \
	--package-path ${BUILDROOT}/PKG \
	${BUILDROOT}/PKG/_MPServer.pkg

	# Possibly Sign the newly created PKG
	#clear
	echo
	read -p "Would you like to sign the installer PKG (Y/N)? [N]: " SIGNPKG
	SIGNPKG=${SIGNPKG:-N}
	echo

	if [ "$SIGNPKG" == "Y" ] || [ "$SIGNPKG" == "y" ] ; then
		#clear

		read -p "Please enter you sigining identity [$CODESIGNIDENTITYALT]: " CODESIGNIDENTITY
		CODESIGNIDENTITY=${CODESIGNIDENTITY:-$CODESIGNIDENTITYALT}
		if [ "$CODESIGNIDENTITY" != "$CODESIGNIDENTITYALT" ]; then
			defaults write ${CODESIGNIDENTITYPLIST} name "${CODESIGNIDENTITY}"
		fi

		echo
		echo  "Signing package..."
		/usr/bin/productsign --sign "${CODESIGNIDENTITY}" ${BUILDROOT}/PKG/_MPServer.pkg ${BUILDROOT}/PKG/MPServer.pkg
		if [ $? -eq 0 ]; then
			# GOOD
			rm ${BUILDROOT}/PKG/_MPServer.pkg
		else
			# FAILED
			echo "The signing process failed."
			echo 
			echo "Please sign the package by hand."
			echo 
			echo "/usr/bin/productsign --sign [IDENTITY] ${BUILDROOT}/PKG/_MPServer.pkg ${BUILDROOT}/PKG/MPServer.pkg"
			echo
		fi

	else
		mv ${BUILDROOT}/PKG/_MPServer.pkg ${BUILDROOT}/PKG/MPServer.pkg
	fi

	# Clean up the base package
	rm ${BUILDROOT}/PKG/Server.pkg

	# Open the build package dir
	open ${BUILDROOT}/PKG
fi

exit 0;
