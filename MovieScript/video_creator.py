#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoGarden 動画作成ツール
BGMと背景画像を使用して動画を作成するGUIアプリケーション
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import json
from datetime import datetime
from pathlib import Path
import subprocess
import sys

class VideoCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EchoGarden 動画作成ツール")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # 変数の初期化
        self.bgm_file = tk.StringVar()
        self.background_files = []
        self.output_directory = tk.StringVar()
        self.video_type = tk.StringVar(value="single")
        self.duration_minutes = tk.IntVar(value=15)
        self.melody_files = []
        self.create_short_version = tk.BooleanVar(value=False)
        self.short_duration_seconds = tk.IntVar(value=30)
        self.video_title = tk.StringVar()
        
        # 設定ファイルの読み込み
        self.config_file = Path(__file__).parent / "config.json"
        
        # 起動時のローディング画面を表示
        self.show_loading_screen()
        
        # 初期化処理を別スレッドで実行
        self.init_app()
    
    def show_loading_screen(self):
        """起動時のローディング画面を表示"""
        # ローディングフレーム
        self.loading_frame = ttk.Frame(self.root)
        self.loading_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # ロゴ・タイトル
        title_label = ttk.Label(self.loading_frame, text="EchoGarden", 
                               font=('Arial', 24, 'bold'))
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(self.loading_frame, text="動画作成ツール", 
                                  font=('Arial', 14))
        subtitle_label.pack(pady=(0, 30))
        
        # プログレスバー
        self.loading_progress = ttk.Progressbar(self.loading_frame, mode='indeterminate', 
                                              length=300)
        self.loading_progress.pack(pady=(0, 20))
        
        # ステータスラベル
        self.loading_status = ttk.Label(self.loading_frame, text="初期化中...", 
                                       font=('Arial', 10))
        self.loading_status.pack()
        
        # プログレスバーを開始
        self.loading_progress.start()
    
    def init_app(self):
        """アプリケーションの初期化処理"""
        def init_thread():
            try:
                # 設定ファイルの読み込み
                self.loading_status.config(text="設定ファイルを読み込み中...")
                self.root.update()
                self.load_config()
                
                # FFmpegの確認
                self.loading_status.config(text="FFmpegを確認中...")
                self.root.update()
                from video_generator import VideoGenerator
                generator = VideoGenerator()
                
                # メインウィジェットの作成
                self.loading_status.config(text="GUIを初期化中...")
                self.root.update()
                self.create_widgets()
                
                # ローディング画面を非表示
                self.loading_status.config(text="完了！")
                self.root.update()
                self.root.after(500, self.hide_loading_screen)
                
            except Exception as e:
                self.loading_status.config(text=f"エラー: {str(e)}")
                self.root.update()
                self.root.after(2000, self.show_error_and_exit, str(e))
        
        # 別スレッドで初期化を実行
        import threading
        thread = threading.Thread(target=init_thread)
        thread.daemon = True
        thread.start()
    
    def hide_loading_screen(self):
        """ローディング画面を非表示にする"""
        if hasattr(self, 'loading_frame'):
            self.loading_frame.destroy()
    
    def show_error_and_exit(self, error_message):
        """エラーを表示して終了"""
        messagebox.showerror("起動エラー", f"アプリケーションの起動に失敗しました:\n{error_message}")
        self.root.destroy()
        
    def load_config(self):
        """設定ファイルを読み込む"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.output_directory.set(config.get('output_directory', ''))
                    self.create_short_version.set(config.get('create_short_version', False))
                    self.short_duration_seconds.set(config.get('short_duration_seconds', 30))
                    self.video_title.set(config.get('video_title', ''))
            except:
                pass
    
    def save_config(self):
        """設定ファイルを保存"""
        config = {
            'output_directory': self.output_directory.get(),
            'create_short_version': self.create_short_version.get(),
            'short_duration_seconds': self.short_duration_seconds.get(),
            'video_title': self.video_title.get()
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def create_widgets(self):
        """GUIウィジェットを作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # タイトル
        title_label = ttk.Label(main_frame, text="EchoGarden 動画作成ツール", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # タイトル入力セクション
        self.create_title_section(main_frame, 1)
        
        # BGM選択セクション
        self.create_bgm_section(main_frame, 2)
        
        # 背景画像選択セクション
        self.create_background_section(main_frame, 3)
        
        # 動画タイプ選択セクション
        self.create_video_type_section(main_frame, 4)
        
        # ショートバージョン設定セクション
        self.create_short_version_section(main_frame, 5)
        
        # 出力設定セクション
        self.create_output_section(main_frame, 6)
        
        # 作成ボタン
        create_button = ttk.Button(main_frame, text="動画を作成", 
                                  command=self.create_video, style='Accent.TButton')
        create_button.grid(row=7, column=0, columnspan=3, pady=20)
        
        # プログレスバー
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # ステータスラベル
        self.status_label = ttk.Label(main_frame, text="準備完了")
        self.status_label.grid(row=9, column=0, columnspan=3)
        
        # グリッドの重み設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def create_title_section(self, parent, row):
        """タイトル入力セクションを作成"""
        # タイトル入力フレーム
        title_frame = ttk.LabelFrame(parent, text="動画タイトル", padding="10")
        title_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        title_frame.columnconfigure(1, weight=1)
        
        ttk.Label(title_frame, text="タイトル:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        title_entry = ttk.Entry(title_frame, textvariable=self.video_title, width=50)
        title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 説明ラベル
        info_label = ttk.Label(title_frame, text="※ ファイル名に使用されます（特殊文字は自動的に除去、重複時は番号付きになります）", 
                              font=('Arial', 9), foreground='gray')
        info_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
    
    def create_bgm_section(self, parent, row):
        """BGM選択セクションを作成"""
        # BGM選択フレーム
        bgm_frame = ttk.LabelFrame(parent, text="BGM選択", padding="10")
        bgm_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        bgm_frame.columnconfigure(1, weight=1)
        
        ttk.Label(bgm_frame, text="BGMファイル:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        bgm_entry = ttk.Entry(bgm_frame, textvariable=self.bgm_file, width=50)
        bgm_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        bgm_button = ttk.Button(bgm_frame, text="選択", command=self.select_bgm)
        bgm_button.grid(row=0, column=2)
    
    def create_background_section(self, parent, row):
        """背景画像選択セクションを作成"""
        # 背景画像選択フレーム
        bg_frame = ttk.LabelFrame(parent, text="背景画像・映像選択", padding="10")
        bg_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        bg_frame.columnconfigure(0, weight=1)
        
        bg_button = ttk.Button(bg_frame, text="背景画像・映像を選択", command=self.select_backgrounds)
        bg_button.grid(row=0, column=0, pady=(0, 10))
        
        # 選択されたファイルのリストボックス
        self.bg_listbox = tk.Listbox(bg_frame, height=4)
        self.bg_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # スクロールバー
        bg_scrollbar = ttk.Scrollbar(bg_frame, orient=tk.VERTICAL, command=self.bg_listbox.yview)
        bg_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.bg_listbox.configure(yscrollcommand=bg_scrollbar.set)
        
        # 削除ボタン
        remove_bg_button = ttk.Button(bg_frame, text="選択項目を削除", command=self.remove_background)
        remove_bg_button.grid(row=2, column=0)
    
    def create_video_type_section(self, parent, row):
        """動画タイプ選択セクションを作成"""
        # 動画タイプ選択フレーム
        type_frame = ttk.LabelFrame(parent, text="動画タイプ", padding="10")
        type_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        type_frame.columnconfigure(1, weight=1)
        
        # ラジオボタン
        ttk.Radiobutton(type_frame, text="単曲", variable=self.video_type, 
                       value="single", command=self.on_video_type_change).grid(row=0, column=0, sticky=tk.W)
        
        ttk.Radiobutton(type_frame, text="耐久動画", variable=self.video_type, 
                       value="loop", command=self.on_video_type_change).grid(row=1, column=0, sticky=tk.W)
        
        ttk.Radiobutton(type_frame, text="メドレー", variable=self.video_type, 
                       value="melody", command=self.on_video_type_change).grid(row=2, column=0, sticky=tk.W)
        
        # 耐久動画の設定
        duration_frame = ttk.Frame(type_frame)
        duration_frame.grid(row=1, column=1, sticky=tk.W, padx=(20, 0))
        
        ttk.Label(duration_frame, text="動画長:").pack(side=tk.LEFT)
        duration_spinbox = ttk.Spinbox(duration_frame, from_=15, to=120, 
                                     textvariable=self.duration_minutes, width=10)
        duration_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(duration_frame, text="分").pack(side=tk.LEFT, padx=(5, 0))
        
        # メドレー用のファイル選択
        melody_frame = ttk.Frame(type_frame)
        melody_frame.grid(row=2, column=1, sticky=tk.W, padx=(20, 0))
        
        melody_button = ttk.Button(melody_frame, text="動画ファイル選択", command=self.select_melody_files)
        melody_button.pack(side=tk.LEFT)
        
        # メドレーファイルリスト
        self.melody_listbox = tk.Listbox(melody_frame, height=3, width=40)
        self.melody_listbox.pack(side=tk.LEFT, padx=(10, 0))
    
    def create_output_section(self, parent, row):
        """出力設定セクションを作成"""
        # 出力設定フレーム
        output_frame = ttk.LabelFrame(parent, text="出力設定", padding="10")
        output_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="出力フォルダ:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        output_entry = ttk.Entry(output_frame, textvariable=self.output_directory, width=50)
        output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        output_button = ttk.Button(output_frame, text="選択", command=self.select_output_directory)
        output_button.grid(row=0, column=2)
    
    def create_short_version_section(self, parent, row):
        """ショートバージョン設定セクションを作成"""
        # ショートバージョン設定フレーム
        short_frame = ttk.LabelFrame(parent, text="SNS用ショートバージョン", padding="10")
        short_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        short_frame.columnconfigure(1, weight=1)
        
        # ショートバージョン作成チェックボックス
        short_check = ttk.Checkbutton(short_frame, text="ショートバージョンも作成", 
                                     variable=self.create_short_version)
        short_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # 動画長設定
        duration_frame = ttk.Frame(short_frame)
        duration_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        
        ttk.Label(duration_frame, text="動画長:").pack(side=tk.LEFT)
        duration_spinbox = ttk.Spinbox(duration_frame, from_=10, to=60, 
                                     textvariable=self.short_duration_seconds, width=10)
        duration_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(duration_frame, text="秒").pack(side=tk.LEFT, padx=(5, 0))
        
        # 説明ラベル
        info_label = ttk.Label(short_frame, text="※ Instagram Reels、TikTok、YouTube Shorts などに最適化", 
                              font=('Arial', 9), foreground='gray')
        info_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
    
    def select_bgm(self):
        """BGMファイルを選択"""
        filetypes = [
            ('音声ファイル', '*.mp3 *.wav *.m4a *.flac *.aac'),
            ('MP3ファイル', '*.mp3'),
            ('WAVファイル', '*.wav'),
            ('すべてのファイル', '*.*')
        ]
        filename = filedialog.askopenfilename(
            title="BGMファイルを選択",
            filetypes=filetypes
        )
        if filename:
            self.bgm_file.set(filename)
    
    def select_backgrounds(self):
        """背景画像・映像ファイルを選択"""
        filetypes = [
            ('画像・動画ファイル', '*.jpg *.jpeg *.png *.gif *.mp4 *.mov *.avi'),
            ('画像ファイル', '*.jpg *.jpeg *.png *.gif'),
            ('動画ファイル', '*.mp4 *.mov *.avi'),
            ('すべてのファイル', '*.*')
        ]
        filenames = filedialog.askopenfilenames(
            title="背景画像・映像を選択",
            filetypes=filetypes
        )
        if filenames:
            self.background_files.extend(filenames)
            self.update_background_list()
    
    def update_background_list(self):
        """背景ファイルリストを更新"""
        self.bg_listbox.delete(0, tk.END)
        for file in self.background_files:
            self.bg_listbox.insert(tk.END, os.path.basename(file))
    
    def remove_background(self):
        """選択された背景ファイルを削除"""
        selection = self.bg_listbox.curselection()
        if selection:
            index = selection[0]
            del self.background_files[index]
            self.update_background_list()
    
    def select_melody_files(self):
        """メドレー用の動画ファイルを選択"""
        filetypes = [
            ('動画ファイル', '*.mp4 *.mov *.avi'),
            ('MP4ファイル', '*.mp4'),
            ('すべてのファイル', '*.*')
        ]
        filenames = filedialog.askopenfilenames(
            title="メドレー用動画ファイルを選択",
            filetypes=filetypes
        )
        if filenames:
            self.melody_files = list(filenames)
            self.update_melody_list()
    
    def update_melody_list(self):
        """メドレーファイルリストを更新"""
        self.melody_listbox.delete(0, tk.END)
        for file in self.melody_files:
            self.melody_listbox.insert(tk.END, os.path.basename(file))
    
    def select_output_directory(self):
        """出力ディレクトリを選択"""
        directory = filedialog.askdirectory(title="出力フォルダを選択")
        if directory:
            self.output_directory.set(directory)
    
    def on_video_type_change(self):
        """動画タイプが変更された時の処理"""
        pass
    
    def validate_inputs(self):
        """入力値の検証"""
        if not self.video_title.get().strip():
            messagebox.showerror("エラー", "動画タイトルを入力してください。")
            return False
        
        if not self.bgm_file.get():
            messagebox.showerror("エラー", "BGMファイルを選択してください。")
            return False
        
        if not self.background_files:
            messagebox.showerror("エラー", "背景画像・映像を選択してください。")
            return False
        
        if not self.output_directory.get():
            messagebox.showerror("エラー", "出力フォルダを選択してください。")
            return False
        
        if self.video_type.get() == "melody" and not self.melody_files:
            messagebox.showerror("エラー", "メドレー用の動画ファイルを選択してください。")
            return False
        
        return True
    
    def create_video(self):
        """動画作成を開始"""
        if not self.validate_inputs():
            return
        
        # 設定を保存
        self.save_config()
        
        # 別スレッドで動画作成を実行
        thread = threading.Thread(target=self.create_video_thread)
        thread.daemon = True
        thread.start()
    
    def create_video_thread(self):
        """動画作成スレッド"""
        try:
            self.progress.start()
            self.status_label.config(text="動画作成エンジンを初期化中...")
            self.root.update()
            
            # 動画作成スクリプトを呼び出し
            from video_generator import VideoGenerator
            
            generator = VideoGenerator()
            
            self.status_label.config(text="動画を作成中...")
            self.root.update()
            
            video_type = self.video_type.get()
            video_title = self.video_title.get().strip()
            
            if video_type == "single":
                generator.create_single_video(
                    self.bgm_file.get(),
                    self.background_files,
                    self.output_directory.get(),
                    video_title
                )
                # ショートバージョンも作成
                if self.create_short_version.get():
                    generator.create_short_version(
                        self.bgm_file.get(),
                        self.background_files,
                        self.output_directory.get(),
                        self.short_duration_seconds.get(),
                        video_title
                    )
            elif video_type == "loop":
                generator.create_loop_video(
                    self.bgm_file.get(),
                    self.background_files,
                    self.output_directory.get(),
                    self.duration_minutes.get(),
                    video_title
                )
                # ショートバージョンも作成
                if self.create_short_version.get():
                    generator.create_short_version(
                        self.bgm_file.get(),
                        self.background_files,
                        self.output_directory.get(),
                        self.short_duration_seconds.get(),
                        video_title
                    )
            elif video_type == "melody":
                generator.create_melody_video(
                    self.melody_files,
                    self.background_files,
                    self.output_directory.get(),
                    video_title
                )
                # メドレーのショートバージョンは作成しない（複雑すぎるため）
            
            self.progress.stop()
            self.status_label.config(text="動画作成完了！")
            messagebox.showinfo("完了", "動画の作成が完了しました。")
            
        except Exception as e:
            self.progress.stop()
            self.status_label.config(text="エラーが発生しました")
            messagebox.showerror("エラー", f"動画作成中にエラーが発生しました:\n{str(e)}")

def main():
    """メイン関数"""
    root = tk.Tk()
    app = VideoCreatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 