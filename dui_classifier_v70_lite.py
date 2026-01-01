#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对-Construction Hybrid Classifier (v70)
==========================================
A hybrid rule-based + BERT classifier for Chinese 对-constructions.

Version History:
- v59.x: Previous framework
- v60.0: NEW V60 THEORETICAL FRAMEWORK
- v60.1: Encoding fixes + MS/ABT refinements
- v60.2: COMPREHENSIVE FIX based on complete 617-error analysis
- v60.3: COGNITIVE STATE VERBS → MS + additional fixes
- v60.4: Comprehensive 有-pattern fixes based on training data analysis
- v60.5: Validation error analysis fixes
- v60.6: Cognitive STATE idioms + Institution Y + Action responses
- v60.7: 负责 pattern refinement + 施以 fix + speech verb fixes
- v60.8: DISP refinement - stative manner predicates only
- v67: CRITICAL FIX: 进行 → always SI; vague verb + person → DA
- v68: CONFIDENCE FIXES: 说+inanimate→ABT 0.92; DISP 0.94; name recognition
- v69: LOW CONFIDENCE FIXES: 有+恩→EVAL 0.92; 寄予→MS 0.93; DISP idioms 0.94
- v70: CRITICAL FIX: 说 reversed logic - default DA, only ABT if clearly inanimate

===========================================
V60.9 KEY CHANGES (CRITICAL FIXES)
===========================================

1. 进行 Pattern Fix (CRITICAL):
   - OLD: 进行 split between ABT (discourse) and SI (intervention)
   - NEW: 进行 → ALWAYS SI (procedural intervention)
   - Rationale: 进行 = "carry out/conduct/implement" is inherently procedural
   - Examples:
     * 对Y 进行 研究 → SI (conduct research ON Y - procedural)
     * 对Y 进行 分析 → SI (conduct analysis ON Y - intervention)
     * 对Y 进行 调查 → SI (conduct investigation ON Y - bounded procedure)
   - Impact: Fixes ~40-50 misclassifications

2. Vague Verb + Individual Person → DA (NEW RULE):
   - Pattern: 对[person] + [做/干/作] + [vague action] → DA (not SI)
   - Test: Short/vague complement + individual animate recipient
   - Examples:
     * 对他 做 了什么 → DA (do what TO him)
     * 对她 干 那事 → DA (do that TO her)
     * 对你 做出 什么 → DA (do something TO you)
   - Distinction from SI:
     * DA: Individual animate recipient + vague action directed TO
     * SI: Bounded domain + specific procedural intervention ON
   - Impact: Fixes ~120 SI→DA misclassifications

3. Expected Accuracy Improvement:
   - Before v67: ~78-82%
   - After v67: ~92-95% (estimated)
   - Fixed error patterns: ~170 cases

===========================================
V60 CORE THEORETICAL FRAMEWORK
===========================================

| Type | Definition | Key Test |
|------|------------|----------|
| ABT | X produces external discourse ABOUT Y | Y is reference point, NOT affected |
| MS | Y triggers mental/emotional state in X | Internal psychological response |
| SI | X intervenes ON/UPON Y | Y is AFFECTED by action |
| DA | X directs speech/action TO Y | Speech/gesture TO animate Y |
| DISP | Observable behavioral manner toward Y | External treatment style (STATIVE) |
| EVAL | Y has property/effect FOR X | Benefit/harm FOR Y |

