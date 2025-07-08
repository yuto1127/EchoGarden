#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoGarden 動画作成ツール
BGMと背景画像を使用して動画を作成するGUIアプリケーション
"""

# Tkinterの非推奨警告を抑制
import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
from datetime import datetime
from pathlib import Path
import subprocess
import sys

class VideoCreatorApp:
    def __init__(self, root):
        print("VideoCreatorApp.__init__ 開始")
        try:
            print("1. root ウィンドウ設定")
            self.root = root
            self.root.title("EchoGarden 動画作成ツール")
            self.root.geometry("800x600")
            self.root.configure(bg='#f0f0f0')
            
            print("2. 変数を初期化中...")
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
            print("変数の初期化完了")
            
            print("3. 設定ファイルパス設定")
            # 設定ファイルの読み込み
            print("Path(__file__) を作成中...")
            current_file_path = Path(__file__)
            print(f"current_file_path: {current_file_path}")
            print("current_file_path.parent を取得中...")
            parent_dir = current_file_path.parent
            print(f"parent_dir: {parent_dir}")
            print("config.json パスを作成中...")
            self.config_file = parent_dir / "config.json"
            print(f"設定ファイルパス: {self.config_file}")
            
            print("4. ローディング画面を表示中...")
            # 起動時のローディング画面を表示
            self.show_loading_screen()
            print("ローディング画面表示完了")
            
            print("5. 初期化処理をスケジュール")
            # 初期化処理を非同期で実行（少し待機してから実行）
            self.root.after(500, self.init_app)
            print("VideoCreatorApp.__init__ 完了")
        except Exception as e:
            print(f"VideoCreatorApp.__init__ エラー: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def show_loading_screen(self):
        """起動時のローディング画面を表示"""
        print("show_loading_screen 開始")
        try:
            # ローディングフレーム
            self.loading_frame = ttk.Frame(self.root)
            self.loading_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            print("ローディングフレーム作成完了")
            
            # ロゴ・タイトル
            title_label = ttk.Label(self.loading_frame, text="EchoGarden", 
                                   font=('Arial', 24, 'bold'))
            title_label.pack(pady=(0, 10))
            print("タイトルラベル作成完了")
            
            subtitle_label = ttk.Label(self.loading_frame, text="動画作成ツール", 
                                      font=('Arial', 14))
            subtitle_label.pack(pady=(0, 30))
            print("サブタイトルラベル作成完了")
            
            # プログレスバー
            self.loading_progress = ttk.Progressbar(self.loading_frame, mode='indeterminate', 
                                                  length=300)
            self.loading_progress.pack(pady=(0, 20))
            print("プログレスバー作成完了")
            
            # ステータスラベル
            self.loading_status = ttk.Label(self.loading_frame, text="初期化中...", 
                                           font=('Arial', 10))
            self.loading_status.pack()
            print("ステータスラベル作成完了")
            
            # プログレスバーを開始
            self.loading_progress.start()
            print("プログレスバー開始")
            print("show_loading_screen 完了")
        except Exception as e:
            print(f"show_loading_screen エラー: {e}")
            import traceback
            traceback.print_exc()
    
    def init_app(self):
        """アプリケーションの初期化処理"""
        try:
            print("=== init_app 開始 ===")
            
            # 設定ファイルの読み込み
            print("1. 設定ファイル読み込み開始")
            print("loading_status の存在確認中...")
            if hasattr(self, 'loading_status'):
                print("loading_status 属性が存在します")
                if self.loading_status.winfo_exists():
                    print("loading_status ウィジェットが存在します、テキストを更新中...")
                    self.loading_status.config(text="設定ファイルを読み込み中...")
                    print("root.update_idletasks() を呼び出し中...")
                    self.root.update_idletasks()
                    print("root.update_idletasks() 完了")
                else:
                    print("loading_status ウィジェットが存在しません")
            else:
                print("loading_status 属性が存在しません")
            print("設定ファイルを読み込み中...")
            self.load_config()
            print("設定ファイルの読み込み完了")
            
            # メインウィジェットの作成
            print("2. GUIウィジェット作成開始")
            if hasattr(self, 'loading_status') and self.loading_status.winfo_exists():
                self.loading_status.config(text="GUIを初期化中...")
                self.root.update_idletasks()
            print("GUIを初期化中...")
            self.create_widgets()
            print("GUIの初期化完了")
            
            # ローディング画面を非表示
            print("3. ローディング画面非表示処理")
            if hasattr(self, 'loading_status') and self.loading_status.winfo_exists():
                self.loading_status.config(text="完了！")
                self.root.update_idletasks()
            print("初期化完了、ローディング画面を非表示")
            self.root.after(500, self.hide_loading_screen)
            print("=== init_app 正常完了 ===")
            
        except Exception as e:
            print(f"=== init_app エラー発生 ===")
            print(f"初期化エラー: {str(e)}")
            import traceback
            traceback.print_exc()
            if hasattr(self, 'loading_status') and self.loading_status.winfo_exists():
                self.loading_status.config(text=f"エラー: {str(e)}")
                self.root.update_idletasks()
            self.root.after(2000, self.show_error_and_exit, str(e))
    
    def hide_loading_screen(self):
        """ローディング画面を非表示にする"""
        print("hide_loading_screen 開始")
        try:
            # プログレスバーを停止
            if hasattr(self, 'loading_progress') and self.loading_progress.winfo_exists():
                print("プログレスバーを停止中...")
                self.loading_progress.stop()
                print("プログレスバー停止完了")
            
            # ローディングフレームを破棄
            if hasattr(self, 'loading_frame') and self.loading_frame.winfo_exists():
                print("ローディングフレームを破棄中...")
                self.loading_frame.destroy()
                print("ローディングフレーム破棄完了")
            
            # メインウィジェットを確実に表示
            print("メインウィジェットの表示を更新中...")
            self.root.update_idletasks()
            print("メインウィジェット表示更新完了")
            
            print("hide_loading_screen 完了")
        except Exception as e:
            print(f"hide_loading_screen エラー: {e}")
            import traceback
            traceback.print_exc()
    
    def show_error_and_exit(self, error_message):
        """エラーを表示して終了"""
        messagebox.showerror("起動エラー", f"アプリケーションの起動に失敗しました:\n{error_message}")
        self.root.destroy()
        
    def load_config(self):
        """設定ファイルを読み込む"""
        print("load_config 開始")
        try:
            print(f"設定ファイルパス確認: {self.config_file}")
            print("config_file.exists() を呼び出し中...")
            exists_result = self.config_file.exists()
            print(f"config_file.exists() 結果: {exists_result}")
            
            if exists_result:
                print("設定ファイルが存在します、読み込み開始")
                print("ファイルを開いています...")
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    print("ファイルを開きました、JSONを読み込み中...")
                    config = json.load(f)
                    print("JSON読み込み完了、変数に設定中...")
                    print(f"config内容: {config}")
                    
                    print("output_directory を設定中...")
                    self.output_directory.set(config.get('output_directory', ''))
                    print("create_short_version を設定中...")
                    self.create_short_version.set(config.get('create_short_version', False))
                    print("short_duration_seconds を設定中...")
                    self.short_duration_seconds.set(config.get('short_duration_seconds', 30))
                    print("video_title を設定中...")
                    self.video_title.set(config.get('video_title', ''))
                    print("設定ファイルを読み込みました")
            else:
                print("設定ファイルが存在しません、デフォルト設定を使用します")
            print("load_config 完了")
        except Exception as e:
            print(f"設定ファイルの読み込みエラー: {e}")
            import traceback
            traceback.print_exc()
            # エラーが発生してもデフォルト設定で続行
    
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
        print("create_widgets 開始")
        try:
            # ttkテーマを明示的に設定
            style = ttk.Style()
            style.theme_use('clam')

            print("1. メインフレーム作成")
            self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
            self.main_frame.pack(fill="both", expand=True)

            print("2. タイトルラベル作成")
            title_label = ttk.Label(self.main_frame, text="EchoGarden 動画作成ツール", font=('Arial', 16, 'bold'))
            title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

            print("3. タイトル入力セクション作成")
            self.create_title_section(self.main_frame, 1)

            print("4. BGM選択セクション作成")
            self.create_bgm_section(self.main_frame, 2)

            print("5. 背景画像選択セクション作成")
            self.create_background_section(self.main_frame, 3)

            print("6. 動画タイプ選択セクション作成")
            self.create_video_type_section(self.main_frame, 4)

            print("7. ショートバージョン設定セクション作成")
            self.create_short_version_section(self.main_frame, 5)

            print("8. 出力設定セクション作成")
            self.create_output_section(self.main_frame, 6)

            print("9. 作成ボタン作成")
            create_button = ttk.Button(self.main_frame, text="動画を作成", command=self.create_video, style='Accent.TButton')
            create_button.grid(row=7, column=0, columnspan=3, pady=20)

            print("10. プログレスバー作成")
            self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
            self.progress.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

            print("11. ステータスラベル作成")
            self.status_label = ttk.Label(self.main_frame, text="準備完了")
            self.status_label.grid(row=9, column=0, columnspan=3)

            print("12. グリッド重み設定")
            self.root.columnconfigure(0, weight=1)
            self.root.rowconfigure(0, weight=1)
            self.main_frame.columnconfigure(1, weight=1)

            print("create_widgets 完了")
        except Exception as e:
            print(f"create_widgets エラー: {e}")
            import traceback
            traceback.print_exc()
            raise
    
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
            self.status_label.config(text="FFmpegを確認中...")
            self.root.update_idletasks()
            
            # 動画作成スクリプトを呼び出し
            from video_generator import VideoGenerator
            
            generator = VideoGenerator()
            
            self.status_label.config(text="動画作成エンジンを初期化中...")
            self.root.update_idletasks()
            
            self.status_label.config(text="動画を作成中...")
            self.root.update_idletasks()
            
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
    print("=== main() 開始 ===")
    try:
        print("1. Tkinter root ウィンドウ作成")
        root = tk.Tk()
        print("2. VideoCreatorApp インスタンス作成")
        app = VideoCreatorApp(root)
        print("3. mainloop() 開始")
        root.mainloop()
        print("4. mainloop() 終了")
    except Exception as e:
        print(f"main() エラー: {e}")
        import traceback
        traceback.print_exc()
    print("=== main() 終了 ===")

if __name__ == "__main__":
    main() 