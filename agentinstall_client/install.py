import yaml
import configparser
import requests
import sys
import tarfile
import subprocess
import os
import re
from datetime import datetime

def create_db_conf(file_path, license_code, server_host, server_port, dbms, db_addr, db_port, option_string=""):
    """
    :param file_path: 생성할 파일 경로
    :param license_code: license 값
    :param server_host: whatap.server.host 값 (기본값: 빈 문자열)
    """
    try:
        # 현재 시간: 나노초
        created_time = datetime.now().strftime('%s%f')  # 초와 마이크로초를 합친 나노초 표현

        # 파일 내용 생성
        content = f"""license={license_code}
whatap.server.host={server_host}
whatap.server.port={server_port}

dbms={dbms}
{option_string}
db_ip={db_addr}
db_port={db_port}
"""

        # 디렉토리 확인 및 생성
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 파일 쓰기
        with open(file_path, "w") as conf_file:
            conf_file.write(content)

        print(f"파일 생성 완료: {file_path}")
        print("내용:")
        print(content)

    except Exception as e:
        print(f"파일 생성 중 오류 발생: {e}")

def create_infra_conf(file_path, license_code, server_host, server_port):
    """
    /usr/whatap/infra/conf/whatap.conf 파일을 생성합니다.

    :param file_path: 생성할 파일 경로
    :param license_code: license 값
    :param server_host: whatap.server.host 값 (기본값: 빈 문자열)
    """
    try:
        # 현재 시간: 나노초
        created_time = datetime.now().strftime('%s%f')  # 초와 마이크로초를 합친 나노초 표현

        # 파일 내용 생성
        content = f"""license={license_code}
whatap.server.host={server_host}
whatap.server.port={server_port}
createdtime={created_time}"""

        # 디렉토리 확인 및 생성
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 파일 쓰기
        with open(file_path, "w") as conf_file:
            conf_file.write(content)

        print(f"파일 생성 완료: {file_path}")
        print("내용:")
        print(content)

    except Exception as e:
        print(f"파일 생성 중 오류 발생: {e}")

def install_deb_package(deb_file_path):
    """
    .deb 패키지를 설치합니다.

    :param deb_file_path: .deb 파일 경로
    """
    try:
        print(f"{deb_file_path} 설치 중...")
        # dpkg 명령 실행
        subprocess.run(["sudo", "dpkg", "-i", deb_file_path], check=True)
        print("설치 완료")
    except subprocess.CalledProcessError as e:
        print(f"설치 중 오류 발생: {e}")
    except FileNotFoundError:
        print("dpkg 명령이 시스템에 설치되어 있지 않습니다. 설치 후 다시 시도하세요.")


def extract_tar_gz(file_path, output_dir):
    """
    .tar.gz 파일을 지정된 디렉토리에 압축 해제합니다.

    :param file_path: .tar.gz 파일 경로
    :param output_dir: 압축 해제할 디렉토리 경로
    """
    try:
        # .tar.gz 파일 열기
        with tarfile.open(file_path, "r:gz") as tar:
            print(f"{file_path} 파일 압축 해제 중...")
            tar.extractall(path=output_dir)  # 압축 해제
            print(f"압축 해제 완료: {output_dir}")
    except Exception as e:
        print(f"압축 해제 실패: {e}")