Author: Jiaqi's Dui-construction Project
Date: December 2025
"""

import os
import re
import json
import logging
import warnings
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from collections import Counter
from tqdm import tqdm

import numpy as np
import pandas as pd
# from tqdm import tqdm  # Not needed for classification

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import (
    BertTokenizer,
    BertModel,
    BertPreTrainedModel,
    get_linear_schedule_with_warmup
)
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    f1_score
)
from sklearn.model_selection import train_test_split

warnings.filterwarnings('ignore')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# FEATURE EXTRACTION FROM CONCORDANCE
# ============================================================================

def extract_features_from_concordance(concordance: str) -> dict:
    """Extract Y, Predicate, Predicate+Complement, Y_Anim from concordance line."""
    result = {
        'Y': '',
        'Predicate': '',
        'Predicate+Complement': '',
        'Y_Anim': 'inan',
    }

    if not concordance or not isinstance(concordance, str):
        return result

    if '【对】' not in concordance:
        return result

    try:
        parts = concordance.split('【对】')
        if len(parts) < 2:
            return result

        after_dui = parts[1].strip()
        after_dui = re.sub(r'\s*[;；。,，!！?？]\s*$', '', after_dui).strip()
        space_parts = after_dui.split()

        if len(space_parts) >= 2:
            y_raw = space_parts[0]

            multi_strip = [
                '绝对不会', '根本不会', '完全不会', '简直不会',
                '为什么能', '为什么会', '怎么能', '怎么会',
                '越来越', '越发', '愈发', '愈来愈',
                '绝不会', '不可能', '禁不住', '忍不住', '受不了',
                '仍然是', '依然是', '还是很', '就是很',
                '已是全然', '已经是', '从来不', '永远不',
                '似乎是', '好像是', '简直是', '几乎是',
                '变得更', '显得更', '越来越', '愈来愈',
                '不会', '不能', '不敢', '不肯', '不想', '不愿', '不再',
                '会不', '能不', '敢不', '肯不', '想不', '愿不',
                '绝不', '全然', '全不', '毫不', '并不', '从不', '永不',
                '非常', '特别', '十分', '相当', '极其', '极为', '比较', '更加',
                '有点', '有些', '那么', '这么', '如此', '格外', '分外',
                '开始', '已经', '正在', '仍然', '依然', '似乎', '好像', '居然',
                '简直', '几乎', '总是', '往往', '常常', '经常', '始终', '一直',
                '热切', '迫切', '殷切', '极度', '高度', '深度',
                '变得', '显得', '越发', '愈发', '所有', '有所',
            ]

            for pattern in sorted(multi_strip, key=len, reverse=True):
                if y_raw.endswith(pattern) and len(y_raw) > len(pattern):
                    y_raw = y_raw[:-len(pattern)]
                    break

            single_strip = {'很', '更', '最', '太', '挺', '蛮', '颇', '极', '甚', '尤',
                            '也', '都', '就', '才', '又', '再', '还', '却', '倒', '便',
                            '能', '会', '敢', '肯', '想', '愿', '要', '可', '得',
                            '不', '没', '别', '莫', '勿'}

            while y_raw and y_raw[-1] in single_strip and len(y_raw) > 1:
                y_raw = y_raw[:-1]

            if y_raw.endswith('的') and len(y_raw) > 2:
                y_raw = y_raw[:-1]

            result['Y'] = y_raw
            result['Y_Anim'] = detect_y_animacy(y_raw)
            result['Predicate'] = space_parts[1]
            result['Predicate+Complement'] = ''.join(space_parts[1:])

        elif len(space_parts) == 1:
            result['Y'] = space_parts[0]
            result['Y_Anim'] = detect_y_animacy(space_parts[0])

    except Exception as e:
        logger.debug(f"Feature extraction error: {e}")

    return result


def detect_y_animacy(y_phrase: str) -> str:
    """Detect animacy of Y phrase based on head noun."""
    if not y_phrase:
        return 'inan'

    y_clean = y_phrase.strip()

    pronouns = {'我', '你', '他', '她', '您', '咱', '它', '我们', '你们', '他们', '她们', '咱们',
                '自己', '本人', '人家', '别人', '大家', '各位', '谁', '某人', '有人', '对方'}
    if y_clean in pronouns:
        return 'anim'

    if '的' in y_clean:
        parts = y_clean.rsplit('的', 1)
        if len(parts) == 2 and parts[1]:
            head_noun = parts[1]
            inan_suffixes = {'情', '事', '物', '品', '件', '象', '况', '态', '式', '法',
                             '论', '学', '性', '化', '度', '量', '率', '值', '感', '心',
                             '意', '念', '想', '见', '为', '动', '作', '行', '举', '措',
                             '策', '案', '题', '问', '难', '赞', '评', '议', '说', '话',
                             '子', '气', '力', '能', '用', '效', '果', '响', '益', '害', '姻'}
            if head_noun and head_noun[-1] in inan_suffixes:
                return 'inan'

    inan_nouns = {'事', '事情', '问题', '情况', '现象', '结果', '政策', '制度', '措施',
                  '方法', '做法', '方案', '计划', '工作', '任务', '项目', '活动', '行动',
                  '社会', '国家', '市场', '经济', '发展', '生活', '婚姻', '利率', '反应'}
    for noun in inan_nouns:
        if y_clean.endswith(noun):
            return 'inan'

    inan_suffixes = {'情', '事', '物', '品', '件', '象', '况', '态', '式', '法', '论', '学',
                     '性', '化', '度', '量', '率', '值', '感', '心', '意', '念', '想', '见',
                     '为', '动', '作', '行', '举', '措', '策', '案', '题', '问', '难', '姻'}
    if len(y_clean) >= 2 and y_clean[-1] in inan_suffixes:
        return 'inan'

    human_roles = {'人', '人们', '学生', '老师', '医生', '患者', '观众', '读者', '孩子',
                   '父母', '朋友', '同事', '客人', '员工', '领导', '群众', '民众', '百姓'}
    for role in human_roles:
        if y_clean.endswith(role) or y_clean == role:
            return 'anim'

    if 2 <= len(y_clean) <= 3:
        if not any(y_clean.endswith(s) for s in inan_suffixes):
            return 'anim'

    if len(y_clean) > 6:
        return 'inan'

    return 'inan'


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class Config:
    """Configuration for the hybrid classifier."""

    data_file: str = "training_data_v67.xlsx"
    output_dir: str = "./output"
    model_save_path: str = "./output/best_model_v67.pt"

    train_ratio: float = 0.80
    dev_ratio: float = 0.10
    test_ratio: float = 0.10

    col_concordance: str = "Concordance"
    col_predicate: str = "Predicate"
    col_pred_comp: str = "Predicate+Complement"
    col_y: str = "Y"
    col_y_anim: str = "Y_Anim"
    col_type: str = "Type"
    col_conf: str = "Conf"
    col_reason: str = "Reason"

    bert_model_name: str = "hfl/chinese-roberta-wwm-ext"
    max_seq_length: int = 128
    batch_size: int = 32
    learning_rate: float = 2e-5
    num_epochs: int = 5
    warmup_ratio: float = 0.1
    dropout_rate: float = 0.3

    rule_confidence_threshold: float = 0.90
    bert_confidence_threshold: float = 0.85

    labels: List[str] = field(default_factory=lambda: ["DA", "SI", "MS", "ABT", "DISP", "EVAL"])

    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    seed: int = 42


# ============================================================================
# DATA SPLITTING
# ============================================================================

def create_stratified_splits(df, config, save_splits=True):
    """Create stratified Train/Dev/Test splits from the data."""
    logger.info("=" * 60)
    logger.info("Creating Stratified Data Splits")
    logger.info("=" * 60)

    df = df.copy()
    df[config.col_type] = df[config.col_type].str.upper()
    df = df[df[config.col_type].isin(config.labels)]
    logger.info(f"Total instances: {len(df)}")

    train_dev_df, test_df = train_test_split(
        df, test_size=config.test_ratio, random_state=config.seed,
        stratify=df[config.col_type]
    )

    dev_size_adjusted = config.dev_ratio / (config.train_ratio + config.dev_ratio)
    train_df, dev_df = train_test_split(
        train_dev_df, test_size=dev_size_adjusted, random_state=config.seed,
        stratify=train_dev_df[config.col_type]
    )

    logger.info(f"Train: {len(train_df)}, Dev: {len(dev_df)}, Test: {len(test_df)}")

    if save_splits:
        os.makedirs(config.output_dir, exist_ok=True)
        train_df.to_excel(os.path.join(config.output_dir, "train_split_v67.xlsx"), index=False)
        dev_df.to_excel(os.path.join(config.output_dir, "dev_split_v67.xlsx"), index=False)
        test_df.to_excel(os.path.join(config.output_dir, "test_split_HOLDOUT_v67.xlsx"), index=False)

    return train_df, dev_df, test_df


def preprocess_dataframe(df, config):
    """Preprocess dataframe: extract features from Concordance if missing columns."""
    required_cols = [config.col_predicate, config.col_y, config.col_y_anim]
    missing_cols = [col for col in required_cols if col not in df.columns or df[col].isna().all()]

    if missing_cols and config.col_concordance in df.columns:
        logger.info(f"Extracting features from Concordance (missing: {missing_cols})")
        features_list = []
        for idx, row in df.iterrows():
            conc = str(row[config.col_concordance]) if pd.notna(row[config.col_concordance]) else ''
            features = extract_features_from_concordance(conc)
            features_list.append(features)
        features_df = pd.DataFrame(features_list)

        if config.col_y not in df.columns or df[config.col_y].isna().all():
            df[config.col_y] = features_df['Y']
        if config.col_predicate not in df.columns or df[config.col_predicate].isna().all():
            df[config.col_predicate] = features_df['Predicate']
        if config.col_pred_comp not in df.columns or df[config.col_pred_comp].isna().all():
            df[config.col_pred_comp] = features_df['Predicate+Complement']
        if config.col_y_anim not in df.columns or df[config.col_y_anim].isna().all():
            df[config.col_y_anim] = features_df['Y_Anim']

    return df


# ============================================================================
# RULE-BASED CLASSIFIER (v67)
# ============================================================================

class RuleBasedClassifier:
    """Rule-based classifier implementing v67 specifications."""

    def __init__(self):
        self._init_lexicons()

    def _init_lexicons(self):
        """Initialize all lexicons based on v67 framework."""

        # ================================================================
        # FIX #1: 具有 + significance → EVAL
        # ================================================================
        self.JUYOU_SIGNIFICANCE_EVAL = {
            '意义', '作用', '价值', '影响', '效果', '效应', '疗效',
            '威慑力', '约束力', '吸引力', '诱惑', '吸引', '促进作用',
            '指导意义', '战略意义', '重要性', '抑制性', '深远影响',
            '巨大意义', '重大意义', '现实意义', '借鉴意义', '参考价值',
            '指导作用', '推动作用', '标本意义', '经济意义', '积极作用',
            '重要作用', '示范意义', '挑战性', '性质', '建设性',
            '相当大', '较好', '兼', '历', '现实',
        }

        # ================================================================
        # V60.9: 进行 complements (NO LONGER USED - 进行 always SI)
        # Kept for reference/documentation only
        # ================================================================
        self.JINXING_DISCOURSE_ABT_DEPRECATED = {
            '分析', '研究', '讨论', '评论', '报道', '梳理', '挖掘',
            '答辩', '直播', '调研', '评价', '阐述', '论述', '描述',
            '反省', '抨击', '批驳', '批判', '宣传', '研讨', '统计',
            '摸底', '学习', '鉴定', '介绍', '诊断', '唱评', '追究',
            '视察', '评述', '总结', '推荐', '计算', '界定', '调查',
            '讲评',
        }

        self.JINXING_INTERVENTION_SI_DEPRECATED = {
            '打击', '处理', '训练', '教育', '改造', '整治',
            '投票', '采访', '帮助', '非礼', '劝说', '嘱托',
            '宣传教育', '随访调研', '退款', '拥抱', '讴歌',
            '整理', '积累',
        }

        # ================================================================
        # FIX #3: 提出 + discourse → ABT
        # ================================================================
        self.TICHU_DISCOURSE_ABT = {
            '建议', '方案', '批评', '抗议', '意见',
            '看法', '观点', '主张', '提案', '议案', '质疑',
        }

        # ================================================================
        # FIX #4: 作出 + discourse → ABT
        # ================================================================
        self.ZUOCHU_DISCOURSE_ABT = {
            # Judgment/evaluation outputs
            '预报', '决定', '定位', '再现', '判断',
            '评价', '解释', '说明', '分析', '结论', '诊断',
            # Expanded discourse outputs
            '回应', '回答', '答复', '表态', '表示', '声明', '阐述',
            '预测', '预言', '推测', '估计', '推断', '论断', '判定',
            '总结', '概括', '归纳', '描述', '噪述', '陈述',
            '评论', '评估', '鉴定', '认定', '裁定',
            '反应', '反馈', '响应',  # response outputs
        }

        # ================================================================
        # FIX #5: 给予 patterns
        # ================================================================
        self.JIYU_DISCOURSE_ABT = {
            '肯定', '评价', '关注', '重视', '高度评价', '充分肯定', '好评', '高度',
        }

        self.JIYU_ACTION_DA = {
            '指导', '帮助', '关照', '支持', '援助', '奖励',
        }

        # ================================================================
        # FIX #6: Speech verbs + animate Y → DA
        # ================================================================
        self.SPEECH_ACTION_TO_DA = {
            '提供', '感谢', '致歉', '下达', '送', '赞美', '嘲弄',
            '顶撞', '献计', '指责', '表扬', '批评',
            # NOTE v60.8: 施以 removed - training 87% SI, always intervention ON Y
            '说明', '解释', '交代', '隐瞒', '否认', '告诉', '汇报',
            '报告', '通知', '宣布', '说', '讲', '介绍', '启发',
        }

        # ================================================================
        # FIX #7: Emotional states → MS
        # ================================================================
        self.EMOTIONAL_STATES_MS = {
            '屈服', '迷惑',
            '好感', '感情', '保留',
            '持态度', '抱着', '怀揣', '期盼', '狂热', '死心',
            '生闷气', '戒备', '防备', '警惕', '放松警惕',
            '弄懂', '没概念',
            '注重', '用心', '有意向',
        }

        # ================================================================
        # V60.4: Comprehensive 有-pattern lexicons
        # 有 is a LIGHT VERB - complement determines construction type
        # ================================================================

        # 有 + EVAL complements (effect/significance FOR Y)
        self.YOU_EVAL_COMPS = {
            # Effect/impact
            '影响', '作用', '效果', '效应', '意义', '价值', '贡献',
            '好处', '益处', '害处', '坏处', '危害', '损害', '利', '弊',
            '用', '用处', '用途', '帮助', '启发', '启示', '借鉴',
            # Significance
            '吸引力', '说服力', '感染力', '约束力', '执行力',
            '可能', '前途', '前景', '出路', '市场',
            # Pressure/support (effect on Y)
            '压力', '支撑', '冲击', '威胁',
            # Obligation FOR Y
            '义务',
            # NOTE: '希望' moved to MS (internal emotional state)
        }

        # 有 + SI complements (bounded scope/control ON Y)
        self.YOU_SI_COMPS = {
            # Institutional control
            '管辖权', '控制权', '所有权', '主权', '决定权', '否决权',
            '监护权', '处分权', '裁判权', '管理权', '支配权',
            # Regulations/constraints
            '规范', '限制', '约束', '制约', '束缚',
            # Administrative actions
            '反馈', '安排', '部署', '处理', '调整',
            # Resistance (bounded response)
            '抗性', '耐药性', '抵抗力', '免疫力',
            # Targets/goals ON scope
            '目标', '指标',
        }

        # 有 + DA complements (speech act results TO animate Y)
        self.YOU_DA_COMPS = {
            '交代', '暗示', '指示', '嘱咐', '婉咐',
            '答复', '回复', '回应',
            '建议', '指导', '批评', '表扬',
        }

        # 有 + DISP complements (manner TOWARD animate Y)
        self.YOU_DISP_COMPS = {
            '距离', '隔阂', '隔膜',  # interpersonal distance
            '礼貌', '礼', '耐心', '耐性', '诚意', '敬意', '善意', '恶意',
            '笑意', '笑容', '好脸色',
            '义气', '情义', '恩情',  # interpersonal manner
        }

        # 有 + ABT complements (discourse/opinion ABOUT Y)
        self.YOU_ABT_COMPS = {
            # Knowledge production (external, expressible)
            '研究', '心得', '体验', '发现', '认知',
            # Analysis/evaluation (discourse production)
            '评价', '分析', '判断', '论述', '总结', '描述',
            # Method/approach
            '招', '招数', '手段', '对策', '措施',
            # Institutional discourse
            '规定', '规则', '定论',
            # Critique (discourse production)
            '微词', '批判', '揭露',
        }

        # Patterns that should only match in pred_comp (not concordance)
        self.YOU_ABT_STRICT_COMPS = {
            '计划', '安排', '部署', '指示', '嘱咐', '责任',
        }

        # 有 + MS complements (internal psychological state)
        self.YOU_MS_COMPS = {
            # Opinion/view (internal stance, NOT discourse production)
            '看法', '观点', '见解', '高见', '见地', '主张', '意见',
            # Cognitive states (internal, Y as stimulus)
            '了解', '认识', '理解', '印象', '记忆', '概念', '把握',
            '成见', '偏见',  # biased cognitive state
            # Internal ability/capacity
            '办法', '方法', '能力', '天分', '才能',
            # Emotional states
            '好感', '恶感', '反感', '厌恶', '敌意', '戒心', '戒备',
            '好奇', '好奇心', '兴趣', '热情', '激情', '感情', '深情',
            '信心', '信任', '信赖', '依赖', '依恋', '眷恋', '留恋',
            '同情', '同情心', '怜悯', '慈悲',
            '期待', '期望', '期盼', '向往', '憧憬', '幻想', '希望',
            '怀疑', '疑虑', '疑惧', '顾虑', '担忧', '担心',
            '不满', '怨言', '怨气', '异议',
            # Feeling/sensation (full words only, not single chars)
            '感觉', '感受', '感触', '体会', '反应',
            # Internal planning (mental, not external arrangements)
            '想法', '念头', '打算', '意向', '意愿', '企图', '野心',
            '准备',  # mental readiness
            # Heart-related internal states
            '心态', '心意', '心理', '心思',
            '虚荣心', '进取心', '上进心', '责任心', '事业心',
            # Internal evaluative states (full words)
            '讲究', '追求',
        }

        # 有所 + action → SI
        self.YOUSUO_SI_COMPS = {
            '处理', '改变', '调整', '行动', '作为', '限制',
            '改善', '提高', '增加', '减少', '收敛', '节制',
            '牺牲', '付出', '贡献',
            '促进', '推动', '帮助',
        }

        # 有所 + cognitive → MS
        self.YOUSUO_MS_COMPS = {
            '了解', '认识', '感悟', '体会', '领悟', '察觉', '保留',
            '理解', '把握', '准备', '顾虑', '怀疑',
        }

        # 有所 + selection/choice → ABT (selective attitude)
        self.YOUSUO_ABT_COMPS = {
            '选择', '侧重', '偏重', '取舍',
        }

        # ================================================================
        # FIX #9: Manner expressions → DISP
        # ================================================================
        self.MANNER_EXPRESSIONS_DISP = {
            '一样', '不苟言笑', '真心实意', '惺惺相惜', '刮目相视',
            '视而不见', '视若无睹', '不予理睬', '不予理会',
        }

        # ================================================================
        # FIX #10: 不予 → ABT patterns
        # ================================================================
        self.BUYU_ABT_PATTERNS = {
            '理睬', '理会', '置评', '评论', '回应',
        }

        # ================================================================
        # V60.3: Cognitive STATE verbs → MS
        # ================================================================
        self.COGNITIVE_STATE_MS_VERBS = {
            # Core knowledge states (Y triggers knowledge in X)
            '了解', '理解', '认识', '熟悉', '知道', '知晓', '明白', '懂', '懂得',
            '掌握', '把握', '洞悉', '洞察', '通晓', '深知', '获悉', '悉知',
            # Memory states (Y triggers memory in X)
            '记得', '记住', '忆起', '想起', '回忆', '回想', '追忆',
            # Complete knowledge idioms
            '一无所知', '略知', '略知一二', '心知肚明', '了若指掌',
            # V60.3: Internal deliberation (no output, internal process)
            '考虑', '估计', '琢磨', '思量', '思考', '斟酌',
        }

        # Core Lexicons - Cognitive ACTIVITY verbs (produce output) → ABT
        self.COGNITIVE_ABT_VERBS = {
            # Prediction/estimation (produces judgments about Y)
            '判断', '推测', '预测', '预料', '预期', '预见', '猜测',
        }

        self.DISCOURSE_ABT_VERBS = {
            # Research/study (pure discourse production, not speech TO)
            '研究', '调查', '考察', '探讨', '分析', '调研', '考证',
            # Evaluation (produces evaluation output)
            '评价', '评论', '评述', '评判', '唱评', '点评',
            '评估', '评定', '评分', '评级',
            # Discussion (debate ABOUT topic, not speech TO person)
            '讨论', '辩论', '争论', '争议', '议论', '商议', '商讨',
            # Reporting (when no recipient specified)
            '报道', '陈述', '噪述', '阐述', '论述',
            '置评', '发言', '表态', '发表意见', '发表看法',
        }

        self.STANCE_ABT_VERBS = {
            '负有', '负有责任', '承担责任', '担负', '肩负', '背负',
            '适用', '适用于', '针对', '面向', '涉及',
        }

        self.ABT_IDIOMS = {
            # Cognitive dismissal/indifference (discourse stance)
            '不以为然', '不以为意', '不解', '不理解', '不明白',
            '不置可否', '无所谓', '置若罔闻', '充耳不闻',
            '不予置评', '不予评论', '不予回应',
            # Cognitive ignorance (training: ABT majority)
            '一窍不通',
            # Empathetic understanding
            '感同身受', '感到不解',
        }

        # V60.6: Cognitive STATE idioms → MS (training data MS-majority)
        self.COGNITIVE_STATE_IDIOMS_MS = {
            '了如指掌',  # Training: MS=14, ABT=5
            '心知肚明',  # Training: MS=2
            '心中有数',  # state of understanding
        }

        # Emotional avoidance idioms → MS (not ABT)
        self.EMOTIONAL_AVOIDANCE_MS = {
            '讳莫如深',  # emotional avoidance, not cognitive
        }

        self.FEELING_MARKERS = {'感到', '觉得', '感觉', '深感', '倍感', '感'}

        self.EMOTIONAL_RESPONSE_VERBS = {
            '喜欢', '喜爱', '爱', '热爱', '深爱', '钟爱', '宠爱', '溺爱', '偏爱',
            '爱慕', '仰慕', '倾慕', '爱恋', '迷恋', '眷恋', '留恋',
            '思念', '想念', '怀念', '眷念', '牵挂', '挂念', '惦记', '惦念',
            '害怕', '恐惧', '畏惧', '惧怕', '惊惧', '惶恐', '畏缩',
            '担心', '担忧', '操心', '忧虑', '焦虑', '顾虑', '忧心',
            '讨厌', '厌恶', '厌烦', '嫌恶', '嫌弃', '反感', '抵触',
            '痛恨', '憎恨', '仇恨', '憎恶',
            '感激', '感恩', '怨恨', '记恨', '记仇', '怀恨',
            '着迷', '入迷', '上瘾', '沉迷', '痴迷',
            '期待', '期望', '企盼', '盼望', '渴望', '向往', '憧憬', '指望',
            '满意', '不满', '失望', '绝望',
            '佩服', '敬佩', '钦佩', '崇拜', '景仰',
            '嫉妒', '羡慕', '眼红',
            '放心', '安心', '揪心', '伤心', '死心',
            '动心', '动情', '动容', '动怒',
            '错愕', '惊愕', '诧异', '惊讶', '惊奇',
        }

        self.CONSCIOUS_ENGAGEMENT_MS_VERBS = {
            '重视', '注意', '关注', '留意', '在意', '在乎', '介意',
            '忽视', '无视', '漠视',
        }

        self.INTERNAL_PSYCH_MS_VERBS = {
            '尊重', '尊敬', '敬重', '不敬', '敬畏', '尊崇', '崇敬', '崇尚',
            '器重', '看重', '重视', '珍视', '珍重', '青睐', '眷顾', '垂青',
            '关心', '关怀', '关切', '挂心', '怜悯', '同情', '慈悲', '悲悯',
            '信任', '信赖', '依赖', '倚重', '蔑视', '鄙视', '轻视', '藐视',
            '不屑', '瞧不起', '看不起', '冷落', '疏远', '疏忽', '赞赏', '欣赏',
        }

        self.LOYALTY_MS_VERBS = {
            '忠', '忠诚', '忠心', '忠实', '忠贞', '效忠', '尽忠', '赤胆忠心', '忠心耿耿',
        }

        self.INSTITUTIONAL_SI_VERBS = {
            '保护', '监管', '管制', '软禁', '限制', '约束',
            '审查', '审批', '批准', '核准', '许可', '授权',
            '整顿', '改革', '治理', '管控', '管辖', '督促',
            '处理', '处置', '处罚', '惩罚', '惩处',
            '制裁', '打击', '整治', '查处',
            '检查', '核查', '稽查', '督查',
            '使用', '采用', '运用', '利用',
        }

        self.CARE_SI_VERBS = {
            '照顾', '照料', '关照', '照看', '照应', '看护', '护理', '伺候',
            '服侍', '侍奉', '侍候', '奉养', '赡养', '抚养', '养育',
            '帮助', '援助', '救助', '扶助', '协助', '辅助',
            '保护', '维护', '捍卫', '守护', '呵护', '爱护',
            '慰问', '安慰', '劝慰', '感谢', '致谢',
            # v60.8: 道歉/致歉 moved to COMMUNICATIVE_VERBS (speech act TO person)
            '培训', '训练', '教育', '培养',
        }

        self.OPPOSITION_SI_VERBS = {
            '反抗', '抵抗', '对抗', '抗争', '斗争', '抵制', '反对', '违抗',
            '攻击', '袭击', '进攻', '打击', '拒绝', '抗拒', '排斥',
        }

        self.TOLERANCE_SI_VERBS = {
            '担待', '原谅', '包容', '宽恕', '体谅', '迁就', '忍让',
            '谅解', '饶恕', '宽待', '宽宥', '容忍', '忍受', '容纳', '宽容',
        }

        self.POLICY_SI_VERBS = {
            '实行', '实施', '执行', '施行', '采用',
            '推行', '贯彻', '落实', '开展', '展开',
            '征收', '加征', '设限', '开放', '投资',
        }

        self.CONTROL_SI_VERBS = {
            '控制', '管', '管理', '掌控', '操控', '驾驭', '把控',
            '约束', '规范', '制约', '支配', '主宰', '左右',
            '奈何', '丢', '弃', '抛弃', '放弃',
        }

        # ================================================================
        # V60.8: Reclassified from DISP → SI (Active Verbs V他✓)
        # ================================================================
        self.FORMER_DISP_NOW_SI_VERBS = {
            '对待',  # 对待他✓
            '保持',  # Active maintaining
            '留情',  # Affects Y
            '苛求',  # 苛求他✓
            '优待',  # 优待他✓
            '接待',  # 接待他✓
            '招待',  # 招待他✓
            '款待',  # 款待他✓
            '纵容',  # 纵容他✓
            '放纵',  # 放纵他✓
            '放任',  # 放任他✓
            '避',  # Active avoiding
            '避而远之',  # Active avoiding
            '摆',  # Active posturing (except 摆架子)
        }

        # ================================================================
        # V60.8: Reclassified from DISP → MS (Internal States)
        # ================================================================
        self.FORMER_DISP_NOW_MS_IDIOMS = {
            '不理不睬',  # Internal disregard
            '视而不见',  # Internal disregard
            '视若无睹',  # Internal disregard
            '不闻不问',  # Internal disregard
            '熟视无睹',  # Internal disregard
            '睁一只眼闭一只眼',  # Internal choice to ignore
            '有求必应',  # Internal willingness
        }

        self.FORMER_DISP_NOW_MS_VERBS = {
            '疼爱',  # Emotional love (Y triggers)
            '敬',  # Internal respect (Y triggers)
            '敬爱',  # Internal respect (Y triggers)
            '吝于',  # Internal reluctance
        }

        # V60.4: Gesture verbs → DA with animate Y
        self.GESTURE_DA_VERBS = {
            '摇', '点', '摇头', '点头', '挥手', '招手', '摆手',
            '瞪', '瞥', '盯', '注视', '凝视',
        }

        self.INHERENT_ADDRESSEE_VERBS = {
            '呵斥', '斥责', '训斥', '责骂', '怒斥', '痛斥',
            '喝止', '喝令', '骂', '辱骂', '臭骂',
            '请求', '祈求', '央求', '哀求', '乞求',
        }

        self.SPEECH_DAO_VERBS = {
            '笑道', '哭道', '说道', '问道', '答道', '叫道', '喊道',
            '骂道', '怒道', '冷道', '淡道', '道',
            '低声道', '大声道', '高声道', '轻声道', '厉声道',
            '冷冷道', '淡淡道', '怒喝道', '冷声道',
        }

        self.COMMUNICATIVE_VERBS = {
            '说', '讲', '谈', '聊', '问', '答', '告诉', '通知', '报告',
            '解释', '说明', '介绍', '描述', '陈述',
            '表达', '表示', '表明', '声明', '宣布', '宣称', '发表',
            '提出', '提议', '建议', '呼吁', '号召',
            '下达', '传达', '转达', '汇报', '反映', '反馈',
            '批评', '称赞', '赞扬', '夸奖', '责备', '指责', '责怪',
            '表扬', '嘉奖', '褒奖', '鼓励', '激励', '勉励',
            '警告', '告诫', '劝告', '劝诫', '训诫', '教训', '训斥', '斥责',
            '报道', '报导', '交代', '隐瞒', '否认',
            '道歉', '致歉',  # v60.8: speech acts TO person (training 83% DA)
        }

        # V60.6: Institutions that can receive speech acts (metonymy)
        self.INSTITUTION_Y = {
            # Government/political bodies
            '朝廷', '政府', '当局', '官方', '国会', '议会', '人大', '政协',
            # Legal institutions
            '法院', '法庭', '检察院', '公安', '警方',
            # Media organizations
            '媒体', '报馆', '报社', '电视台', '记者', '新闻界',
            # Organizations/enterprises
            '公司', '企业', '单位', '机构', '组织', '委员会', '协会',
            '学校', '医院', '银行', '工厂', '部门',
            # Abstract collectives (addressable via metonymy)
            '世界', '社会', '公众', '外界', '舆论',
        }

        self.SIMILE_VERBS = {
            '像', '象', '如', '如同', '宛如', '犹如', '好像', '好似', '仿佛',
            '类似', '相似', '相像', '近似', '形似', '神似',
            '酷似', '酷肖', '活像', '活似',
        }

        # ================================================================
        # V60.8: REFINED DISP - STATIVE manner predicates ONLY
        # ================================================================
        self.PURE_MANNER_DISP_VERBS = {
            '热情', '冷淡', '冷漠', '热心', '客气', '礼貌', '有礼貌', '没礼貌',
            '温柔', '柔和', '和蔼', '亲切', '慈祥',
            '粗暴', '粗鲁', '蛮横', '野蛮', '霸道',
            '体贴', '细心', '周到', '殷勤',
            '严厉', '苛刻', '严苛', '严酷', '刻薄',
            '真诚', '诚恳', '坦诚', '直率', '坦白', '坦率',
            '公道', '厚道', '地道',
            '不理不睬', '言听计从', '唯命是从', '百依百顺',
            '呼来唤去', '说打就打', '颐指气使', '克尽妇道',
            '恭敬', '恭顺', '毕恭毕敬', '孝顺', '顺从', '服从',
            '敷衍', '漠视', '无视', '忽视',
            '松', '紧', '严', '宽', '软', '硬',
            # V69: Add manner idioms found in low confidence cases
            '恩爱', '专情', '真心', '偏袒', '袒护', '严肃',
        }

        # V60.8: Treatment verbs that are STATIVE → DISP
        self.TREATMENT_VERBS = {
            '待', '对待', '善待', '厚待', '薄待', '优待', '虐待', '款待', '招待',
            '相待', '看待', '接待', '应付', '应对',
        }

        self.EFFECT_VERBS = {
            '造成', '导致', '引起', '带来', '促进', '阻碍', '构成', '影响', '触动', '刺激',
        }

        self.EVAL_PREDICATES = {
            '灵', '不灵', '有效', '无效', '有用', '无用', '管用', '好使',
            '重要', '必要', '关键', '至关重要',
            '有利', '有害', '有益', '有意义',
            '适用', '实用', '中用', '顶用', '可行', '不行', '适合', '合适',
            '微不足道',
        }

        self.FAIRNESS_EVAL_PREDICATES = {
            '公平', '公正', '平等', '不公', '不公平', '不公正', '一视同仁',
        }

        self.ANIMATE_Y_MARKERS = {
            '我', '你', '他', '她', '您', '我们', '你们', '他们', '她们',
            '自己', '本人', '人家', '别人', '大家', '咱', '咱们',
            '人', '人们', '学生', '老师', '客户', '患者', '观众', '读者',
            '孩子', '父母', '朋友', '同事', '邻居', '客人', '医生', '护士',
            '群众', '民众', '百姓', '大众', '公众', '员工', '领导',
            '父亲', '母亲', '儿子', '女儿', '妻子', '丈夫', '哥哥', '姐姐',
        }

        # V68: Common Chinese surnames for name detection
        self.COMMON_SURNAMES = {
            '李', '王', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴',
            '徐', '孙', '马', '胡', '朱', '郭', '何', '林', '罗', '高',
            '梁', '郑', '谢', '韩', '唐', '冯', '于', '董', '萧', '程',
            '曹', '袁', '邓', '许', '傅', '沈', '曾', '彭', '吕', '苏',
            '卢', '蒋', '蔡', '贾', '丁', '魏', '薛', '叶', '阎', '余',
            '潘', '杜', '戴', '夏', '钟', '汪', '田', '任', '姜', '范',
            '方', '石', '姚', '谭', '廖', '邹', '熊', '金', '陆', '郝',
            '孔', '白', '崔', '康', '毛', '邱', '秦', '江', '史', '顾',
            '侯', '邵', '孟', '龙', '万', '段', '漕', '钱', '汤', '尹',
            '黎', '易', '常', '武', '乔', '贺', '赖', '龚', '文', '庞',
        }

        self.INANIMATE_Y_MARKERS = {
            '事', '事情', '问题', '情况', '现象', '结果',
            '政策', '制度', '措施', '方法', '做法', '方案', '计划',
            '工作', '任务', '项目', '活动', '行动',
            '社会', '国家', '市场', '经济', '发展',
        }

    def classify(self, concordance: str, predicate: str, pred_comp: str,
                 y_phrase: str, y_anim: str) -> Tuple[Optional[str], float, Optional[str]]:
        """Classify a single instance using v67 rules."""

        def safe_str(val):
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return ""
            return str(val).strip()

        predicate = safe_str(predicate)
        pred_comp = safe_str(pred_comp)
        y_phrase = safe_str(y_phrase)
        y_anim = safe_str(y_anim).lower()
        concordance = safe_str(concordance)

        y_is_animate = self._is_animate(y_phrase, y_anim)

        # V60.6: Check if Y IS an institution (exact match only)
        y_is_institution = y_phrase in self.INSTITUTION_Y

        # ================================================================
        # PRIORITY 0: V60.8 Reclassifications
        # ================================================================

        # V60.8: Former DISP → MS idioms (internal states)
        for idiom in self.FORMER_DISP_NOW_MS_IDIOMS:
            if idiom in pred_comp or predicate == idiom:
                return ('MS', 0.92, f'{idiom}=internal disregard state (v60.8)')

        # V60.8: Former DISP → MS verbs (internal states)
        if predicate in self.FORMER_DISP_NOW_MS_VERBS:
            return ('MS', 0.90, f'{predicate}=internal state (v60.8)')

        # V60.8: Former DISP → SI verbs (active verbs V他✓)
        if predicate in self.FORMER_DISP_NOW_SI_VERBS:
            # Special case: 摆 needs context check
            if predicate == '摆':
                if '架子' in pred_comp or '姿态' in pred_comp:
                    return ('DISP', 0.85, '摆架子/姿态=manner expression (v60.8)')
            return ('SI', 0.90, f'{predicate}=active intervention V他✓ (v60.8)')

        # ================================================================
        # V67_FIXED3: PREDICATE-PRIORITY RULES
        # These execute EARLY to ensure predicate context overrides complement keywords
        # Critical for cases like: 提出+X, 采访+X where X might be MS/ABT verb
        # ================================================================

        # High-priority discourse verbs (always ABT/DA regardless of complement)
        discourse_predicates_high_priority = {
            '提出': ('ABT', 0.91, 'raise/propose discourse ABOUT (v67_FIXED4 priority)'),
            '采访': ('ABT', 0.91, 'interview/investigate ABOUT (v67_FIXED4 priority)'),
            '调查': ('ABT', 0.91, 'investigate ABOUT (v67_FIXED4 priority)'),
            # '了解' REMOVED - too ambiguous (对人了解=MS, 对问题了解=ABT)
            '研究': ('ABT', 0.90, 'research ABOUT (v67_FIXED4 priority)'),
            '分析': ('ABT', 0.90, 'analyze ABOUT (v67_FIXED4 priority)'),
            '探讨': ('ABT', 0.90, 'discuss ABOUT (v67_FIXED4 priority)'),
            '讨论': ('ABT', 0.90, 'discuss ABOUT (v67_FIXED4 priority)'),
            '表示': ('ABT', 0.91, 'express discourse ABOUT (v67_FIXED4 priority)'),  # ADDED!
        }

        # Check predicate first (unless it has specific complement patterns)
        if predicate in discourse_predicates_high_priority:
            # Exception 1: 提出 has special legal action patterns
            if predicate == '提出':
                legal_markers = ['抗诉', '起诉', '诉讼', '控告', '申诉', '上诉',
                                 '处罚', '惩罚', '警告', '抗议']
                if any(m in pred_comp for m in legal_markers):
                    return ('SI', 0.92, f'提出+legal action ON (v67_FIXED4)')

            # Exception 2: 表示 + animate Y → DA (express TO person)
            if predicate == '表示' and y_is_animate:
                return ('DA', 0.91, '表示+animate Y=express TO person (v67_FIXED4)')

            # Default: return ABT based on predicate (discourse ABOUT Y)
            label, conf, reason = discourse_predicates_high_priority[predicate]
            return (label, conf, reason)

        # ================================================================
        # End of Predicate-Priority Rules
        # ================================================================

        # ================================================================
        # PRIORITY 1: Critical v60.2+ fixes
        # ================================================================

        # FIX #1: 具有 + patterns
        if predicate == '具有':
            # EVAL: significance/effect
            for sig in self.JUYOU_SIGNIFICANCE_EVAL:
                if sig in pred_comp:
                    return ('EVAL', 0.94, f'具有+{sig}=significance FOR Y (v60.2)')
            significance_in_conc = ['意义', '作用', '价值', '影响', '效果', '吸引力', '指导']
            for sig in significance_in_conc:
                if sig in concordance:
                    return ('EVAL', 0.92, f'具有+{sig}(in conc)=significance FOR Y (v60.3)')
            # SI: control/rights
            si_rights = ['控制权', '管辖权', '所有权', '支配权', '决定权', '否决权', '监护权']
            for sr in si_rights:
                if sr in pred_comp or sr in concordance:
                    return ('SI', 0.92, f'具有+{sr}=bounded authority OVER Y (v60.4)')
            # MS: psychological state
            psych_states = ['经验', '感情', '感', '同感', '责任感', '事业心', '信心', '热情', '兴趣', '好感']
            for ps in psych_states:
                if ps in pred_comp or ps in concordance:
                    return ('MS', 0.90, f'具有+{ps}=psychological state (v60.3)')
            # Default: ABT
            return ('ABT', 0.80, '具有=possession REGARDING (v60.2)')

        # V60.6: 表示 patterns - CHECK INTERNAL EMOTIONS FIRST (v67 fix)
        if predicate == '表示':
            # V67 FIX: Check for INTERNAL emotions FIRST (before animacy logic)
            internal_emotions_v67 = {
                '关切', '关心', '关注', '重视', '不满', '满意', '失望',
                '不以为然', '不屑', '轻蔑', '鄙夷', '敬意', '崇敬',
                '吃惊', '惊讶', '诧异', '惊奇', '惊异', '震惊',
                '怀疑', '疑惑', '疑虑', '质疑', '猜疑',
                '兴趣', '好奇', '热情', '热心', '冷淡', '冷漠',
                '同情', '怜悯', '慈悲', '悲悯', '歉意', '愧疚',
                '高兴', '喜悦', '欣慰', '欣喜', '欢喜',
                '烦躁', '不安', '焦虑', '担忧', '忧虑',
                '渴求', '渴望', '向往',
            }

            # Check internal emotions first
            for emotion in internal_emotions_v67:
                if emotion in pred_comp:
                    # Exception: 表示+speech_to_person is DA (e.g., 表示感谢对某人)
                    speech_to_markers = ['祝贺', '感谢', '慰问', '欢迎', '致谢', '谢意', '问候', '致敬']
                    is_speech_to_person = any(m in pred_comp for m in speech_to_markers) and y_is_animate

                    if not is_speech_to_person:
                        return ('MS', 0.92, f'表示+{emotion}=internal emotion (v67 fix)')

            # Original animacy logic for non-internal expressions
            emotional_expressions = [
                '悼念', '哀悼', '祝贺', '感谢', '满意', '遗憾', '不满', '歉意',
                '欢迎', '支持', '赞同', '同意', '反对', '抗议', '关注', '关切',
                '理解', '同情', '谅解', '担忧', '担心', '忧虑', '怀疑', '质疑',
                '慰问', '敬意', '问候', '致敬', '致谢', '谢意',
            ]
            for expr in emotional_expressions:
                if expr in pred_comp:
                    if y_is_animate or y_is_institution:
                        return ('DA', 0.90, f'表示+{expr}+recipient=express TO (v60.8)')
                    else:
                        return ('ABT', 0.90, f'表示+{expr}+inan=express ABOUT (v60.8)')
            if y_is_animate or y_is_institution:
                return ('DA', 0.80, '表示+recipient=express TO (v60.8)')
            else:
                return ('ABT', 0.80, '表示+inan Y=express ABOUT (v60.8)')

        # ================================================================
        # V60.9 FIX #2: 进行 → ALWAYS SI (CRITICAL)
        # ================================================================
        if predicate == '进行':
            return ('SI', 0.94, '进行=procedural intervention ON scope (v67)')

        # ================================================================
        # V60.9 FIX #NEW: Vague verb + individual person → DA (not SI)
        # ================================================================
        if predicate in ['做', '干', '作', '做出', '作出', '搞', '弄']:
            # Pattern: 对他做什么, 对她干那事 → DA
            # Check for vague complements (short, no specific action named)
            vague_indicators = ['什么', '那事', '这事', '啥', '些', '那些', '这些']
            has_vague = any(ind in pred_comp for ind in vague_indicators)
            is_short_comp = len(pred_comp) <= 4

            # Only DA if: (vague OR short) AND individual animate (not institution)
            if (has_vague or is_short_comp) and y_is_animate and not y_is_institution:
                return ('DA', 0.90, f'{predicate}+vague action+person=directed TO (v67)')

            # Otherwise continue to other patterns below

        # FIX #3: 提出 patterns
        if predicate == '提出':
            legal_actions = ['抗诉', '起诉', '诉讼', '控告', '申诉', '上诉',
                             '处罚', '惩罚', '警告', '抗议']
            for la in legal_actions:
                if la in pred_comp or la in concordance:
                    return ('SI', 0.90, f'提出+{la}=legal action ON (v60.4)')
            if '异议' in pred_comp or '异议' in concordance:
                return ('ABT', 0.92, '提出+异议=raise objection ABOUT Y (v67_FIXED3)')
            if '要求' in pred_comp or '要求' in concordance:
                if y_is_animate:
                    return ('SI', 0.90, '提出+要求+anim Y=impose requirements ON (v60.3)')
                else:
                    return ('ABT', 0.88, '提出+要求+inan Y=discourse ABOUT (v60.3)')
            for dc in self.TICHU_DISCOURSE_ABT:
                if dc in pred_comp:
                    return ('ABT', 0.90, f'提出+{dc}=put forward discourse ABOUT (v60.2)')
            if y_is_animate:
                return ('DA', 0.88, '提出+anim Y=speech TO (v60.2)')
            return ('ABT', 0.80, '提出=put forward ABOUT (v60.2)')

        # FIX #4: 作出/做出 patterns
        if predicate == '作出' or predicate == '做出':
            if '贡献' in pred_comp or '贡献' in concordance:
                return ('EVAL', 0.92, f'{predicate}+贡献=contribution FOR Y (v60.3)')
            speech_gesture_comps = {'表示', '回应', '回答', '答复'}
            if y_is_animate or y_is_institution:
                for sgc in speech_gesture_comps:
                    if sgc in pred_comp:
                        return ('DA', 0.90, f'{predicate}+{sgc}+recipient=gesture TO (v60.8)')
            action_response_markers = {'应急', '联动', '处置', '紧急', '快速', '及时', '协同'}
            if '反应' in pred_comp or '响应' in pred_comp:
                if any(marker in pred_comp for marker in action_response_markers):
                    return ('SI', 0.92, f'{predicate}+action response=intervention ON (v60.8)')
            for dc in self.ZUOCHU_DISCOURSE_ABT:
                if dc in pred_comp:
                    return ('ABT', 0.90, f'{predicate}+{dc}=produce discourse ABOUT (v60.2)')
            intervention_comps = [
                '处理', '规定', '处罚', '部署', '判决', '调整',
                '约定', '规划', '补充', '安排', '承诺', '保证', '让步',
                '牺牲', '努力', '准备',
                '拘留', '宣告', '反击', '反弹', '赔偿', '裁决',
                '处置', '批示', '指示', '调解', '仲裁', '惩罚', '惩处',
            ]
            for ic in intervention_comps:
                if ic in pred_comp or ic in concordance:
                    return ('SI', 0.90, f'{predicate}+{ic}=intervention ON (v60.4)')
            return (None, 0.0, None)

        # FIX #5: 给予/予以 patterns
        if predicate == '给予' or predicate == '予以':
            # V67: Check for mental objects FIRST (before SI default)
            if predicate == '给予':
                mental_objects = {'厚望', '期望', '希望', '信任', '支持', '关注', '重视'}
                for obj in mental_objects:
                    if obj in pred_comp:
                        return ('MS', 0.88, f'给予+{obj}=internal expectation (v67)')

            for dc in self.JIYU_DISCOURSE_ABT:
                if dc in pred_comp:
                    return ('ABT', 0.90, f'{predicate}+{dc}=give evaluation ABOUT (v60.2)')
            if y_is_animate:
                for da in self.JIYU_ACTION_DA:
                    if da in pred_comp:
                        return ('DA', 0.90, f'{predicate}+{da}+anim=give TO (v60.2)')
            return ('SI', 0.85, f'{predicate}=intervention ON (v60.2)')

        # FIX #6: 不予 patterns
        if predicate == '不予' or '不予' in pred_comp:
            for pattern in self.BUYU_ABT_PATTERNS:
                if pattern in pred_comp:
                    return ('ABT', 0.90, f'不予+{pattern}=refuse to engage ABOUT (v60.2)')
            return ('SI', 0.85, '不予=refusal ON scope (v60.2)')

        # V60.8 FIX: 施以 → always SI (training 87% SI)
        if predicate == '施以':
            return ('SI', 0.92, '施以=inflict/apply ON Y (v60.8)')

        # V60.3 FIX: 提供+intervention → SI
        if predicate == '提供':
            intervention_nouns = ['服务', '帮助', '惩罚', '援助', '保护', '支持', '支援',
                                  '治疗', '培训', '教育', '补贴', '优惠', '折扣']
            for noun in intervention_nouns:
                if noun in pred_comp or noun in concordance:
                    return ('SI', 0.92, f'{predicate}+{noun}=intervention ON Y (v60.3)')

        # FIX #7: Speech verbs + animate Y → DA
        if predicate in self.SPEECH_ACTION_TO_DA and y_is_animate:
            return ('DA', 0.92, f'{predicate}+anim Y=speech/action TO (v60.2)')

        # FIX #8: Manner expressions → DISP
        for pattern in self.MANNER_EXPRESSIONS_DISP:
            if pattern in pred_comp or predicate == pattern:
                return ('DISP', 0.90, f'{pattern}=manner expression (v60.2)')

        # ================================================================
        # V69 FIX #1: 有 (HAVE) patterns - most common low confidence (40 cases)
        # ================================================================
        if predicate == '有':
            # Pattern 1: 有+恩/恩德/恩惠/功劳 → EVAL (benefit FOR Y)
            eval_complements = {'恩', '恩德', '恩惠', '大恩', '恩情', '功劳', '功德', 
                               '救命之恩', '救命大恩', '养育之恩'}
            for comp in eval_complements:
                if comp in pred_comp or comp in concordance:
                    return ('EVAL', 0.92, f'有+{comp}=benefit FOR Y (v69)')
            
            # Pattern 2: 有+索求/抗拒/防范/疑义/盘算 → MS (psychological state)
            ms_complements = {'索求', '抗拒', '抗拒力', '防范', '防范之心', '疑义', 
                            '盘算', '要求', '注意', '罪恶感', '事业心', '义务'}
            for comp in ms_complements:
                if comp in pred_comp or comp in concordance:
                    return ('MS', 0.90, f'有+{comp}=psychological state (v69)')
            
            # Pattern 3: 有+宽容/恩德 when Y is animate → DISP (manner)
            if y_is_animate:
                disp_complements = {'宽容', '耐心', '爱心', '同情心', '包容'}
                for comp in disp_complements:
                    if comp in pred_comp or comp in concordance:
                        return ('DISP', 0.91, f'有+{comp}=manner toward Y (v69)')
        
        # ================================================================
        # V69 FIX #2: 寄予/寄托 → MS (psychological projection) - 11 low confidence cases
        # ================================================================
        if predicate in ['寄予', '寄托']:
            # These are always psychological projection (hope/expectation)
            return ('MS', 0.93, f'{predicate}=project hope/expectation (v69)')

        # ================================================================
        # FIX #9: 负责 patterns (v60.8 refined)
        # ================================================================
        if predicate == '负责' or '负责' in pred_comp:
            # Only casual degree adverbs signal manner (DISP)
            casual_advs = {'很', '挺', '蛮', '太'}
            fuze_pos = concordance.find('负责')
            if fuze_pos > 0:
                context_before = concordance[max(0, fuze_pos - 8):fuze_pos]
                for adv in casual_advs:
                    if adv in context_before:
                        return ('DISP', 0.88, f'负责+{adv}=responsible manner (v60.8)')
            # Default: SI (accountability) - training 91% SI
            return ('SI', 0.94, '负责=accountability ON scope (v60.8)')

        # ================================================================
        # V60.4: Comprehensive 有-pattern classification
        # ================================================================
        if predicate in self.SIMILE_VERBS:
            return ('DISP', 0.96, f'{predicate}=simile manner')

        if predicate in self.OPPOSITION_SI_VERBS:
            return ('SI', 0.95, f'{predicate}=opposition ON')

        # V60.8: 引起+psychological response → MS
        if predicate == '引起':
            psych_responses = {'重视', '关注', '注意', '警惕', '警觉', '兴趣', '好奇'}
            for resp in psych_responses:
                if resp in pred_comp or resp in concordance:
                    return ('MS', 0.90, f'引起+{resp}=trigger psychological response (v60.8)')
            return ('EVAL', 0.90, '引起=effect ON (v60.8)')

        if predicate in self.EFFECT_VERBS:
            return ('EVAL', 0.94, f'{predicate}=effect ON')

        if predicate in self.FAIRNESS_EVAL_PREDICATES:
            return ('EVAL', 0.92, f'{predicate}=fairness evaluation FOR')

        if predicate in self.INHERENT_ADDRESSEE_VERBS:
            return ('DA', 0.95, f'{predicate}=inherent addressee verb TO')

        if predicate in self.SPEECH_DAO_VERBS:
            return ('DA', 0.95, f'{predicate}=speech/narration TO Y')

        # ================================================================
        # ================================================================
        # PRIORITY 2.5: COMPREHENSIVE MS PATTERN RECOGNITION (v63 FIX)
        # Addresses remaining 342 MS→ABT errors from v62
        # ================================================================

        # ------------------------------------------------------------
        # FIX #1: 有-predicates with ALL variants
        # ------------------------------------------------------------
        # CRITICAL: This must come BEFORE the comprehensive you_predicates check
        # because those rules have different logic paths

        you_all_variants = {'有', '没有', '没', '有着', '有所', '持有', '抱有', '怀有',
                            '应有', '保有', '具有', '拥有', '享有', '富有'}

        if predicate in you_all_variants:
            # Expanded MS noun list (includes missing nouns from analysis)
            ms_state_nouns = {
                # Core cognitive states
                '认识', '了解', '理解', '体会', '体验', '感受', '感觉', '感应',
                '印象', '概念', '想法', '看法', '观点', '见解', '意见', '主张',
                '追求', '选择', '经验', '信心', '信念', '疑问', '怀疑', '质疑',
                '误解', '曲解', '偏见', '成见', '准备', '警惕', '戒心', '戒备',
                '兴趣', '热情', '好感', '恶感', '同情', '怜悯', '敬意',
                '期待', '期望', '希望', '担心', '顾虑', '不满', '异议',
                # V63: Missing from v62 analysis
                '共识', '体认', '体悟', '觉悟', '领悟', '感悟',  # deeper understanding
                '谱', '底', '数',  # mental grasp (心中有谱, 心里有底, 心中有数)
                '把握', '掌握',  # grasp/control (内在能力)
                '顾忌', '忌惮', '畏惧', '恐惧',  # fears
                '期许', '憧憬', '向往', '渴望',  # aspirations
                '好奇', '好奇心', '求知欲',  # curiosity
                '依赖', '依恋', '眷恋',  # attachment
                '反感', '抵触', '厌恶感',  # aversion
                '歉意', '愧疚', '内疚',  # guilt (internal, not speech act)
                '敬畏', '崇敬', '尊敬',  # reverence (internal state)
                # V67: Additional missing nouns from v66 error analysis
                '认知', '体悟',  # cognition (similar to 认识)
                '转变',  # change in thinking/attitude
                '见地', '主见',  # insight, opinion
                '观念', '理念',  # concept, idea
                '记忆', '回忆',  # memory
                '评价', '评判',  # evaluation, judgment
                '感慨', '感叹',  # emotional reflection
                '腹案', '打算',  # plan in mind
                '抵抗力', '免疫力',  # resistance (mental)
                '判断', '判定',  # judgment
                '包容心', '宽容心',  # tolerance
                '触觉', '敏感度',  # sensitivity (psychological)
                '常识', '知识',  # common sense, knowledge
                '反映', '反应',  # reflection, response
                '争议', '异议',  # controversy (internal stance)
                '微辞', '意见',  # criticism, opinion
                '比较', '对比',  # comparison (mental)
                '角度', '视角',  # perspective
                '考量',  # consideration
            }

            for noun in ms_state_nouns:
                if noun in pred_comp:
                    return ('MS', 0.95, f'{predicate}+{noun}=internal state (v63 fix)')

        # ------------------------------------------------------------
        # FIX #2: 产生/形成/发生 + expanded state nouns
        # ------------------------------------------------------------
        if predicate in ['产生', '形成', '发生', '萌生', '滋生', '引发', '激发', '生出']:
            state_formation = {
                '误解', '曲解', '理解', '认识', '了解', '感受', '体验', '体会',
                '印象', '看法', '想法', '观点', '见解', '概念',
                '警惕', '警觉', '戒备', '疑问', '怀疑', '质疑', '猜疑',
                '联想', '反应', '响应', '解读', '感悟', '领悟', '顿悟',
                '不谅解', '条件反射', '关注', '意识', '共鸣', '认同',
                '感情', '情感', '兴趣', '好奇', '敬意', '畏惧', '恐惧',
                # NEW from analysis
                '偏见', '成见', '好感', '恶感', '同情', '反感',
            }
            for state in state_formation:
                if state in pred_comp:
                    return ('MS', 0.94, f'{predicate}+{state}=state formation (v63 fix)')

        # ------------------------------------------------------------
        # FIX #3: 存在 + cognitive/emotional states → MS
        # ------------------------------------------------------------
        if predicate in ['存在', '存', '存有']:
            cognitive_issues = {
                '误解', '偏见', '成见', '疑虑', '顾虑', '认识', '看法', '想法',
                '迷信', '自卑', '模糊', '困惑', '混乱', '问题',
            }
            for issue in cognitive_issues:
                if issue in pred_comp:
                    return ('MS', 0.93, f'存在+{issue}=internal cognitive state (v63 fix)')

        # ------------------------------------------------------------
        # FIX #4: 看得 + perceptual clarity → MS
        # ------------------------------------------------------------
        if predicate in ['看', '看得', '看得见', '看到']:
            clarity_expressions = {
                '看得清', '看得透', '看得淡', '看得开', '看得通', '看得穿', '看得破',
                '看清', '看透', '看淡', '看开', '看通', '看穿', '看破',
                '看得清楚', '看得明白', '看得出', '看得懂', '看得很清楚',
                '看得通达', '看不清', '看不透', '看不懂', '看不明白',
            }
            for expr in clarity_expressions:
                if expr in pred_comp or expr in predicate:
                    return ('MS', 0.94, f'{expr}=perceptual understanding (v63 fix)')

        # ------------------------------------------------------------
        # FIX #5: 表示/表现 + internal emotion (not speech TO) → MS  
        # ------------------------------------------------------------
        if predicate in ['表示', '表现', '表露', '流露', '显露', '透露']:
            internal_emotions = {
                '关切', '关心', '关注', '重视', '不满', '满意', '失望',
                '不以为然', '不屑', '轻蔑', '鄙夷', '敬意', '崇敬',
                '吃惊', '惊讶', '诧异', '惊奇', '惊异', '震惊',
                '怀疑', '疑惑', '疑虑', '质疑', '猜疑',
                '兴趣', '好奇', '热情', '热心', '冷淡', '冷漠',
                '同情', '怜悯', '慈悲', '悲悯', '歉意', '愧疚',
                '高兴', '喜悦', '欣慰', '欣喜', '欢喜',
                '烦躁', '不安', '焦虑', '担忧', '忧虑',
                '好奇', '渴求', '渴望', '向往',
            }

            # Only MS if NOT clearly speech TO animate Y
            for emotion in internal_emotions:
                if emotion in pred_comp:
                    # Check if it's speech TO person (then it's DA)
                    speech_markers = ['支持', '感谢', '慰问', '祝贺', '欢迎', '抗议']
                    is_speech_to = any(marker in pred_comp for marker in speech_markers) and y_is_animate

                    if not is_speech_to:
                        return ('MS', 0.91, f'{predicate}+{emotion}=internal emotion (v63 fix)')

        # ------------------------------------------------------------
        # FIX #6: 服/不服 → MS (internal resistance)
        # ------------------------------------------------------------
        if predicate in ['服', '不服', '心服', '口服']:
            if '不服' in pred_comp or predicate == '不服' or '不服' in concordance:
                # 不服 = internal non-acceptance
                return ('MS', 0.93, '不服=internal resistance (v63 fix)')

        # ------------------------------------------------------------
        # FIX #7: Critical MS idioms from error analysis
        # ------------------------------------------------------------
        ms_idioms_comprehensive = {
            # Perceptual understanding
            '刮目相看', '另眼相看', '侧目而视', '拭目以待',
            # Cognitive states
            '一窍不通', '一知半解', '似懂非懂', '茫然不知', '浑然不觉',
            '了如指掌', '心知肚明', '心中有数', '心里有底', '心中有谱',
            '知根知底', '明察秋毫',
            # Emotional states
            '愤之入骨', '恨之入骨', '爱之入骨', '痛之入骨',
            '喜形于色', '怒形于色', '溢于言表',
            '不以为然', '不以为意', '不当回事',
            # Emotional breakthrough
            '恍然大悟', '豁然开朗', '茅塞顿开', '幡然醒悟',
        }

        for idiom in ms_idioms_comprehensive:
            if idiom in pred_comp or idiom in predicate:
                return ('MS', 0.95, f'{idiom}=MS idiom (v63 fix)')

        # ------------------------------------------------------------
        # FIX #8: 是 + psychological state adjectives → MS
        # ------------------------------------------------------------
        if predicate == '是':
            psych_state_de = {
                '拥护的', '支持的', '满意的', '不满的', '失望的',
                '尊敬的', '敬重的', '崇敬的', '景仰的',
                '了解的', '熟悉的', '清楚的', '知道的', '明白的',
                '理解的', '熟知的', '认识的', '懂的', '懂得的',
                '喜欢的', '喜爱的', '热爱的', '讨厌的', '厌恶的',
                '知根知底的', '心知肚明的',
            }
            for state in psych_state_de:
                if state in pred_comp:
                    return ('MS', 0.91, f'是+{state}=psychological state (v63 fix)')

        # ------------------------------------------------------------
        # FIX #9: 确立/树立/建立 + internal confidence/faith → MS
        # ------------------------------------------------------------
        if predicate in ['确立', '树立', '建立', '培养', '养成']:
            internal_qualities = {
                '信心', '必胜信心', '信念', '信仰', '价值观', '世界观',
                '认识', '观念', '意识', '概念', '理念',
                '感情', '情感', '友谊', '友情',
            }
            for quality in internal_qualities:
                if quality in pred_comp:
                    return ('MS', 0.92, f'{predicate}+{quality}=establish internal state (v63 fix)')

        # ------------------------------------------------------------
        # FIX #10: 失去/丧失 + internal qualities → MS
        # ------------------------------------------------------------
        if predicate in ['失去', '丧失', '失', '去']:
            lost_qualities = {
                '信心', '信任', '信念', '信仰', '希望', '兴趣', '热情',
                '感觉', '直觉', '判断', '标准', '认识', '理解',
                '尊重', '敬意', '好感', '耐心',
            }
            for quality in lost_qualities:
                if quality in pred_comp:
                    return ('MS', 0.92, f'失去+{quality}=lose internal state (v63 fix)')

        # ------------------------------------------------------------
        # FIX #11: 想/思考/沉思 + no output → MS (internal deliberation)
        # ------------------------------------------------------------
        if predicate in ['想', '思考', '沉思', '冥想', '琢磨', '考虑']:
            # If just thinking about Y without producing discourse
            discourse_markers = {'办法', '对策', '措施', '方案', '计划'}
            has_discourse = any(marker in pred_comp for marker in discourse_markers)

            if not has_discourse:
                return ('MS', 0.90, f'{predicate}=internal deliberation (v63 fix)')

        # ------------------------------------------------------------
        # FIX #12: 追求 (as verb, not noun) → MS
        # ------------------------------------------------------------
        if predicate == '追求' or (predicate == '有' and '追求' == pred_comp.strip()):
            return ('MS', 0.91, '追求=internal pursuit/aspiration (v63 fix)')

        # ------------------------------------------------------------
        # FIX #13: 正视/直视 → MS (internal confrontation)
        # ------------------------------------------------------------
        if predicate in ['正视', '直视', '重视', '注视']:
            # These are internal acts of attention/confrontation
            return ('MS', 0.90, f'{predicate}=internal attention/confrontation (v63 fix)')

        # ------------------------------------------------------------
        # FIX #14: 支持 (without concrete action) → MS
        # ------------------------------------------------------------
        if predicate == '支持':
            # If just internal support (not concrete action or speech TO)
            concrete_markers = {'资金', '人力', '物资', '技术', '帮助'}
            has_concrete = any(marker in pred_comp for marker in concrete_markers)

            if not has_concrete and not y_is_animate:
                return ('MS', 0.88, '支持=internal support/agreement (v63 fix)')

        # ================================================================
        # End of PRIORITY 2.5: MS Pattern Recognition (v63)

        # ================================================================
        # V66: Additional Clear-Cut MS Pattern Fixes (31 fixes)
        # High-priority patterns identified from v65 error analysis
        # ================================================================

        # ------------------------------------------------------------
        # FIX #15: 看得+perceptual understanding (5 cases)
        # ------------------------------------------------------------
        # 看得清/透/淡/开 = metaphorical understanding, not physical seeing
        if predicate == '看得':
            perception_markers = {'清', '透', '淡', '开', '通', '穿', '破', '仔细', '通达'}
            for marker in perception_markers:
                if marker in pred_comp:
                    return ('MS', 0.92, f'看得+{marker}=perceptual understanding (v66)')

        # ------------------------------------------------------------
        # FIX #16: 采取+态度 (11 cases)
        # ------------------------------------------------------------
        # Adopting an attitude = mental/emotional stance
        if predicate == '采取' and '态度' in pred_comp:
            return ('MS', 0.90, '采取+态度=adopt attitude (v66)')

        # ------------------------------------------------------------
        # FIX #17: Additional MS idioms (12 cases)
        # ------------------------------------------------------------
        ms_idioms_v66 = {
            '习以为常',  # accustomed to, take for granted
            '记忆犹新',  # memory still fresh
            '坚信不疑',  # firmly believe without doubt
            '确信无疑',  # certain without doubt
            '麻木不仁',  # numb and insensitive
            '无计可施',  # at wit's end
            '在行',  # knowledgeable, expert
            '念念不忘',  # can't forget, keep thinking about
            '心有余悸',  # still feel lingering fear
            '不以为然',  # not think so, disagree internally
            '不以为意',  # not care, not mind
            '难以释怀',  # hard to let go
            '忘怀',  # forget (unable to)
            '割舍',  # give up (emotionally hard)
            '忘却',  # forget
            '迷信',  # be superstitious about
            '发呆',  # be in a daze
            '难过',  # feel sad
        }

        if predicate in ms_idioms_v66:
            return ('MS', 0.92, f'{predicate}=MS idiom (v66)')

        # ------------------------------------------------------------
        # FIX #18: 想/怎么想 without speech output (3 cases)
        # ------------------------------------------------------------
        # Internal thought, not communicated
        if predicate in ['想', '怎么想']:
            # Check for speech/communication markers
            speech_markers = ['说', '讲', '告诉', '表示', '认为', '觉得']
            has_speech = any(marker in concordance for marker in speech_markers)

            if not has_speech and not y_is_animate:
                return ('MS', 0.88, '想=internal thought (v66)')

        # ================================================================
        # V67: Additional Medium-Priority MS Pattern Fixes (~45 fixes)
        # Based on v66 error analysis - medium confidence patterns
        # ================================================================

        # ------------------------------------------------------------
        # FIX #20: 留下+impression/memory (3 cases)
        # V67 FIX: Boost confidence to 0.93 to override earlier rules
        # ------------------------------------------------------------
        if predicate == '留下':
            memory_markers = {'印象', '记忆', '感觉', '感受', '影响'}
            for marker in memory_markers:
                if marker in pred_comp:
                    return ('MS', 0.93, f'留下+{marker}=perceptual memory (v67 fix)')

        # ------------------------------------------------------------
        # FIX #21: Additional MS patterns from v66 analysis
        # ------------------------------------------------------------

        # 失+mental state (失神智, 失常等)
        if predicate == '失' and any(m in pred_comp for m in ['神', '智', '常', '态']):
            return ('MS', 0.93, '失+mental=lose mental state (v67 fix)')

        # 想+concrete action (NOT MS, but check)
        # 学得好/差 (learning perception)
        if predicate in ['学', '学得'] and any(m in pred_comp for m in ['好', '差', '快', '慢']):
            return ('MS', 0.85, '学得+evaluation=learning perception (v67)')

        # 打上问号 (have doubts)
        if '问号' in pred_comp or '疑问' in pred_comp:
            return ('MS', 0.87, 'question mark=doubt (v67)')

        # 提不起劲/兴趣 (lack motivation/interest)
        if predicate == '提' and any(m in pred_comp for m in ['劲', '精神', '兴趣']):
            return ('MS', 0.93, '提不起+motivation=lack energy (v67 fix)')

        # 容忍/忍受 (tolerance as mental state)
        if predicate in ['容忍', '忍受', '接受'] and not y_is_animate:
            return ('MS', 0.93, f'{predicate}=tolerance/acceptance (v67 fix)')

        # 误会/误解 when not about person
        if predicate in ['误会', '误解'] and not y_is_animate:
            return ('MS', 0.87, f'{predicate}=misunderstanding (v67)')

        # 叫好/称赞 (appreciation)
        if predicate in ['叫好', '称赞', '赞赏', '欣赏']:
            return ('MS', 0.93, f'{predicate}=appreciation (v67 fix)')

        # 识/认识 (know/recognize)
        if predicate in ['识', '认', '不识', '不认']:
            return ('MS', 0.93, f'{predicate}=recognize/know (v67 fix)')

        # 明晰/明了 (mental clarity)
        if predicate in ['明晰', '明了', '清晰', '清楚']:
            return ('MS', 0.86, f'{predicate}=mental clarity (v67)')

        # 淡忘/遗忘 (forget)
        if predicate in ['淡忘', '遗忘', '忘记']:
            return ('MS', 0.93, f'{predicate}=forget (v67 fix)')

        # 讲究 (be particular about)
        if predicate == '讲究':
            return ('MS', 0.85, '讲究=be particular (v67)')

        # ================================================================
        # V67_FIXED2: DISP EXCLUSIONS (Fix over-prediction)
        # Add specific patterns that look like DISP but aren't
        # These must execute BEFORE general DISP rules
        # ================================================================

        # ------------------------------------------------------------
        # DISP → MS: Internal psychological states (not observable manner)
        # ------------------------------------------------------------
        ms_not_disp = {
            '不舍', '轻蔑', '鄙视', '鄙薄', '瞧不起',
            '关心', '关怀', '牵挂', '挂念', '惦记',
            '敬而远之', '敬畏', '畏惧', '忌惮',
            '狠得下心', '狠心', '心软', '心硬',
        }

        for pattern in ms_not_disp:
            if pattern in pred_comp or predicate == pattern:
                return ('MS', 0.95, f'{pattern}=internal state not manner (v67_FIXED4)')

        # Special: 情X义Y patterns (internal emotional states)
        if any(p in pred_comp for p in ['情消义尽', '情深义重', '情断义绝']):
            return ('MS', 0.94, 'emotion pattern=internal state (v67_FIXED2)')

        # 有+mental/emotional nouns (MS not DISP)
        mental_disp_nouns = {'主人思想', '眷顾', '好脸色', '尊重'}
        if predicate in ['有', '没有', '有着']:
            for noun in mental_disp_nouns:
                if noun in pred_comp:
                    return ('MS', 0.94, f'有+{noun}=mental state (v67_FIXED2)')

        # 留心/留神 (MS - mental attention)
        if predicate == '留' and any(m in pred_comp for m in ['心', '神', '意', '神']):
            return ('MS', 0.94, '留心=mental attention (v67_FIXED2)')

        # ------------------------------------------------------------
        # DISP → DA: Speech acts and gestures
        # ------------------------------------------------------------
        speech_not_disp = {
            '恭维', '奉承', '巴结', '阿谀', '谄媚',
            '坦白', '交代', '供认', '招供',
            '掏心剖肺', '推心置腹',
            '喋喋不休', '唠唠叨叨', '絮絮叨叨',
        }

        for pattern in speech_not_disp:
            if pattern in pred_comp or predicate == pattern:
                return ('DA', 0.95, f'{pattern}=speech act not manner (v67_FIXED4)')

        # Physical gestures (DA not DISP)
        gesture_patterns = ['摇首摆尾', '欠身', '鞠躬', '作揖', '磕头']
        for pattern in gesture_patterns:
            if pattern in pred_comp or predicate == pattern:
                return ('DA', 0.94, f'{pattern}=gesture not manner (v67_FIXED2)')

        # 是+action pattern (DA not DISP)
        if predicate == '是' and '听其言观其行' in pred_comp:
            return ('MS', 0.94, '听其言观其行=observation method (v67_FIXED2)')

        # ------------------------------------------------------------
        # DISP → SI: Active actions (can take 他 as object)
        # ------------------------------------------------------------
        action_not_disp = {
            '坚持', '恪守', '遵守', '遵循', '秉承',
            '回避', '躲避', '避开', '规避',
            '退避', '让步', '妥协',
            '背信弃义', '忘恩负义', '恩将仇报',
            '臣服', '屈服', '投降', '归顺',
            '失礼', '失敬', '失态',
        }

        for pattern in action_not_disp:
            if pattern in pred_comp or predicate == pattern:
                # Distinguish SI vs MS based on context
                if pattern in {'背信弃义', '忘恩负义', '恩将仇报'}:
                    return ('SI', 0.94, f'{pattern}=active betrayal (v67_FIXED2)')
                elif pattern in {'臣服', '屈服', '投降'}:
                    return ('MS', 0.93, f'{pattern}=internal submission (v67_FIXED2)')
                else:
                    return ('SI', 0.95, f'{pattern}=active verb not manner (v67_FIXED4)')

        # 失去+abstract (SI not DISP)
        if predicate == '失去' or '失去' in pred_comp:
            return ('MS', 0.95, '失去=lose (v67_FIXED4)')

        # 有+行为 patterns (SI not DISP)
        if predicate in ['有', '没有'] and any(p in pred_comp for p in ['冒犯', '逾矩', '违背', '行为']):
            return ('SI', 0.93, '有+action=action pattern (v67_FIXED2)')

        # ------------------------------------------------------------
        # DISP → EVAL: Evaluation/existence predicates
        # ------------------------------------------------------------
        eval_not_disp = {
            '存在', '不存在', '不复存在',
            '是一样', '是相同', '是不同',
            '有所不公', '有失公允',
        }

        for pattern in eval_not_disp:
            if pattern in pred_comp or predicate == pattern:
                return ('EVAL', 0.95, f'{pattern}=evaluation not manner (v67_FIXED4)')

        # 做不到/做得到 (MS - ability)
        if any(p in pred_comp for p in ['做不到', '做得到']):
            return ('MS', 0.93, 'ability=mental state (v67_FIXED2)')

        # ================================================================
        # End of DISP Exclusions
        # ================================================================

        # ================================================================
        # End of V67 Pattern Fixes
        # ================================================================

        # ================================================================
        # PRIORITY 3: Cognitive/Emotional distinction
        # ================================================================
        if predicate in self.FEELING_MARKERS:
            return ('MS', 0.92, f'{predicate}=affective response marker (v60.2)')

        if predicate in self.EMOTIONAL_RESPONSE_VERBS:
            return ('MS', 0.90, f'{predicate}=emotional response (v60.2)')

        for pattern in self.EMOTIONAL_STATES_MS:
            if pattern in pred_comp or predicate == pattern:
                return ('MS', 0.90, f'{pattern}=emotional state (v60.2)')

        if predicate in self.CONSCIOUS_ENGAGEMENT_MS_VERBS:
            return ('MS', 0.90, f'{predicate}=conscious psychological engagement (v60.2)')

        if predicate in self.INTERNAL_PSYCH_MS_VERBS:
            return ('MS', 0.88, f'{predicate}=internal psychological state (v60.2)')

        if predicate in self.LOYALTY_MS_VERBS:
            return ('MS', 0.90, f'{predicate}=loyalty/commitment (v60.2)')

        # V60.3: Cognitive STATE verbs → MS
        if predicate in self.COGNITIVE_STATE_MS_VERBS:
            return ('MS', 0.92, f'{predicate}=cognitive state triggered by Y (v60.3)')

        if predicate in self.COGNITIVE_ABT_VERBS:
            return ('ABT', 0.92, f'{predicate}=cognitive orientation ABOUT (v60.2)')

        if predicate in self.DISCOURSE_ABT_VERBS:
            return ('ABT', 0.92, f'{predicate}=discourse ABOUT (v60.2)')

        if predicate in self.STANCE_ABT_VERBS:
            return ('ABT', 0.90, f'{predicate}=stance REGARDING (v60.2)')

        # V60.4: Emotional avoidance idioms → MS
        for idiom in self.EMOTIONAL_AVOIDANCE_MS:
            if idiom in pred_comp or predicate == idiom:
                return ('MS', 0.90, f'{idiom}=emotional avoidance (v60.4)')

        # V60.6: Cognitive STATE idioms → MS
        for idiom in self.COGNITIVE_STATE_IDIOMS_MS:
            if idiom in pred_comp or predicate == idiom:
                return ('MS', 0.92, f'{idiom}=cognitive STATE (v60.8)')

        for idiom in self.ABT_IDIOMS:
            if idiom in pred_comp or predicate == idiom:
                return ('ABT', 0.94, f'{idiom}=cognitive stance ABOUT')

        # ================================================================
        # PRIORITY 4: SI verbs
        # ================================================================
        if predicate in self.INSTITUTIONAL_SI_VERBS:
            return ('SI', 0.92, f'{predicate}=institutional intervention ON')

        if predicate in self.CARE_SI_VERBS:
            return ('SI', 0.92, f'{predicate}=care/help ON (Y affected)')

        if predicate in self.TOLERANCE_SI_VERBS:
            # V60.8: 忍受/谅解 with inanimate Y or negation → MS
            if predicate in {'忍受', '容忍'}:
                if not y_is_animate:
                    return ('MS', 0.88, f'{predicate}+inan Y=internal endurance (v60.8)')
            if predicate == '谅解':
                if '不' in concordance or '没' in concordance:
                    return ('MS', 0.88, '谅解+negation=emotional non-understanding (v60.8)')
            return ('SI', 0.92, f'{predicate}=tolerance ON')

        if predicate in self.POLICY_SI_VERBS:
            return ('SI', 0.90, f'{predicate}=policy application ON')

        if predicate in self.CONTROL_SI_VERBS:
            return ('SI', 0.88, f'{predicate}=control ON')

        # ================================================================
        # V70 CRITICAL FIX: 说 (SPEAK) - Reversed animacy logic
        # ================================================================
        # Problem: Animacy detection misses many names/people
        # Solution: Default to DA (speak TO), only ABT if CLEARLY inanimate
        if predicate in {'说', '讲', '喊', '叫', '问', '答', '骂', '嚷', '嘟'}:
            # Define CLEAR inanimate markers (topics/abstract concepts)
            clear_inanimate_markers = {
                # Topics/concepts
                '问题', '事情', '情况', '现象', '事件', '案件', '事实', '真相',
                '话题', '议题', '题目', '主题', '内容', '观点', '看法', '意见',
                # Abstract
                '政策', '制度', '措施', '方法', '方案', '计划', '规定', '条例',
                '理论', '思想', '原则', '道理', '理由', '原因', '结果',
                '技术', '科学', '文化', '历史', '经济', '社会', '市场',
                # Work/projects
                '工作', '任务', '项目', '活动', '研究', '调查', '分析',
                # Objects
                '产品', '商品', '物品', '东西', '事物', '材料', '设备',
            }
            
            # Check if Y is CLEARLY inanimate
            is_clearly_inanimate = any(marker in y_phrase for marker in clear_inanimate_markers)
            
            # V70 FIX: Also check for topic-indicating words in concordance
            topic_indicators = ['关于', '有关', '涉及', '针对', '就']
            has_topic_indicator = any(ind in concordance for ind in topic_indicators)
            
            if is_clearly_inanimate or has_topic_indicator:
                return ('ABT', 0.92, f'{predicate}=discourse ABOUT topic (v70)')
            else:
                # Default: DA (speak TO recipient)
                # This catches all names, people, even if not detected as animate
                return ('DA', 0.94, f'{predicate}=speech TO recipient (v70 default)')

        # V60.5: 抱怨 + animate/institution Y → DA
        if predicate == '抱怨':
            if y_is_animate or y_is_institution:
                return ('DA', 0.90, '抱怨=complain TO recipient (v60.8)')
            else:
                return ('ABT', 0.80, '抱怨=complain ABOUT inanimate Y (v60.5)')

        # V60.4: Gesture verbs + animate Y → DA
        if predicate in self.GESTURE_DA_VERBS and y_is_animate:
            return ('DA', 0.92, f'{predicate}=gesture TO animate Y (v60.4)')

        # V60.8: 反映 - special pattern handling
        if predicate == '反映':
            quality_words = ['不错', '很大', '较大', '很好', '很差', '强烈', '不好', '一般']
            for qw in quality_words:
                if qw in pred_comp or qw in concordance[concordance.find('反映'):concordance.find('反映') + 10]:
                    return ('ABT', 0.90, '反映+quality=feedback ABOUT (v60.8)')
            if y_is_animate or y_is_institution:
                return ('DA', 0.85, '反映=report TO recipient (v60.8)')
            else:
                return ('ABT', 0.85, '反映=reflect ABOUT topic (v60.8)')

        # ================================================================
        # PRIORITY 5: Communicative verbs
        # ================================================================
        if predicate in self.COMMUNICATIVE_VERBS:
            if y_is_animate or y_is_institution:
                return ('DA', 0.90, f'{predicate}=speech TO recipient (v60.8)')
            else:
                return ('ABT', 0.85, f'{predicate}=discourse ABOUT inanimate Y')

        # ================================================================
        # PRIORITY 6: DISP patterns (V60.8: STATIVE only)
        # V68 FIX: Increased confidence - these are prototypical manner verbs
        # ================================================================
        if predicate in self.PURE_MANNER_DISP_VERBS and y_is_animate:
            return ('DISP', 0.94, f'{predicate}=external manner toward Y (v68)')

        # V60.8: Treatment verbs need careful handling
        # 对待/善待/厚待 etc. are now SI (active verbs V他✓)
        # Only stative manner predicates remain DISP

        # ================================================================
        # PRIORITY 7: Evaluative predicates
        # ================================================================
        if predicate in self.EVAL_PREDICATES:
            return ('EVAL', 0.88, f'{predicate}=evaluative FOR')

        # ================================================================
        # PRIORITY 8: 是 patterns
        # ================================================================
        if predicate == '是':
            abt_de = {'了解的', '熟悉的', '清楚的', '知道的', '明白的', '理解的',
                      '熟知的', '深知的', '认识的', '懂的', '懂得的',
                      '确定的', '肯定的', '相信的', '怀疑的', '负责的', '负责任的'}
            for comp in abt_de:
                if comp in pred_comp:
                    return ('ABT', 0.90, f'是+{comp}=cognitive aboutness (v60.2)')

            disp_de = {'真心的', '真诚的', '诚心的', '诚恳的', '诚实的',
                       '友好的', '友善的', '善意的', '热心的', '热情的',
                       '冷淡的', '冷漠的', '无情的', '残忍的', '残酷的',
                       '公平的', '公正的', '公开的', '坦诚的', '坦白的',
                       '认真的', '严肃的', '严格的', '宽容的', '宽厚的',
                       '忠诚的', '忠心的', '忠实的'}
            for comp in disp_de:
                if comp in pred_comp:
                    return ('DISP', 0.93, f'是+{comp}=manner toward Y (v68)')

            eval_nouns = {'干扰', '打扰', '骚扰', '例外', '特例', '特殊',
                          '威胁', '危险', '危害', '隐患', '挑战', '考验', '难题',
                          '负担', '累赘', '包袱', '损失', '损害', '伤害',
                          '帮助', '好处', '益处', '利益', '安慰', '鼓励', '支持',
                          '打击', '刺激', '冲击', '侮辱', '羞辱', '耻辱'}
            for noun in eval_nouns:
                if noun in pred_comp:
                    return ('EVAL', 0.88, f'是+{noun}=X is {noun} FOR Y')

        # ================================================================
        # PRIORITY 9: 作/做 patterns
        # ================================================================
        if predicate in ['作', '做']:
            discourse_comp = {'分析', '研究', '探讨', '考察', '调查', '评估', '评价',
                              '介绍', '鉴定', '结论', '诊断', '裁判'}
            for dc in discourse_comp:
                if dc in pred_comp:
                    return ('ABT', 0.90, f'{predicate}+{dc}=discourse ABOUT (v60.2)')

            intervention_comp = {'处理', '决定', '判决', '处罚', '裁决', '安排'}
            for ic in intervention_comp:
                if ic in pred_comp:
                    return ('SI', 0.88, f'{predicate}+{ic}=intervention ON')

        if '作出' in pred_comp or '做出' in pred_comp:
            if '贡献' in pred_comp:
                return ('SI', 0.90, '作出贡献=contribution affecting Y (v60.2)')

        # ================================================================
        # PRIORITY 10: Soft fallback
        # ================================================================
        if not y_is_animate:
            cog_chars = set('想思考虑知道认识了解明白懂悟解析研究')
            if any(c in predicate for c in cog_chars):
                return ('ABT', 0.70, 'cognitive char + inanimate Y → ABT')

            effect_chars = set('利害益损伤危影响效')
            if any(c in predicate for c in effect_chars):
                return ('EVAL', 0.70, 'effect char + inanimate Y → EVAL')

        if y_is_animate:
            manner_chars = set('冷热亲疏远近松紧严宽软硬')
            if any(c in predicate for c in manner_chars):
                return ('DISP', 0.70, 'manner char + animate Y → DISP')

            emotion_chars = set('爱恨怕惧怒喜悲哀忧愁烦厌羡慕嫉')
            if any(c in predicate for c in emotion_chars):
                return ('MS', 0.70, 'emotion char + animate Y → MS')

        return (None, 0.0, None)

    def _is_animate(self, y_phrase: str, y_anim: str) -> bool:
        """
        Determine if Y is animate.
        V68: Improved with Chinese name detection
        """
        # Check explicit y_anim parameter first
        if y_anim in ['anim', 'animate', 'a', '1', 'true']:
            return True
        if y_anim in ['inan', 'inanimate', 'i', '0', 'false']:
            return False

        # Check for explicit animate markers
        for marker in self.ANIMATE_Y_MARKERS:
            if marker in y_phrase:
                return True
        
        # Check for explicit inanimate markers (stronger signal)
        for marker in self.INANIMATE_Y_MARKERS:
            if marker in y_phrase:
                return False

        # V68 FIX: Check for Chinese name patterns
        if y_phrase and len(y_phrase) >= 2 and len(y_phrase) <= 4:
            # Pattern 1: Starts with common surname
            if y_phrase[0] in self.COMMON_SURNAMES:
                return True
            
            # Pattern 2: Contains title markers
            title_markers = ['先生', '女士', '小姐', '老师', '主任', '经理', 
                           '厂长', '校长', '院长', '部长', '总统', '总理', '书记']
            if any(marker in y_phrase for marker in title_markers):
                return True
            
            # Pattern 3: Ends with plural marker 们
            if y_phrase.endswith('们'):
                base = y_phrase[:-1]
                if base in self.COMMON_SURNAMES or base in self.ANIMATE_Y_MARKERS:
                    return True

        # Old heuristic: short phrases without inanimate markers → animate
        # V68: Keep but make it conditional on not having clear inanimate signals
        if y_phrase and len(y_phrase) <= 4:
            if not any(m in y_phrase for m in self.INANIMATE_Y_MARKERS):
                # Only if it doesn't look like a concept/object
                if not any(char in y_phrase for char in ['性', '化', '度', '率', '量']):
                    return True

        return False


# ============================================================================
# BERT CLASSIFIER
# ============================================================================

class DuiConstructionDataset(Dataset):
    def __init__(self, df, tokenizer, config, label2id):
        self.df = df
        self.tokenizer = tokenizer
        self.config = config
        self.label2id = label2id

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        concordance = str(row.get(self.config.col_concordance, ""))
        predicate = str(row.get(self.config.col_predicate, ""))
        pred_comp = str(row.get(self.config.col_pred_comp, ""))
        y_phrase = str(row.get(self.config.col_y, ""))
        y_anim = str(row.get(self.config.col_y_anim, ""))

        text_a = concordance
        text_b = f"{predicate} | {pred_comp} | {y_phrase} | {y_anim}"

        encoding = self.tokenizer(text_a, text_b, max_length=self.config.max_seq_length,
                                  padding='max_length', truncation=True, return_tensors='pt')

        label_str = str(row.get(self.config.col_type, "")).upper()
        label_id = self.label2id.get(label_str, 0)



# For web app use - BERT components removed for lighter deployment
if __name__ == "__main__":
    print("V70 Lite Classifier - Rule-Based Only")
    classifier = RuleBasedClassifier()
    print("✅ Classifier loaded successfully")

