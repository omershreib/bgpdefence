import paramiko
from ftplib import FTP
import os


# === Router connection details ===
ROUTER_IP = "203.0.113.254"
ROUTER_USER = "local_isp"
ROUTER_PASS = "051295"

# === FTP server details ===
FTP_SERVER = "203.0.113.1"
FTP_USER = "ftpuser"
FTP_PASS = "vbnWgoEbHUzapEGD1KYP"
FTP_FILENAME = "bgp_table.txt"

# === Temporary local file ===
LOCAL_FILENAME = "bgp_output.txt"

def get_bgp_output():
    """Connect to router via SSH and run 'show ip bgp'."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ROUTER_IP, username=ROUTER_USER, password=ROUTER_PASS)

    stdin, stdout, stderr = ssh.exec_command("show ip bgp")
    output = stdout.read().decode()
    ssh.close()

    # Save to local file
    with open(LOCAL_FILENAME, "w") as f:
        f.write(output)

    return LOCAL_FILENAME

def upload_to_ftp(filename):
    """Upload file to FTP server."""
    ftp = FTP(FTP_SERVER)
    ftp.login(user=FTP_USER, passwd=FTP_PASS)

    with open(filename, "rb") as f:
        ftp.storbinary(f"STOR {FTP_FILENAME}", f)

    ftp.quit()

    # with pysftp.Connection(host=myHostname, username=myUsername, password=myPassword, cnopts=cnopts) as sftp:
    #     print("Connection succesfully stablished ... ")
    #     sftp.put(filename)

if __name__ == "__main__":
    print("Connecting to router and fetching BGP table...")
    file = get_bgp_output()
    print("Uploading to FTP server...")
    upload_to_ftp(file)
    print("Done! File uploaded as", FTP_FILENAME)

    # Clean up local file
    os.remove(file)
