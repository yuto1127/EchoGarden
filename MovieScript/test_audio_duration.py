#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音声ファイルの長さ取得テスト
"""

import subprocess
import os
from pathlib import Path

def find_ffmpeg():
    """FFmpegのパスを検索"""
    possible_paths = [
        'ffmpeg',  # PATHにある場合
        '/usr/local/bin/ffmpeg',
        '/opt/homebrew/bin/ffmpeg',  # macOS Homebrew
        '/usr/bin/ffmpeg',
    ]
    
    for path in possible_paths:
        try:
            print(f"FFmpegを確認中: {path}")
            result = subprocess.run([path, '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"FFmpegが見つかりました: {path}")
                return path
        except FileNotFoundError:
            print(f"FFmpegが見つかりません: {path}")
            continue
        except subprocess.TimeoutExpired:
            print(f"FFmpegの確認がタイムアウトしました: {path}")
            continue
        except Exception as e:
            print(f"FFmpegの確認でエラー: {path} - {str(e)}")
            continue
    
    print("FFmpegが見つかりませんでした")
    return None

def get_audio_duration(ffmpeg_path, audio_file):
    """音声ファイルの長さを取得（リターンコード無視版）"""
    print(f"音声ファイルの長さを取得中: {audio_file}")
    cmd = [ffmpeg_path, '-i', audio_file]
    print(f"実行コマンド: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        # リターンコードに関係なくstderrをパース
        for line in result.stderr.split('\n'):
            if 'Duration:' in line:
                print(f"Duration行を発見: {line}")
                duration_str = line.split('Duration:')[1].split(',')[0].strip()
                print(f"抽出された時間文字列: {duration_str}")
                time_parts = duration_str.split(':')
                hours = int(time_parts[0])
                minutes = int(time_parts[1])
                seconds = float(time_parts[2])
                total_seconds = hours * 3600 + minutes * 60 + seconds
                print(f"変換結果: {hours}時間 {minutes}分 {seconds}秒 = {total_seconds}秒")
                return total_seconds
        print("Duration行が見つかりませんでした")
        return 0
    except Exception as e:
        print(f"予期しないエラー: {e}")
        return 0

def main():
    print("=== 音声ファイルの長さ取得テスト（修正版） ===")
    
    # FFmpegのパスを取得
    ffmpeg_path = find_ffmpeg()
    if not ffmpeg_path:
        print("FFmpegが見つかりません。テストを終了します。")
        return
    
    # テスト用の音声ファイルを探す
    test_files = [
        "../TestAudio/A Tune of Mystery.mp3",
        "../TestAudio/Melody Beneath the Moon.mp3",
        "../TestAudio/Rain Knows My Name.mp3",
        "../TestAudio/Under the Downpour.mp3",
        "../TestAudio/Where Dreams Meet the Sky.mp3"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n--- テストファイル: {test_file} ---")
            duration = get_audio_duration(ffmpeg_path, test_file)
            if duration > 0:
                print(f"✅ 成功: {duration:.2f}秒")
            else:
                print("❌ 失敗: 長さを取得できませんでした")
        else:
            print(f"⚠️  ファイルが見つかりません: {test_file}")

if __name__ == "__main__":
    main() 