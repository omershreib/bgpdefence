BGPDefence - Israel Open University Network Seminar Project (Summer 2025)
=========================================================================


Github URL: https://github.com/omershreib/bgpdefence

Lab was tested on GNS3 lab version 2.2.54 (important! both GNS3 VM Server and GNS3 application must be with the same version!)

check the GNS3 labs in the gns3lab folder:
	
	lab1 - with malicious device 		(required extra hardware)
	lab2 - without malicious device


in order to open one of these labs in GNS3, open GNS3 and go to file > import portable project

code was tested on python version 3.12.1

python requirements can be fulfilled by typing "pip install -r requirements.txt" in your project virtual environment.

Then the code can be simply run by typing "python main.py"

Tests:
======
All local tests can be run by "python tests/main.py"
Global tests (there are 2, one in "real" and one is mocked and used to check the GUI, less the backend)
can be run as follows:
    python tests/global_test.py
    python tests/global_mocked_test.py

please go over the installation chapter (written in the PDF project report file) before running this project. 


GNS3 Network Lab Troubleshooting:
=================================

1. cannot communicate with the lab:
	
	open CMD as Administrator and add these static routes to your system
  	(do not worry, all these configuration will erased by restart)

	ROUTE ADD 198.18.1.0 MASK 255.255.255.0 192.0.0.254
	ROUTE ADD 203.0.113.0 MASK 255.255.255.0 192.0.0.254

	also, make sure that your Ethernet loobpack adapter is configured properly as written in the project report.

	if this not solve the problem, you might need to temporarly disable firewall or anti-virus...


2. FTP Server is not working:
	
	connect via console to toolbox-ftp-1 and type these following linux command:

	# check if ftpuser exists
	grep ftpuser /etc/passwd

	# check if ftpuser home directory exists
	ls -ld /home /home/ftpuser


	# if not, create this directory
	mkdir -p /home/ftpuser
	

	# next, fix directory permissions
	chown ftpuser:ftpuser /home/ftpuser
	chmod 755 /home
	chmod 755 /home/ftpuser
	
	
	# edit /etc/vsftpd.conf (using nano or vi, does not matter)
	# ensure that these configuration lines exist in the file
	chroot_local_user=YES
	allow_writeable_chroot=YES
	

	# finally, restart vsftpd service
	service vsftpd restart


3. MaliciousDevice blocks communication between ISP1 and ISP2:

	this means that the rasberry pi's bridge is not properly configured
	bridge configuration is as follows:

	sudo ip link add name br0 type bridge
	sudo ip link set eth0 master br0
	sudo ip link set eth1 master br0
	sudo ip link set br0 up

	# type ifconfig to check interfaces status (make sure that all the interfaces are Up)
	
	also, make sure that your Ethernet phisical adapter is configured properly as written in the project report. 
 

	
	