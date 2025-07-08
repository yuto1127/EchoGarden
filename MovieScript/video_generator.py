#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動画生成エンジン
BGMと背景画像を使用して動画を作成する
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import json
import random

class VideoGenerator:
    def __init__(self):
        self.temp_dir = None
        self.ffmpeg_path = self.find_ffmpeg()
        
    def find_ffmpeg(self):
        """FFmpegのパスを検索"""
        # 一般的なFFmpegのインストール場所をチェック
        possible_paths = [
            'ffmpeg',  # PATHにある場合
            '/usr/local/bin/ffmpeg',
            '/opt/homebrew/bin/ffmpeg',  # macOS Homebrew
            '/usr/bin/ffmpeg',
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, '-version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return path
            except FileNotFoundError:
                continue
        
        raise FileNotFoundError("FFmpegが見つかりません。FFmpegをインストールしてください。")
    
    def create_temp_directory(self):
        """一時ディレクトリを作成"""
        if self.temp_dir is None:
            self.temp_dir = tempfile.mkdtemp(prefix="echogarden_")
        return self.temp_dir
    
    def cleanup_temp_directory(self):
        """一時ディレクトリを削除"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
    
    def get_audio_duration(self, audio_file):
        """音声ファイルの長さを取得"""
        cmd = [
            self.ffmpeg_path, '-i', audio_file,
            '-show_entries', 'format=duration',
            '-v', 'quiet', '-of', 'csv=p=0'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except:
            pass
        
        return 0
    
    def create_single_video(self, bgm_file, background_files, output_dir):
        """単曲動画を作成"""
        print("単曲動画を作成中...")
        
        # 一時ディレクトリを作成
        temp_dir = self.create_temp_directory()
        
        try:
            # 音声の長さを取得
            audio_duration = self.get_audio_duration(bgm_file)
            if audio_duration == 0:
                raise ValueError("音声ファイルの長さを取得できませんでした")
            
            # 出力ファイル名を生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"single_video_{timestamp}.mp4")
            
            # 背景画像をランダムに選択
            background_file = random.choice(background_files)
            
            # FFmpegコマンドを構築
            cmd = [
                self.ffmpeg_path,
                '-loop', '1',  # 画像をループ
                '-i', background_file,  # 背景画像
                '-i', bgm_file,  # BGM
                '-c:v', 'libx264',  # ビデオコーデック
                '-c:a', 'aac',  # オーディオコーデック
                '-shortest',  # 短い方に合わせる
                '-pix_fmt', 'yuv420p',  # ピクセルフォーマット
                '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2',  # 1920x1080にリサイズ
                '-af', 'afade=t=in:st=0:d=3,afade=t=out:st=' + str(audio_duration - 3) + ':d=3',  # フェードイン・アウト
                '-y',  # 上書き
                output_file
            ]
            
            # 動画を作成
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"動画作成に失敗しました: {result.stderr}")
            
            print(f"動画を作成しました: {output_file}")
            return output_file
            
        finally:
            self.cleanup_temp_directory()
    
    def create_loop_video(self, bgm_file, background_files, output_dir, duration_minutes):
        """耐久動画を作成"""
        print(f"耐久動画を作成中... ({duration_minutes}分)")
        
        # 一時ディレクトリを作成
        temp_dir = self.create_temp_directory()
        
        try:
            # 音声の長さを取得
            audio_duration = self.get_audio_duration(bgm_file)
            if audio_duration == 0:
                raise ValueError("音声ファイルの長さを取得できませんでした")
            
            # 目標時間（秒）
            target_duration = duration_minutes * 60
            
            # 音声をループして目標時間に達するまで繰り返す
            loop_count = int(target_duration / audio_duration) + 1
            
            # ループ用の音声ファイルを作成
            loop_audio_file = os.path.join(temp_dir, "loop_audio.mp3")
            
            # 音声ファイルを連結
            concat_file = os.path.join(temp_dir, "concat.txt")
            with open(concat_file, 'w') as f:
                for _ in range(loop_count):
                    f.write(f"file '{bgm_file}'\n")
            
            cmd_concat = [
                self.ffmpeg_path,
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',
                '-y',
                loop_audio_file
            ]
            
            result = subprocess.run(cmd_concat, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"音声の連結に失敗しました: {result.stderr}")
            
            # 最終的な音声の長さを取得
            final_audio_duration = self.get_audio_duration(loop_audio_file)
            
            # 出力ファイル名を生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"loop_video_{duration_minutes}min_{timestamp}.mp4")
            
            # 背景画像をランダムに選択
            background_file = random.choice(background_files)
            
            # FFmpegコマンドを構築
            cmd = [
                self.ffmpeg_path,
                '-loop', '1',  # 画像をループ
                '-i', background_file,  # 背景画像
                '-i', loop_audio_file,  # ループBGM
                '-c:v', 'libx264',  # ビデオコーデック
                '-c:a', 'aac',  # オーディオコーデック
                '-shortest',  # 短い方に合わせる
                '-pix_fmt', 'yuv420p',  # ピクセルフォーマット
                '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2',  # 1920x1080にリサイズ
                '-af', 'afade=t=in:st=0:d=3,afade=t=out:st=' + str(final_audio_duration - 3) + ':d=3',  # フェードイン・アウト
                '-y',  # 上書き
                output_file
            ]
            
            # 動画を作成
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"動画作成に失敗しました: {result.stderr}")
            
            print(f"耐久動画を作成しました: {output_file}")
            return output_file
            
        finally:
            self.cleanup_temp_directory()
    
    def create_melody_video(self, melody_files, background_files, output_dir):
        """メドレー動画を作成"""
        print("メドレー動画を作成中...")
        
        # 一時ディレクトリを作成
        temp_dir = self.create_temp_directory()
        
        try:
            # 出力ファイル名を生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"melody_video_{timestamp}.mp4")
            
            # 動画ファイルを連結
            concat_file = os.path.join(temp_dir, "concat.txt")
            with open(concat_file, 'w') as f:
                for video_file in melody_files:
                    f.write(f"file '{video_file}'\n")
            
            # 背景画像をランダムに選択
            background_file = random.choice(background_files)
            
            # 一時的な動画ファイルを作成（背景画像のみ）
            temp_video = os.path.join(temp_dir, "temp_background.mp4")
            
            # 背景画像から動画を作成（十分な長さ）
            cmd_bg = [
                self.ffmpeg_path,
                '-loop', '1',
                '-i', background_file,
                '-t', '3600',  # 1時間
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2',
                '-y',
                temp_video
            ]
            
            result = subprocess.run(cmd_bg, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"背景動画の作成に失敗しました: {result.stderr}")
            
            # メドレー動画を連結
            temp_concat = os.path.join(temp_dir, "temp_concat.mp4")
            
            cmd_concat = [
                self.ffmpeg_path,
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',
                '-y',
                temp_concat
            ]
            
            result = subprocess.run(cmd_concat, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"動画の連結に失敗しました: {result.stderr}")
            
            # 最終的な動画を作成（背景画像 + メドレー音声）
            cmd_final = [
                self.ffmpeg_path,
                '-i', temp_video,
                '-i', temp_concat,
                '-map', '0:v',  # 背景動画の映像
                '-map', '1:a',  # メドレーの音声
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                '-af', 'afade=t=in:st=0:d=3,afade=t=out:st=-3:d=3',
                '-y',
                output_file
            ]
            
            result = subprocess.run(cmd_final, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"最終動画の作成に失敗しました: {result.stderr}")
            
            print(f"メドレー動画を作成しました: {output_file}")
            return output_file
            
        finally:
            self.cleanup_temp_directory()
    
    def create_short_version(self, bgm_file, background_files, output_dir, duration_seconds):
        """SNS用ショートバージョン動画を作成"""
        print(f"SNS用ショートバージョン動画を作成中... ({duration_seconds}秒)")
        
        # 一時ディレクトリを作成
        temp_dir = self.create_temp_directory()
        
        try:
            # 音声の長さを取得
            audio_duration = self.get_audio_duration(bgm_file)
            if audio_duration == 0:
                raise ValueError("音声ファイルの長さを取得できませんでした")
            
            # 出力ファイル名を生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"short_video_{duration_seconds}s_{timestamp}.mp4")
            
            # 背景画像をランダムに選択
            background_file = random.choice(background_files)
            
            # 音声を指定時間にトリム
            trimmed_audio_file = os.path.join(temp_dir, "trimmed_audio.mp3")
            
            cmd_trim = [
                self.ffmpeg_path,
                '-i', bgm_file,
                '-t', str(duration_seconds),
                '-c:a', 'aac',
                '-y',
                trimmed_audio_file
            ]
            
            result = subprocess.run(cmd_trim, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"音声のトリムに失敗しました: {result.stderr}")
            
            # 最終的な音声の長さを取得
            final_audio_duration = self.get_audio_duration(trimmed_audio_file)
            
            # FFmpegコマンドを構築（縦型動画用）
            cmd = [
                self.ffmpeg_path,
                '-loop', '1',  # 画像をループ
                '-i', background_file,  # 背景画像
                '-i', trimmed_audio_file,  # トリムされたBGM
                '-c:v', 'libx264',  # ビデオコーデック
                '-c:a', 'aac',  # オーディオコーデック
                '-shortest',  # 短い方に合わせる
                '-pix_fmt', 'yuv420p',  # ピクセルフォーマット
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',  # 1080x1920にリサイズ（縦型）
                '-af', 'afade=t=in:st=0:d=1,afade=t=out:st=' + str(final_audio_duration - 1) + ':d=1',  # フェードイン・アウト（短縮版）
                '-y',  # 上書き
                output_file
            ]
            
            # 動画を作成
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"ショートバージョン動画作成に失敗しました: {result.stderr}")
            
            print(f"SNS用ショートバージョン動画を作成しました: {output_file}")
            return output_file
            
        finally:
            self.cleanup_temp_directory()
    
    def __del__(self):
        """デストラクタで一時ディレクトリを削除"""
        self.cleanup_temp_directory() 