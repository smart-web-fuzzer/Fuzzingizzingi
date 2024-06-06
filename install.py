import subprocess
import os
import zipfile

class InstallRequirement():
    def __init__(self,):
        self.current_path = os.getcwd()
        self.chrdri_zip = '\\chromedriver-win64.zip'
        self.folder_zip = '\\chromedriver-win64'
    def get_version(self):
        try:
            result = subprocess.run(
                ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.splitlines():
                if 'version' in line:
                    version = line.split()[-1]

            return version

        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")
            return None

    def install_chrdri(self, version):
        install_command = f'curl -o chromedriver-win64.zip https://storage.googleapis.com/chrome-for-testing-public/{version}/win64/chromedriver-win64.zip'

        try:
            spider_path = self.current_path

            os.chdir(spider_path)
            subprocess.check_call(install_command, shell=True)

        except Exception as e:
            print(e)

    def unzip_chrdri(self):
        final_path = self.current_path + self.chrdri_zip
        print(f"Final path: {final_path}")

        # ZIP 파일 추출
        try:
            with zipfile.ZipFile(final_path, 'r') as zip_ref:
                zip_ref.extractall(self.current_path)
            print(f"Files extracted to {self.current_path}")
        except zipfile.BadZipFile as e:
            print(f"An error occurred while extracting the zip file: {e}")

    def mv_chrdir(self):
        folder_path = self.current_path + self.folder_zip
        final_path = self.current_path + '\\crawler\\spiders\\'
        move_command = f'move {folder_path}\\chromedriver.exe {final_path}'

        subprocess.check_call(move_command, shell=True)
#

# main 함수 사용 시
# from install import InstallRequirement

# installer = InstallRequirement()
# installer.install_chrdri(installer.get_version())
# installer.unzip_chrdri()
# installer.mv_chrdir()

