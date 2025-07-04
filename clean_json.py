import os
import json
import argparse
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

def clean_json_file(file_path, keep_keys):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        cleaned_data = clean_json(json_data, keep_keys)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=4)
        print(f"Cleaned {file_path}")
    except FileNotFoundError:
        print(f"File {file_path} not found, skipping.")
    except json.JSONDecodeError:
        print(f"File {file_path} is not a valid JSON file, skipping.")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def clean_json(data, keep_keys):
    if isinstance(data, dict):
        cleaned_data = {}
        for key, value in data.items():
            if key in keep_keys:
                cleaned_data[key] = clean_json(value, keep_keys)
        return cleaned_data
    elif isinstance(data, list):
        return [clean_json(item, keep_keys) for item in data]
    else:
        return data

def pack_to_zip(file_paths, zip_path):
    # 确保输出目录存在
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    
    with ZipFile(zip_path, 'w', compression=ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            if os.path.exists(file_path):
                # 使用文件名作为zip中的路径，避免目录结构
                arcname = os.path.basename(file_path)
                zipf.write(file_path, arcname)
                print(f"Added {file_path} to {zip_path} as {arcname}")
            else:
                print(f"File {file_path} not found, skipping.")

def main():
    parser = argparse.ArgumentParser(description="Clean JSON files in a directory based on a configuration file.")
    parser.add_argument('--output_dir', type=Path, required=True, help="Directory containing JSON files.")
    parser.add_argument('--server', type=str, required=True, choices=['日服', '国服', '国际服'], help="选择服务器")
    parser.add_argument("--zip_path", type=Path, default="./unpacked/UnpackedExcel.zip", help="Path to save the ZIP archive.")
    args = parser.parse_args()

    # 读取配置文件
    config_file = '配置.json'
    if not os.path.exists(config_file):
        print(f"Configuration file {config_file} not found.")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    # 获取指定目录
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        print(f"Directory {output_dir} does not exist.")
        return

    # 获取指定服务器的配置
    server_config = config_data.get("DBSchema", {}).get(args.server)
    if not server_config:
        print(f"Server {args.server} not found in configuration file.")
        return

    # 遍历配置中的每个文件和对应的保留键
    processed_files = []
    for file_name, keep_keys in server_config.items():
        file_path = os.path.join(output_dir, file_name)
        if os.path.exists(file_path) and file_path.endswith('.json'):  # 只处理.json文件
            clean_json_file(file_path, keep_keys)
            processed_files.append(file_path)
        else:
            print(f"File {file_path} not found or not a JSON file, skipping.")

    # 删除多余的文件
    for file_name in os.listdir(output_dir):
        file_path = os.path.join(output_dir, file_name)
        if file_path not in processed_files and os.path.isfile(file_path) and not file_path.endswith('.zip'):  # 排除.zip文件
            os.remove(file_path)
            print(f"Deleted {file_path}")

    # 压缩处理过的文件
    if processed_files:
        pack_to_zip(processed_files, args.zip_path)
        print(f"Successfully created ZIP archive at {args.zip_path}")
    else:
        print("No files processed, skipping ZIP creation.")

if __name__ == "__main__":
    main()
