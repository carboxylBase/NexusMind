import logging
import sys

def setup_logger(name: str = "NexusMind") -> logging.Logger:
    """
    配置并返回一个标准化的全局 Logger。
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加 Handler
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # 将日志输出到控制台
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 定义专业的日志格式：时间 - 模块名 - 级别 - 信息
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-7s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
    return logger

# 导出一个全局可用的 logger 实例
logger = setup_logger()