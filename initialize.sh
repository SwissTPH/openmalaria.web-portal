#!/bin/bash

########################################################################################################################
# This documentation/script assumes the following:
# 1. centos/Fedora/RedHat 64-bit OS(use of yum, chkconfig, library versions, etc)
# 2. Apache2 (httpd) is installed and configured appropriately for the site (mod_wsgi, mod_ssl, all configured and working)
# 3. documents are being served from /var/www/html
# 4. openmalaria code resides in /var/www/openmalaria
# 5. Python 2.6 is already installed
# 6. EPEL package repository needs to be installed (see PART 0)
#
# I usually install codebase into openmalaria folder in /var/www and link openmalaria->html. Directory structure looks like:
#
#/var/
#   www/
#       cgi-bin/        <- not used/modified
#       error/        <- not used/modified
#       html/           <- sym link to "openmalaria" directory at same level
#       icons/          <- not used/modified
#       openmalaria/    <- code base root folder (html links to this folder)
#           frontend/
#               fixtures/   <- initial model info to be loaded
#                   initial_fixtures.json   <- Loaded when syncdb command is run!
#           initialize.sh  <- this file
#           OpenMalaria/
#               settings.py            <- modified in part 0! used in part 6!
#               static/
#                   code/
#                       densities.csv   <- necessary file to run openmalaria app. copied in part 5!
#                       openMalaria     <- openmalaria app (binary). copied in part 5! Overwritten in step 2!
#                       scenario_30.xsd <- scenario schema definition. copied in part 5!
#
# NOTE! Other directories and files omitted (but also necessary).
# NOTE! Parts 1-3 are commented out (intended to be a step-by-step tutorial not part of the initialization script
#   because many pieces may be installed already or installed using different means. This is just how I set it all up.
#   In particular, the build/installation of OpenMalaria
#
########################################################################################################################
# PART 0 - Prepare before you run this script.
########################################################################################################################
# edit /var/www/openmalaria/OpenMalaria/settings.py
#   change database parameters (if necessary). This rest of this script assumes that db parameters will be exactly what is shown.
#   change the email parameters (host, port, etc). These must be supplied to use the password reset functionality of the site!!!

# edit /var/www/openmalaria/WorkerPackage/Task/settings.py
#   change host to the database host FQDN
#   change BROKERURL host to the FQDN of the webserver (which will be running rabbitMQ).

#You need to change the initialization fixtures to use the domain
#name where this site will be running. Inside the root folder of OpenMalaria, edit frontend/fixtures/post_syncdb.json

#At the top of this file, you'll find:
#    {
#        "model": "django.site",
#        "pk": 1,
#        "fields": {
#            "name": "<Some default value>",
#            "domain": "<Some default value>"
#        }
#    },

#Change <Some default value> to the host and domain for the site (includng the port number if not 80 or 443). For example
#if the site is being hosted at www.mygreatdomain.com then the django.site fields should be:
#    {
#        "model": "django.site",
#        "pk": 1,
#        "fields": {
#            "name": "www.mygreatdomain.com",
#            "domain": "www.mygreatdomain.com"
#        }
#    },
#Setting the correct domain is critical to the password reset functionality (the rest of the site ignores this).



# edit the BOINC path!!!
# The BOINC settings found in settings.py were developed primarily to allow job submission to STPHI's BOINC server.
# BOINC_[HOST/USER/PASSWORD] settings should be changed accordingly

#Add the EPEL package repository so yum can locate many of the.  Assuming a 64-bit Redhat or Centos 6.x OS...
#In your home directory type the following two lines
#wget http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm;
#sudo rpm -Uvh epel-release-6*.rpm;
#rm epel-release-6*.rpm;

########################################################################################################################
# PART 1 - must install a bunch of yum/pip/rpm packages first!
########################################################################################################################
#Now, install the gcc developer tools (so other packages can be compiled by pip-python later)
#yum groupinstall "Development Tools"

#Then install postgresql stuff, python-devel packages, RabbitMQ and packages needed to build OpenMalaria from source
#yum install postgresql postgresql-server postgresql-devel python-devel python-pip rabbitmq-server
#yum install gsl gsl-devel xerces-c xerces-c-devel boost boost-devel cmake zlib-devel java-1.7.0-openjdk java-1.7.0-openjdk-devel

#python packages (don't use yum for these) to install. The command may be "pip" (if built from source) or "pip-python" (if installed by yum)
#pip-python install requests psycopg2 celery django-celery lxml;

#install xsd library
#wget -O /tmp/xsd.rpm http://codesynthesis.com/download/xsd/3.3/linux-gnu/x86_64/xsd-3.3.0-1.x86_64.rpm
#rpm -ivh /tmp/xsd.rpm
#clean up the tmp file (optional)
#rm -f /tmp/xsd.rpm

