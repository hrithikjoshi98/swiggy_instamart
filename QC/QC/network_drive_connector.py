import subprocess

network_drive_path = r"\\172.27.132.84\D"  # Network drive path with ip and Drive name
drive_letter = "W:"  # Drive letter you want to use for network drive
username = "actowiz"  # username of KVM
password = "actowiz123"  # password of KVM

if __name__ == '__main__':
    subprocess.run(args=["net", "use", drive_letter, network_drive_path, "/user:" + username, password], shell=True)
