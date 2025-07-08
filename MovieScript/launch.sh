#!/bin/bash

# EchoGarden 動画作成ツール ランチャー

# Tkinterの非推奨警告を抑制
export TK_SILENCE_DEPRECATION=1

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# Pythonのバージョンをチェック
python_version=$(python --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "エラー: Python 3.7以上が必要です。現在のバージョン: $python_version"
    exit 1
fi

# FFmpegの存在をチェック
if ! command -v ffmpeg &> /dev/null; then
    echo "警告: FFmpegが見つかりません。"
    echo "FFmpegをインストールしてください:"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo ""
    echo "FFmpegをインストールした後、再度実行してください。"
    read -p "続行しますか？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# アプリケーションを起動
echo "EchoGarden 動画作成ツールを起動中..."
python video_creator.py 