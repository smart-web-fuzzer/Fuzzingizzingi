import boto3
import json
from datetime import datetime
# 성능 최적화 모듈인 9번 모듈을 사용하여 JSON 데이터를 처리해야 할듯... 

# Boto3를 사용하여 S3 클라이언트 설정
s3_client = boto3.client('s3')

def save_to_s3(bucket_name, key, data):
    """
    AWS S3 버킷에 데이터를 저장합니다.
    :param bucket_name: S3 버킷 이름
    :param key: S3에 저장될 파일의 키 (경로 포함)
    :param data: 저장할 데이터
    """
    s3_client.put_object(Bucket=bucket_name, Key=key, Body=data)

def process_and_save_data(method, url, headers, body, source_ip, request_size, response_size):
    # 메소드를 처리해서 크기 구현 
    """
    받은 데이터를 처리하고 S3에 저장합니다.
    :param method: HTTP 메소드
    :param url: 요청 URL
    :param headers: HTTP 헤더
    :param source_ip: 소스 IP 주소
    
    :param request_size: 요청 크기
    :param response_size: 응답 크기
    """
    
    # 메소드 처리 후 사이즈 지정 
    data = {
        'method': method,
        'url': url,
        'source_ip': source_ip,
        'request_size': request_size,
        'response_size': response_size
    }
    
    # JSON 형식으로 데이터 변환
    json_data = json.dumps(data)
    
    # 현재 시간을 기준으로 파일 이름 생성
    now = datetime.now()
    file_name = f"http_data_{now.strftime('%Y-%m-%d_%H-%M-%S')}.json"
    
    # S3에 데이터 저장
    save_to_s3('your-bucket-name', file_name, json_data)
    print(f"Data saved to S3: {file_name}")
