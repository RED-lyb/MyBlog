"""
网盘文件定时清理管理命令
每天0:00执行，删除files文件夹下最近修改时间超过7天的文件和文件夹

使用方法：
python manage.py cleanup_old_files

可以设置cron任务每天0:00执行：
0 0 * * * cd /webproject/my-blog/back && python3 manage.py cleanup_old_files
"""
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = '清理网盘files文件夹下超过7天未修改的文件和文件夹'

    def __init__(self):
        super().__init__()
        self.logger = None
        self.log_file_path = Path(settings.BASE_DIR/'..'/'log'/'back.log')
        self.max_log_size = 50 * 1024 * 1024  # 50MB

    def setup_logging(self):
        """设置日志记录，输出到文件"""
        # 确保日志目录存在
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 管理日志文件大小
        self.manage_log_size()
        
        # 配置logger
        self.logger = logging.getLogger('cleanup_old_files')
        self.logger.setLevel(logging.INFO)
        
        # 如果已经有handler，先清除
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 创建文件handler
        file_handler = logging.FileHandler(
            self.log_file_path,
            encoding='utf-8',
            mode='a'  # 追加模式
        )
        file_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        
        return self.logger

    def manage_log_size(self):
        """当日志文件超过50MB时，删除前50%的行"""
        if not self.log_file_path.exists():
            return
        
        try:
            file_size = self.log_file_path.stat().st_size
            
            if file_size >= self.max_log_size:
                warning_msg = (
                    f'日志文件大小: {file_size / 1024 / 1024:.2f}MB，'
                    f'超过限制 {self.max_log_size / 1024 / 1024}MB，开始清理...'
                )
                self.stdout.write(self.style.WARNING(warning_msg))
                
                # 使用临时文件方式，避免大文件一次性加载到内存
                temp_file = self.log_file_path.with_suffix('.tmp')
                total_lines = 0
                lines_to_skip = 0
                
                # 第一遍：统计总行数
                with open(self.log_file_path, 'r', encoding='utf-8') as f:
                    for _ in f:
                        total_lines += 1
                
                if total_lines > 0:
                    # 计算需要跳过的行数（前50%）
                    lines_to_skip = total_lines // 2
                    
                    # 第二遍：跳过前50%的行，写入剩余行到临时文件
                    with open(self.log_file_path, 'r', encoding='utf-8') as infile, \
                         open(temp_file, 'w', encoding='utf-8') as outfile:
                        for i, line in enumerate(infile):
                            if i >= lines_to_skip:
                                outfile.write(line)
                    
                    # 用临时文件替换原文件
                    temp_file.replace(self.log_file_path)
                    
                    success_msg = (
                        f'日志清理完成：删除了 {lines_to_skip} 行，'
                        f'保留了 {total_lines - lines_to_skip} 行'
                    )
                    self.stdout.write(self.style.SUCCESS(success_msg))
        except Exception as e:
            error_msg = f'管理日志文件大小时出错: {str(e)}'
            self.stdout.write(self.style.ERROR(error_msg))
            # 如果出错，尝试删除临时文件
            temp_file = self.log_file_path.with_suffix('.tmp')
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except:
                    pass

    def log_message(self, message, level='info', style=None):
        """将消息同时输出到控制台和日志文件"""
        # 输出到控制台
        if style:
            self.stdout.write(style(message))
        else:
            self.stdout.write(message)
        
        # 输出到日志文件
        if self.logger:
            # 移除ANSI颜色代码，只保留纯文本
            clean_message = message
            if level == 'info':
                self.logger.info(clean_message)
            elif level == 'warning':
                self.logger.warning(clean_message)
            elif level == 'error':
                self.logger.error(clean_message)
            else:
                self.logger.info(clean_message)

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='删除多少天前修改的文件（默认7天）'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示将要删除的文件，不实际删除'
        )
        parser.add_argument(
            '--no-log',
            action='store_true',
            help='不写入日志文件，仅输出到控制台'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        no_log = options.get('no_log', False)
        
        # 初始化日志（除非指定了 --no-log）
        if not no_log:
            self.setup_logging()
        
        # 网盘文件根目录
        network_disk_root = Path(settings.BASE_DIR) / 'api' / 'static' / 'files'
        
        if not network_disk_root.exists():
            msg = f'网盘目录不存在: {network_disk_root}'
            if no_log:
                self.stdout.write(self.style.WARNING(msg))
            else:
                self.log_message(msg, 'warning', self.style.WARNING)
            return
        
        # 计算截止时间（当前时间减去指定天数）
        cutoff_time = datetime.now() - timedelta(days=days)
        
        start_msg = f'开始清理 {days} 天前修改的文件...'
        cutoff_msg = f'截止时间: {cutoff_time.strftime("%Y-%m-%d %H:%M:%S")}'
        
        if no_log:
            self.stdout.write(self.style.SUCCESS(start_msg))
            self.stdout.write(cutoff_msg)
        else:
            self.log_message(start_msg, 'info', self.style.SUCCESS)
            self.log_message(cutoff_msg, 'info')
        
        if dry_run:
            dry_run_msg = 'DRY RUN 模式：仅显示，不删除'
            if no_log:
                self.stdout.write(self.style.WARNING(dry_run_msg))
            else:
                self.log_message(dry_run_msg, 'warning', self.style.WARNING)
        
        deleted_files = []
        deleted_dirs = []
        errors = []
        
        # 第一步：删除所有超过指定天数的文件
        step1_msg = f'删除超过{days}天的文件...'
        if no_log:
            self.stdout.write(step1_msg)
        else:
            self.log_message(step1_msg, 'info')
        
        try:
            for item in network_disk_root.rglob('*'):
                if item.is_file():
                    try:
                        # 获取最后修改时间
                        mtime = datetime.fromtimestamp(item.stat().st_mtime)
                        
                        # 如果修改时间早于截止时间，删除文件
                        if mtime < cutoff_time:
                            if not dry_run:
                                item.unlink()
                            deleted_files.append(str(item.relative_to(network_disk_root)))
                            delete_msg = f'{"[DRY RUN] " if dry_run else ""}删除文件: {item.relative_to(network_disk_root)}'
                            if no_log:
                                self.stdout.write(delete_msg)
                            else:
                                self.log_message(delete_msg, 'info')
                    except (OSError, PermissionError) as e:
                        error_msg = f'删除文件失败 {item}: {str(e)}'
                        errors.append(error_msg)
                        if no_log:
                            self.stdout.write(self.style.ERROR(error_msg))
                        else:
                            self.log_message(error_msg, 'error', self.style.ERROR)
        except Exception as e:
            error_msg = f'扫描文件过程出错: {str(e)}'
            errors.append(error_msg)
            if no_log:
                self.stdout.write(self.style.ERROR(error_msg))
            else:
                self.log_message(error_msg, 'error', self.style.ERROR)
        
        # 第二步：删除空文件夹（从最深层的文件夹开始，向上删除）
        step2_msg = f'删除超过{days}天且为空的文件夹...'
        if no_log:
            self.stdout.write('')
            self.stdout.write(step2_msg)
        else:
            self.log_message('', 'info')
            self.log_message(step2_msg, 'info')
        
        try:
            # 获取所有文件夹，按深度从深到浅排序
            all_dirs = []
            for item in network_disk_root.rglob('*'):
                if item.is_dir():
                    all_dirs.append(item)
            
            # 按路径深度排序（最深的在前）
            all_dirs.sort(key=lambda x: len(x.parts), reverse=True)
            
            for item in all_dirs:
                try:
                    # 检查文件夹是否仍然存在（可能已被删除）
                    if not item.exists():
                        continue
                    
                    # 获取最后修改时间
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    
                    # 如果修改时间早于截止时间
                    if mtime < cutoff_time:
                        # 检查文件夹是否为空
                        try:
                            contents = list(item.iterdir())
                            if len(contents) == 0:
                                # 空文件夹：删除
                                if not dry_run:
                                    item.rmdir()
                                deleted_dirs.append(str(item.relative_to(network_disk_root)))
                                delete_dir_msg = f'{"[DRY RUN] " if dry_run else ""}删除空文件夹: {item.relative_to(network_disk_root)}'
                                if no_log:
                                    self.stdout.write(delete_dir_msg)
                                else:
                                    self.log_message(delete_dir_msg, 'info')
                        except OSError as e:
                            # 文件夹可能已被删除或无法访问
                            pass
                except (OSError, PermissionError) as e:
                    error_msg = f'处理文件夹失败 {item}: {str(e)}'
                    errors.append(error_msg)
                    if no_log:
                        self.stdout.write(self.style.ERROR(error_msg))
                    else:
                        self.log_message(error_msg, 'error', self.style.ERROR)
        
        except Exception as e:
            error_msg = f'扫描过程出错: {str(e)}'
            errors.append(error_msg)
            if no_log:
                self.stdout.write(self.style.ERROR(error_msg))
            else:
                self.log_message(error_msg, 'error', self.style.ERROR)
        
        # 输出统计信息
        summary_separator = '-' * 50
        summary_complete = '清理完成'
        summary_files = f'删除文件数: {len(deleted_files)}'
        summary_dirs = f'删除文件夹数: {len(deleted_dirs)}'
        summary_errors = f'错误数: {len(errors)}' if errors else None
        
        if no_log:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS(summary_separator))
            self.stdout.write(self.style.SUCCESS(summary_complete))
            self.stdout.write(summary_files)
            self.stdout.write(summary_dirs)
            if errors:
                self.stdout.write(self.style.ERROR(summary_errors))
            self.stdout.write(self.style.SUCCESS(summary_separator))
        else:
            self.log_message('', 'info')
            self.log_message(summary_separator, 'info', self.style.SUCCESS)
            self.log_message(summary_complete, 'info', self.style.SUCCESS)
            self.log_message(summary_files, 'info')
            self.log_message(summary_dirs, 'info')
            if errors:
                self.log_message(summary_errors, 'error', self.style.ERROR)
            self.log_message(summary_separator, 'info', self.style.SUCCESS)
        
        if errors:
            error_detail_title = '错误详情:'
            if no_log:
                self.stdout.write('')
                self.stdout.write(self.style.ERROR(error_detail_title))
                for error in errors:
                    self.stdout.write(self.style.ERROR(f'  - {error}'))
            else:
                self.log_message('', 'info')
                self.log_message(error_detail_title, 'error', self.style.ERROR)
                for error in errors:
                    self.log_message(f'  - {error}', 'error', self.style.ERROR)

