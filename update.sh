#!/bin/bash

export $(grep -v '^#' ba.env | xargs)

download_file() {
    local url=$1
    local output=$2

    while true; do
        echo "Downloading: $url"
        http_status=$(curl -s -w "%{http_code}" -o "$output" "$url")

        if [ "$http_status" -eq 200 ] && [ -s "$output" ]; then
            echo "Downloaded: $output"
            break
        else
            echo "Download failed with status $http_status or file is empty: $url"
            exit 1
        fi
    done
}


download_file "${ADDRESSABLE_CATALOG_URL}/TableBundles/TableCatalog.bytes" "TableCatalog.bytes"
download_file "${ADDRESSABLE_CATALOG_URL}/MediaResources/Catalog/MediaCatalog.bytes" "MediaCatalog.bytes"
download_file "${ADDRESSABLE_CATALOG_URL}/TableBundles/Excel.zip" "Excel.zip"
download_file "${ADDRESSABLE_CATALOG_URL}/TableBundles/ExcelDB.db" "ExcelDB.db"