########################################################################################################################
# PART 2 - build OpenMalaria executable
########################################################################################################################
#svn checkout http://openmalaria.googlecode.com/svn/trunk/ openmalaria-executable;
#cd openmalaria-executable;
#mkdir build;

##### WARNING: THE FOLLOWING MUST BE DONE MANUALLY BEFORE CONTINUING THE REST OF STEP #1
# edit /var/www/html/openmalaria-executable/FindXERCESC.cmake
#   add the line the path: /usr/lib64
#   after PATHS ${CMAKE_SOURCE_DIR}/lib (approximately line 22-23)
#
# edit /var/www/html/openmalaria-executable/FindXERCESC.cmake
#   add the line the path: /usr/lib64
#   after PATHS ${CMAKE_SOURCE_DIR}/lib ${CMAKE_SOURCE_DIR}/../gsl/lib (approximately line 45-46)
#
# edit /var/www/html/openmalaria-executable/FindZ.cmake
#   add the line the path: /usr/lib64
#   ${CMAKE_SOURCE_DIR}/../zlib/projects/visualc6/Win32_LIB_Release (approximately line 23-24)
#
# edit /var/www/html/openmalaria-executable/CMakeLists.txt
#   add: /usr/lib64
#   to the end of the list PTHREAD library list (approximately line 199)
#   ie. change:
#       find_library (PTHREAD_LIBRARIES pthread PATHS ${CMAKE_SOURCE_DIR}/lib /usr/lib /usr/local/lib)
#   to:
#       find_library (PTHREAD_LIBRARIES pthread PATHS ${CMAKE_SOURCE_DIR}/lib /usr/lib /usr/local/lib /usr/lib64)
##### END WARNING ########

# Assuming your're in the openmalaria-executable directory, configure the building of OpenMalaria executable
#cd build;
#cmake ..;
#make;

# At this point, you should have a built version of the OpenMalaria executable to the current host to use.
#cp ./openMalaria ../../OpenMalaria/static/code



########################################################################################################################
# PART 3 - set up the database and user
########################################################################################################################
#First set postgresql to start up when machine boots
#chkconfig postgresql on;

#Initialize postgresql and start the server
#service postgresql initdb;
#service postgresql start;

# Create the OpenMalaria database and user
#su - postgres;
#createdb "OpenMalaria" -U postgres;
#psql -U postgres -c "create user openmalaria with password 'openmalaria';";
#psql -U postgres -c "grant all privileges on database \"OpenMalaria\" to openmalaria;";
#exit;

########################################################################################################################
# PART 4 - setup RabbitMQ
########################################################################################################################
#chkconfig rabbitmq-server on;
#service rabbitmq-server start;


########################################################################################################################
# PART 5 - Set up the required directories and copy the openmalaria executable for server-side validation of XML files
########################################################################################################################
echo "ALERT!!! ###############################################################"
echo "This script only performs the final two steps of a much larger sequence."
echo "Running this script, it is assumed that the server and required software"
echo "is already installed and configured. Thus running this script directly"
echo "is only intended to 'stand-up' the django site and enter the default"
echo "database content required to use the site. If you have not performed the"
echo "other steps prior to running this, bad things can happen (site won't"
echo "work). The prerequisite steps are outlined in the text of this script."

read -p "Are you sure you want to continue' (y/n)?"
[ "$REPLY" != "y" ] || exit;

echo "Performing Step 5..."
#Create the omdata directory if it doesn't exist
if [ ! -d "/omdata" ]; then
    echo "Creating /omdata"
    mkdir /omdata;
    chmod a+rwx /omdata;
fi

#Create the omdata/validation directory if it doesnt' exist
if [ ! -d "/omdata/validation" ]; then
    echo "Creating /omdata/validation"
    mkdir /omdata/validation;
    chmod a+rwx /omdata/validation;
fi
#Copy the two required files into the validation directory
echo "Copying densities.csv to /omdata/validation"
cp ./OpenMalaria/static/code/densities.csv /omdata/validation/
echo "Copying scenario_30.xsd to /omdata/validation"
cp ./OpenMalaria/static/code/scenario_30.xsd /omdata/validation/
chmod a+r /omdata/validation/*

#Create the omdata/build directory if it doesnt' exist
if [ ! -d "/omdata/build" ]; then
    echo "Creating /omdata/build"
    mkdir /omdata/build;
    chmod a+rwx /omdata/build;
fi
echo "Copying openMalaria executable to /omdata/build"
cp ./OpenMalaria/static/code/openMalaria /omdata/build/
chmod a+x /omdata/build/*

########################################################################################################################
# PART 6 - initialize django and setup this website!
########################################################################################################################
echo "Performing step 6..."
#Run the syncdb command to create the tables.
echo "Running syncdb"
python manage.py syncdb;

echo "Restarting web server"
service httpd restart;
