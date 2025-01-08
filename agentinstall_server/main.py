import mysql.connector
import configparser
import yaml

# INI 파일에서 DB 설정 읽기
def load_db_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    db_config = {
        'host': config['mysql']['host'],
        'user': config['mysql']['user'],
        'password': config['mysql']['password'],
        'database': config['mysql']['database'],
        'charset': 'utf8mb4_0900_ai_ci'
    }
    yaml_file_path = config['output']['yaml_file_path']
    return db_config, yaml_file_path



# INI 파일 경로
config_file = "config.ini"

# MySQL 연결 및 데이터 조회
try:
    db_config, yaml_file_path = load_db_config(config_file)
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT ProjectCode, Name, ProductType, ApiToken, Platform, LicenseKey FROM ApmProject WHERE LicenseKey != ''")
    results = cursor.fetchall()
    
    # 결과를 YAML로 저장
    with open(yaml_file_path, "w", encoding="utf-8") as yaml_file:
        yaml.dump(results, yaml_file, allow_unicode=True, default_flow_style=False)
    
    print(f"Project 메타타데이터를 YAML 파일로 저장했습니다: {yaml_file_path}")

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals() and connection.is_connected():
        connection.close()