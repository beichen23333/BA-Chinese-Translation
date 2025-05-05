import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from zipfile import ZipFile
from extractor import TablesExtractor
from repacker import TableRepackerImpl
from lib.encryption import zip_password
import shutil
from collections import defaultdict

def main(excel_input_path: Path, repl_input_dir: Path, temp_output_dir: Path) -> None:
    import setup_flatdata
    packer = TableRepackerImpl('Extracted.FlatData')
    source_dir = Path(f'Extracted/Table/{excel_input_path.stem}')
    source_binary_dir = Path(f'Extracted/Temp/Table/{excel_input_path.stem}')
    
    if not source_dir.exists():
        print("Extracting source zip JSONs...")
        TablesExtractor('Extracted', excel_input_path.parent).extract_table(excel_input_path.name)
    
    if not source_binary_dir.exists():
        print("Extracting source zip binaries...")
        source_binary_dir.mkdir(parents=True, exist_ok=True)
        with ZipFile(excel_input_path, "r") as excel_zip:
            excel_zip.setpassword(zip_password("Excel.zip"))
            excel_zip.extractall(path=source_binary_dir)
    
    with tempfile.TemporaryDirectory() as temp_extract_dir:
        temp_extract_path = Path(temp_extract_dir)
        shutil.copytree(source_binary_dir, temp_extract_dir, dirs_exist_ok=True)
        
        print("Applying replacements...")
        for file in source_dir.iterdir():
            target_file = temp_extract_path / f"{file.stem.lower()}.bytes"
            repl_file = repl_input_dir / file.name
            if repl_file.exists():
                out_file = apply_replacements(file, repl_file)
                if out_file.exists():
                    with open(target_file, "wb") as tf:
                        with open(out_file, "rb") as of:
                            tf.write(of.read())
                    out_file.unlink()
        
        # 将处理后的文件复制到临时输出目录
        if not temp_output_dir.exists():
            temp_output_dir.mkdir(parents=True, exist_ok=True)
        for file in temp_extract_path.iterdir():
            shutil.copy(file, temp_output_dir / file.name)
    
    temp_dir = source_dir / "temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    print(f"Outputed modified files to {temp_output_dir}")