def download_file_with_progress(url, output_path):
    """
    HTTP를 통해 파일을 다운로드하며 진행률을 표시합니다.

    :param url: 파일의 URL
    :param output_path: 저장할 파일 경로
    """
    try:
        # HTTP GET 요청
        response = requests.get(url, stream=True)
        response.raise_for_status()  # HTTP 오류가 발생하면 예외 처리

        # 파일 크기 가져오기
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0  # 다운로드된 데이터 크기

        # 파일 다운로드
        with open(output_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded_size += len(chunk)

                    # 진행률 계산 및 표시
                    percent = (downloaded_size / total_size) * 100 if total_size > 0 else 0
                    sys.stdout.write(f"\r진행률: {percent:.2f}%")
                    sys.stdout.flush()

        print("\n파일 다운로드 완료:", output_path)

    except requests.exceptions.RequestException as e:
        print(f"파일 다운로드 실패: {e}")

def get_dbx_file(directory):
    # 파일 이름 패턴 정규식 (버전 번호 추출)
    pattern = r"whatap\.agent\.dbx-(\d+\.\d+\.\d+)\.jar"

    # 가장 높은 버전을 저장할 변수
    latest_version = None
    latest_file = None

    # 디렉터리 내 파일 검색
    for filename in os.listdir(directory):
        match = re.match(pattern, filename)
        if match:
            # 버전 번호 추출
            version = tuple(map(int, match.group(1).split(".")))
            if latest_version is None or version > latest_version:
                latest_version = version
                latest_file = filename

    # 최신 파일이 있다면 리턴, 없으면 None을 리턴
    return latest_file


def subproc_uid(java_bin_path, uid_dir, user_id, user_password):
    try:
        dbx_file_path = get_dbx_file(uid_dir)
        #java -cp $EXE_DBX_JAR whatap.dbx.DbUser -update -uid $WUID -user $WUSER -password $WPASSWORD
        subprocess.run([java_bin_path, "-cp", dbx_file_path, "whatap.dbx.DbUser", "-update", "-uid", "1000", "-user", user_id, "-password", user_password], cwd=uid_dir, check=True)
        print("uid  완료")
    except subprocess.CalledProcessError as e:
        print(f"uid  오류 발생: {e}")

def subproc_mv(source_dir, dest_dir):
    try:
        subprocess.run(["mv", source_dir, dest_dir], check=True)
        print("mv 완료")
    except subprocess.CalledProcessError as e:
        print(f"mv 오류 발생: {e}")


def subproc_startd(dest_dir):
    try:
        subprocess.run(["sh", "startd.sh"], cwd=dest_dir, check=True)
        print("start 완료")
    except subprocess.CalledProcessError as e:
        print(f"start 오류 발생: {e}")


def infra_agent_start():
    try:
        subprocess.run(["sudo", "systemctl", "restart", "whatap-infra.service"], check=True)
        print("restart 완료")
    except subprocess.CalledProcessError as e:
        print(f"restart 오류 발생: {e}")


# YAML 파일 읽기
def load_yaml_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as yaml_file:
        data = yaml.safe_load(yaml_file)
    return data



# Platform 선택
def select_platform(data):
    platforms = set(item['Platform'] for item in data)  # Platform 목록 추출
    print("사용 가능한 Platform 목록:")
    for idx, platform in enumerate(platforms, start=1):
        print(f"{idx}. {platform}")

    while True:
        try:
            choice = int(input("Platform 번호를 선택하세요: "))
            if 1 <= choice <= len(platforms):
                return list(platforms)[choice - 1]
            else:
                print("유효한 번호를 선택하세요.")
        except ValueError:
            print("숫자를 입력하세요.")

# Name (ProjectCode) 선택
def select_name(data, selected_platform):
    filtered_projects = [
        {'Name': item['Name'], 'ProjectCode': item['ProjectCode'], 'LicenseKey': item.get('LicenseKey')}
        for item in data if item['Platform'] == selected_platform
    ]
    print(f"\n{selected_platform} Platform에 해당하는 프로젝트 목록:")
    for idx, project in enumerate(filtered_projects, start=1):
        print(f"{idx}. {project['Name']} ({project['ProjectCode']})")

    while True:
        try:
            choice = int(input("프로젝트 번호를 선택하세요: "))
            if 1 <= choice <= len(filtered_projects):
                return filtered_projects[choice - 1]
            else:
                print("유효한 번호를 선택하세요.")
        except ValueError:
            print("숫자를 입력하세요.")

def infra_agent_install(config, license_key):
    temp_base_dir = config['agent']['temp_base_dir']
    agent_url = config['front']['base_url'] + config['front']['infra_agent_path']

    agent_tar_path = temp_base_dir + "/agent.deb"
    download_file_with_progress(agent_url, agent_tar_path)
    install_deb_package(agent_tar_path)

    server_host = config['agent']['server_host']
    server_port = config['agent']['infra_server_port']
    create_infra_conf("/usr/whatap/infra/conf/whatap.conf", license_key, server_host, server_port)
    infra_agent_start()

def mysql_agent_install(config, license_key):
    temp_base_dir = config['agent']['db_base_dir']
    db_agent_url = config['front']['base_url'] + config['front']['db_agent_path']
    mysql_jdbc_url = config['front']['base_url'] + config['front']['mysql_jdbc_path']

    instance_name  = input("DB Instance Name을 입력하세요 : ")
    db_addr  = input("DB Addr을 입력하세요 : ")
    db_port  = input("DB Port을 입력하세요 : ")

    user_id  = input("DB User을 입력하세요 : ")
    user_password  = input("DB Password을 입력하세요 : ")

    agent_tar_path = temp_base_dir + "/db_agent.tar.gz"
    agent_jdbc_path = temp_base_dir + "/mysql.jar"
    download_file_with_progress(db_agent_url, agent_tar_path)
    download_file_with_progress(mysql_jdbc_url, agent_jdbc_path)

    server_host = config['agent']['server_host']
    server_port = config['agent']['db_server_port']

    extract_tar_gz(agent_tar_path, temp_base_dir)
    dest_dir = temp_base_dir + "/" + instance_name
    subproc_mv(temp_base_dir + "/whatap", temp_base_dir + "/" + instance_name)
    subproc_mv(agent_jdbc_path, dest_dir + "/jdbc")
    create_db_conf(dest_dir + "/whatap.conf", license_key, server_host, server_port, "mysql", db_addr, db_port, "object_name=test11")
    subproc_uid(config['db_agent_env']['java_bin_path'], dest_dir, user_id, user_password)
    subproc_startd(dest_dir)



# 대화형 프로그램 실행
def main():

    config = configparser.ConfigParser()
    config.read("installer.ini", encoding='utf-8')

    front_base_url = config['front']['base_url']
    project_path = config['front']['project_path']

    download_file_with_progress(front_base_url + project_path, "project.yaml")

    yaml_file_path = "project.yaml"
    data = load_yaml_file(yaml_file_path)

    print("=== 설치 프로그램 ===")
    selected_platform = select_platform(data)
    selected_project = select_name(data, selected_platform)

    print("\n선택된 항목:")
    print(f"Platform: {selected_platform}")
    print(f"Name: {selected_project['Name']}")
    print(f"ProjectCode: {selected_project['ProjectCode']}")

    # LicenseCode 출력
    if selected_project.get('LicenseKey'):
        print(f"LicenseKey: {selected_project['LicenseKey']}")
    else:
        print("LicenseKey가 존재하지 않습니다.")

    if selected_platform == "INFRA":
        infra_agent_install(config, selected_project['LicenseKey'])
    elif selected_platform == "MYSQL":
        mysql_agent_install(config, selected_project['LicenseKey'])

if __name__ == "__main__":
    main()
