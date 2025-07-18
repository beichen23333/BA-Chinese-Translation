import os
import sys
import requests
from pathlib import Path
import json
import regions.CN.update_urls_cn as update_urls_cn

def download_file(url: str, output_file: Path):
    response = requests.get(url)
    if response.status_code != 200:
        raise ConnectionError(f"无法下载 {url}. 状态代码: {response.status_code}")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "wb") as f:
        f.write(response.content)
    print(f"下载 {url} 并保存至 {output_file}")

def download_excel_files(env_file: Path, output_dir: Path):
    if not env_file.exists():
        raise FileNotFoundError(f"环境文件 {env_file} 没有找到")
    
    env_vars = {}
    with open(env_file, "r") as f:
        for line in f:
            key, value = line.strip().split("=")
            env_vars[key] = value
    
    server_url = update_urls_cn.get_server_url()
    try:
        server_url_dict = json.loads(server_url)
    except json.JSONDecodeError as e:
        raise ValueError(f"无法将server_url解析为JSON: {e}")

    # 从解析后的字典中获取 TableVersion
    table_version = server_url_dict.get("TableVersion")
    if table_version is None:
        raise KeyError("在下载的文件中找不到键TableVersion")
    print(f"TableVersion: {table_version}")

    ba_server_url = env_vars.get("ADDRESSABLE_CATALOG_URL_CN")

    # 下载 TableManifest 文件
    table_manifest_url = f"{ba_server_url}/Manifest/TableBundles/{table_version}/TableManifest"
    table_manifest_path = output_dir / "TableManifest.json"
    download_file(table_manifest_url, table_manifest_path)

    # 解析 TableManifest 文件，提取 ExcelDB.db 的 Crc 值
    with open(table_manifest_path, "r", encoding="utf-8") as f:
        table_manifest_data = json.load(f)
        excel_db_info = table_manifest_data.get("Table", {}).get("ExcelDB.db")
        if not excel_db_info:
            raise KeyError("ExcelDB.db在TableManifest中找不到信息。")
        crc_value = excel_db_info.get("Crc")
        if not crc_value:
            raise KeyError("ExcelDB.db的CRC值未在TableManifest找到")
        print(f"ExcelDB.db的CRC值: {crc_value}")

    # 构造最终的下载链接
    crc_prefix = crc_value[:2]
    excel_db_download_url = f"{ba_server_url}/pool/TableBundles/{crc_prefix}/{crc_value}"
    excel_zip_download_url = f"{ba_server_url}/pool/TableBundles/{crc_prefix}/{crc_value}"

    # 下载 ExcelDB.db 和 Excel.zip 文件
    excel_db_path = output_dir / "ExcelDB.db"
    excel_zip_path = output_dir / "Excel.zip"
    download_file(excel_db_download_url, excel_db_path)
    download_file(excel_zip_download_url, excel_zip_path)

    print(f"下载文件")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Download ExcelDB.db and Excel.zip from BA_SERVER_URL.")
    parser.add_argument("--env_file", type=Path, default="./ba.env", help="Path to the ba.env file.")
    parser.add_argument("--output_dir", type=Path, default="./downloads", help="Directory to save the downloaded files.")
    args = parser.parse_args()
    
    download_excel_files(args.env_file, args.output_dir)
