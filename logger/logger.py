# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/7/13 9:40 上午

import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler(f"{os.path.dirname(os.path.dirname(__file__))}/logs/log.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
