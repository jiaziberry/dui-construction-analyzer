# -*- coding: utf-8 -*-
"""
Classifier Wrapper Module
==========================
Wraps the v70 rule-based classifier for the Streamlit app.
"""

import sys
import os
from typing import Dict, Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)

# Import the rule-based classifier
# We'll recreate the core classification logic here to avoid dependency issues
# This is adapted from dui_classifier_v70.py


class DuiClassifier:
    """
    Classifier for 对-constructions.
    Implements the v70 rule-based classification framework.
    """
    
    def __init__(self):
        self._init_lexicons()
    
    def _init_lexicons(self):
        """Initialize lexicons for classification."""
        
        # Speech verbs (DA)
        self.SPEECH_VERBS = {
            '说', '讲', '谈', '聊', '问', '答', '告诉', '通知', '报告',
            '解释', '说明', '介绍', '描述', '陈述',
            '表达', '表示', '表明', '声明', '宣布', '宣称', '发表',
            '提出', '建议', '呼吁', '号召',
            '批评', '称赞', '赞扬', '夸奖', '责备', '指责', '责怪',
            '表扬', '嘉奖', '褒奖', '鼓励', '激励', '勉励',
            '警告', '告诫', '劝告', '劝诫', '训诫', '教训',
            '道歉', '致歉', '感谢', '致谢',
        }
        
        # Speech 道 verbs (always DA)
        self.SPEECH_DAO_VERBS = {
            '笑道', '哭道', '说道', '问道', '答道', '叫道', '喊道',
            '骂道', '怒道', '冷道', '淡道', '道',
            '低声道', '大声道', '高声道', '轻声道', '厉声道',
        }
        
        # Gesture verbs (DA with animate Y)
        self.GESTURE_VERBS = {
            '摇', '点', '摇头', '点头', '挥手', '招手', '摆手',
            '瞪', '瞥', '盯', '注视', '凝视',
            '微笑', '笑', '冷笑', '苦笑', '傻笑',
        }
        
        # SI verbs (intervention)
        self.SI_VERBS = {
            '进行', '实行', '实施', '执行', '施行', '采用', '采取',
            '推行', '贯彻', '落实', '开展', '展开',
            '检查', '核查', '稽查', '督查', '审查', '审批', '批准',
            '整顿', '改革', '治理', '管控', '管辖', '督促',
            '处理', '处置', '处罚', '惩罚', '惩处',
            '制裁', '打击', '整治', '查处',
            '保护', '监管', '管制', '软禁', '限制', '约束',
            '帮助', '援助', '救助', '扶助', '协助', '辅助',
            '照顾', '照料', '关照', '照看', '照应', '看护', '护理',
            '培训', '训练', '教育', '培养',
            '原谅', '包容', '宽恕', '体谅', '迁就', '忍让',
            '负责', '负', '使用', '运用', '利用',
            '给予', '予以', '施加',
        }
        
        # MS verbs (mental state)
        self.MS_VERBS = {
            # Emotional
            '喜欢', '喜爱', '爱', '热爱', '深爱', '钟爱', '宠爱', '溺爱',
            '讨厌', '厌恶', '厌烦', '嫌恶', '嫌弃', '反感', '抵触',
            '害怕', '恐惧', '畏惧', '惧怕', '惊惧', '惶恐', '畏缩',
            '担心', '担忧', '操心', '忧虑', '焦虑', '顾虑', '忧心',
            '痛恨', '憎恨', '仇恨', '憎恶',
            '感激', '感恩', '怨恨', '记恨',
            '着迷', '入迷', '上瘾', '沉迷', '痴迷',
            '满意', '不满', '失望', '绝望',
            '佩服', '敬佩', '钦佩', '崇拜', '景仰',
            '嫉妒', '羡慕', '眼红',
            # Emotional - anger/happiness
            '愤怒', '生气', '气愤', '恼怒', '发怒', '愤慨',
            '高兴', '开心', '快乐', '欢喜', '喜悦',
            '惊讶', '惊奇', '诧异', '吃惊', '震惊',
            # State verbs
            '充满', '充斥', '弥漫',
            # Cognitive/Experiential
            '了解', '理解', '认识', '熟悉', '知道', '知晓', '明白', '懂',
            '掌握', '把握', '洞悉', '洞察', '通晓', '深知',
            '怀疑', '相信', '信任', '信赖', '依赖',
            '记得', '记住', '忆起', '想起', '回忆', '回想',
            '体会', '感受', '领会', '领悟', '体验',  # experiential cognition
            '印象', '有印象',  # impression
            # Attentional
            '重视', '注意', '关注', '留意', '在意', '在乎', '介意',
            '忽视', '无视', '漠视',
            '关心', '关怀', '关切', '挂心', '怜悯', '同情',
            '尊重', '尊敬', '敬重', '不敬', '敬畏',
            # Interest
            '感兴趣', '有兴趣',
        }
        
        # ABT verbs (aboutness/discourse)
        self.ABT_VERBS = {
            '评价', '评论', '评述', '点评', '评估', '评定', '评分', '评级',
            '分析', '研究', '探讨', '考察', '调查', '调研', '考证',
            '讨论', '辩论', '争论', '争议', '议论', '商议', '商讨',
            '报道', '报告', '陈述', '描述', '阐述', '论述',
            '判断', '推测', '预测', '预料', '预期', '预见', '猜测',
        }
        
        # DISP verbs/adjectives (manner)
        self.DISP_PREDICATES = {
            '热情', '冷淡', '冷漠', '热心', '客气', '礼貌', '有礼貌', '没礼貌',
            '温柔', '柔和', '和蔼', '亲切', '慈祥',
            '粗暴', '粗鲁', '蛮横', '野蛮', '霸道',
            '体贴', '细心', '周到', '殷勤',
            '严厉', '苛刻', '严苛', '严酷', '刻薄',
            '真诚', '诚恳', '忠诚', '直率', '坦白', '坦率',
            '公道', '厚道', '地道',
            '好', '不好', '坏', '友好', '不友好', '友善', '善意', '恶意',
            '认真', '不认真', '严肃', '宽容', '宽厚',
            '言听计从', '百依百顺', '唯命是从',
            '恭敬', '恭顺', '毕恭毕敬', '孝顺', '顺从', '服从',
            '像', '象', '如', '如同', '宛如', '犹如', '好像', '好似', '仿佛',
            '客气', '不客气', '耐心', '没耐心', '温和', '凶',
        }
        
        # EVAL predicates
        self.EVAL_PREDICATES = {
            '有用', '无用', '有效', '无效', '管用', '好使',
            '重要', '必要', '关键', '至关重要',
            '有利', '有害', '有益', '有意义',
            '适用', '实用', '中用', '顶用', '可行', '不行', '适合', '合适',
            '公平', '公正', '平等', '不公', '不公平', '不公正',
            '造成', '导致', '引起', '带来', '促进', '阻碍', '构成', '影响',
            '具有', '形成',
        }
        
        # Feeling markers (always MS)
        self.FEELING_MARKERS = {'感到', '觉得', '感觉', '深感', '倍感', '感'}
        
        # 有 complements for different types
        self.YOU_EVAL_COMPS = {
            '影响', '作用', '效果', '效应', '意义', '价值', '贡献',
            '好处', '益处', '害处', '坏处', '危害', '损害', '利', '弊',
            '用', '用处', '用途', '帮助', '启发', '启示', '借鉴',
            '吸引力', '说服力', '感染力', '约束力', '执行力',
            '压力', '支撑', '冲击', '威胁',
        }
        
        self.YOU_MS_COMPS = {
            '看法', '观点', '见解', '高见', '见地', '主张', '意见',
            '了解', '认识', '理解', '印象', '记忆', '概念', '把握',
            '成见', '偏见',
            '办法', '方法', '能力', '天分', '才能',
            '好感', '恶感', '反感', '厌恶', '敌意', '戒心', '戒备',
            '好奇', '好奇心', '兴趣', '热情', '激情', '感情', '深情',
            '信心', '信任', '信赖', '依赖', '依恋', '眷恋', '留恋',
            '同情', '同情心', '怜悯', '慈悲',
            '期待', '期望', '期盼', '向往', '憧憬', '幻想', '希望',
            '怀疑', '疑虑', '疑惧', '顾虑', '担忧', '担心',
            '不满', '怨言', '怨气', '异议',
            '感觉', '感受', '感触', '体会', '反应',
            '想法', '念头', '打算', '意向', '意愿', '企图', '野心',
        }
        
        self.YOU_ABT_COMPS = {
            '研究', '心得', '体验', '发现', '认知',
            '评价', '分析', '判断', '论述', '总结', '描述',
            '招', '招数', '手段', '对策', '措施',
            '规定', '规则', '定论',
            '微词', '批判', '揭露',
        }
        
        # Animate markers
        self.ANIMATE_MARKERS = {
            '我', '你', '他', '她', '您', '咱', '它', '我们', '你们', '他们', '她们', '咱们',
            '自己', '本人', '人家', '别人', '大家', '各位', '谁', '某人', '有人', '对方',
            '人', '人们', '学生', '老师', '医生', '患者', '观众', '读者', '孩子',
            '父母', '朋友', '同事', '客人', '员工', '领导', '群众', '民众', '百姓',
        }
        
        self.INANIMATE_MARKERS = {
            '事', '事情', '问题', '情况', '现象', '结果',
            '政策', '制度', '措施', '方法', '做法', '方案', '计划',
            '工作', '任务', '项目', '活动', '行动',
            '社会', '国家', '市场', '经济', '发展',
        }
        
        # Common surnames
        self.COMMON_SURNAMES = {
            '李', '王', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴',
            '徐', '孙', '马', '胡', '朱', '郭', '何', '林', '罗', '高',
        }
    
    def classify(self, concordance: str, predicate: str, pred_comp: str,
                 y_phrase: str, y_anim: str) -> Tuple[str, float, str]:
        """
        Classify a 对-construction instance.
        
        Args:
            concordance: Full sentence
            predicate: Main predicate
            pred_comp: Predicate + complement
            y_phrase: Y argument
            y_anim: Animacy of Y ('anim' or 'inan')
            
        Returns:
            Tuple of (label, confidence, reason)
        """
        # Clean inputs
        predicate = str(predicate).strip() if predicate else ""
        pred_comp = str(pred_comp).strip() if pred_comp else ""
        y_phrase = str(y_phrase).strip() if y_phrase else ""
        y_anim = str(y_anim).lower().strip() if y_anim else "inan"
        concordance = str(concordance).strip() if concordance else ""
        
        y_is_animate = self._is_animate(y_phrase, y_anim)
        
        # Priority 1: Speech 道 verbs → DA
        if predicate in self.SPEECH_DAO_VERBS:
            return ('DA', 0.95, f'{predicate} = speech/narration TO Y (speech verb)')
        
        # Priority 2: Feeling markers → MS
        if predicate in self.FEELING_MARKERS:
            return ('MS', 0.92, f'{predicate} = affective response marker (feeling)')
        
        # Priority 3: 进行 → always SI
        if predicate == '进行':
            return ('SI', 0.94, '进行 = procedural intervention ON scope')
        
        # Priority 4: EVAL predicates
        if predicate in self.EVAL_PREDICATES:
            return ('EVAL', 0.90, f'{predicate} = evaluative FOR Y')
        
        # Priority 5: 有 patterns
        if predicate == '有' or predicate == '没有' or predicate == '没':
            # Check complements
            for comp in self.YOU_EVAL_COMPS:
                if comp in pred_comp:
                    return ('EVAL', 0.92, f'有+{comp} = effect/benefit FOR Y')
            for comp in self.YOU_MS_COMPS:
                if comp in pred_comp:
                    return ('MS', 0.90, f'有+{comp} = psychological state')
            for comp in self.YOU_ABT_COMPS:
                if comp in pred_comp:
                    return ('ABT', 0.88, f'有+{comp} = discourse ABOUT Y')
            # Default 有
            return ('MS', 0.75, '有 = having state (default)')
        
        # Priority 6: MS verbs
        if predicate in self.MS_VERBS:
            return ('MS', 0.90, f'{predicate} = psychological state triggered by Y')
        
        # Priority 7: ABT verbs
        if predicate in self.ABT_VERBS:
            return ('ABT', 0.90, f'{predicate} = discourse ABOUT Y')
        
        # Priority 8a: 负责 with degree adverbs → DISP (before SI check)
        if predicate == '负责':
            # Check for degree adverbs in concordance (很负责, 非常负责, etc.)
            degree_advs = ['很', '非常', '特别', '十分', '比较', '挺', '相当', '太']
            for adv in degree_advs:
                if adv + '负责' in concordance:
                    return ('DISP', 0.88, f'{adv}+负责 = responsible manner toward Y')
            # Bare 负责 → SI (accountability)
            return ('SI', 0.90, '负责 = accountability/obligation TO scope')
        
        # Priority 8: SI verbs
        if predicate in self.SI_VERBS:
            return ('SI', 0.90, f'{predicate} = intervention ON Y')
        
        # Priority 9: DISP predicates (with animate Y)
        if predicate in self.DISP_PREDICATES and y_is_animate:
            return ('DISP', 0.88, f'{predicate} = behavioral manner toward Y')
        
        # Priority 10: Speech verbs
        if predicate in self.SPEECH_VERBS:
            if y_is_animate:
                return ('DA', 0.88, f'{predicate} + animate Y = speech TO recipient')
            else:
                return ('ABT', 0.80, f'{predicate} + inanimate Y = discourse ABOUT topic')
        
        # Priority 11: Gesture verbs
        if predicate in self.GESTURE_VERBS and y_is_animate:
            return ('DA', 0.90, f'{predicate} = gesture TO animate Y')
        
        # Priority 12: 表示 patterns
        if predicate == '表示':
            if y_is_animate:
                return ('DA', 0.85, '表示 + animate Y = express TO recipient')
            else:
                return ('ABT', 0.85, '表示 + inanimate Y = express ABOUT topic')
        
        # Priority 13: 提出 patterns
        if predicate == '提出':
            return ('ABT', 0.88, '提出 = put forward discourse ABOUT Y')
        
        # Priority 14: 作出/做出 patterns
        if predicate in ['作出', '做出']:
            if '贡献' in pred_comp:
                return ('EVAL', 0.90, f'{predicate}+贡献 = contribution FOR Y')
            return ('ABT', 0.80, f'{predicate} = produce discourse ABOUT Y')
        
        # Fallback based on Y animacy and predicate characters
        if y_is_animate:
            # Check for manner characters
            manner_chars = set('冷热亲疏远近松紧严宽软硬')
            if any(c in predicate for c in manner_chars):
                return ('DISP', 0.70, 'manner char + animate Y → DISP')
            # Check for emotion characters
            emotion_chars = set('爱恨怕惧怒喜悲哀忧愁烦厌羡慕嫉')
            if any(c in predicate for c in emotion_chars):
                return ('MS', 0.70, 'emotion char + animate Y → MS')
            # Default for animate Y
            return ('DA', 0.60, 'animate Y default → DA')
        else:
            # Check for cognitive characters
            cog_chars = set('想思考虑知道认识了解明白懂悟解析研究')
            if any(c in predicate for c in cog_chars):
                return ('ABT', 0.70, 'cognitive char + inanimate Y → ABT')
            # Check for effect characters
            effect_chars = set('利害益损伤危影响效')
            if any(c in predicate for c in effect_chars):
                return ('EVAL', 0.70, 'effect char + inanimate Y → EVAL')
            # Default for inanimate Y
            return ('ABT', 0.55, 'inanimate Y default → ABT')
    
    def _is_animate(self, y_phrase: str, y_anim: str) -> bool:
        """Determine if Y is animate."""
        if y_anim in ['anim', 'animate', 'a', '1', 'true']:
            return True
        if y_anim in ['inan', 'inanimate', 'i', '0', 'false']:
            return False
        
        # Check markers
        for marker in self.ANIMATE_MARKERS:
            if marker in y_phrase:
                return True
        for marker in self.INANIMATE_MARKERS:
            if marker in y_phrase:
                return False
        
        # Check for names (surname + 1-2 chars)
        if y_phrase and len(y_phrase) >= 2 and len(y_phrase) <= 4:
            if y_phrase[0] in self.COMMON_SURNAMES:
                return True
        
        # Short phrases without inanimate markers → likely animate
        if y_phrase and len(y_phrase) <= 3:
            return True
        
        return False
    
    def get_classification_explanation(self, label: str, predicate: str, 
                                       y_phrase: str, y_anim: str, reason: str) -> Dict:
        """
        Generate a detailed explanation for the classification.
        
        Returns:
            Dictionary with explanation components
        """
        explanation = {
            'label': label,
            'predicate': predicate,
            'y_phrase': y_phrase,
            'y_animacy': 'animate' if y_anim == 'anim' else 'inanimate',
            'rule_reason': reason,
            'detailed_explanation': ''
        }
        
        if label == 'DA':
            explanation['detailed_explanation'] = f"""
The sentence is classified as **Directed-Action (DA)** because:
- The predicate '{predicate}' indicates an action directed TOWARD Y ('{y_phrase}')
- Y is the recipient/addressee of the action
- The action flows TO Y but does not necessarily transform Y
- Rule applied: {reason}
            """
        elif label == 'SI':
            explanation['detailed_explanation'] = f"""
The sentence is classified as **Scoped-Intervention (SI)** because:
- The predicate '{predicate}' indicates a bounded intervention UPON Y ('{y_phrase}')
- Y is the scope/patient that undergoes the intervention
- Y is affected by the action (changes state)
- Rule applied: {reason}
            """
        elif label == 'MS':
            explanation['detailed_explanation'] = f"""
The sentence is classified as **Mental-State (MS)** because:
- The predicate '{predicate}' indicates a psychological state
- Y ('{y_phrase}') is the stimulus that TRIGGERS this state in X
- This is an internal state (not observable from outside)
- Rule applied: {reason}
            """
        elif label == 'ABT':
            explanation['detailed_explanation'] = f"""
The sentence is classified as **Aboutness (ABT)** because:
- The predicate '{predicate}' indicates discourse/commentary ABOUT Y
- Y ('{y_phrase}') is the topic of the discourse
- X produces external, observable discourse about Y
- Rule applied: {reason}
            """
        elif label == 'DISP':
            explanation['detailed_explanation'] = f"""
The sentence is classified as **Disposition (DISP)** because:
- The predicate '{predicate}' indicates a behavioral manner TOWARD Y
- Y ('{y_phrase}') is the target of X's behavioral attitude
- This describes HOW X treats Y (observable manner)
- Rule applied: {reason}
            """
        elif label == 'EVAL':
            explanation['detailed_explanation'] = f"""
The sentence is classified as **Evaluation (EVAL)** because:
- The predicate '{predicate}' indicates an evaluation relative to Y
- Y ('{y_phrase}') is the perspective/beneficiary of the evaluation
- X is evaluated as good/bad/useful/harmful FOR Y
- Rule applied: {reason}
            """
        
        return explanation


# Singleton instance
_classifier = None

def get_classifier() -> DuiClassifier:
    """Get or create the classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = DuiClassifier()
    return _classifier


def classify_sentence(sentence: str, predicate: str = "", pred_comp: str = "",
                      y_phrase: str = "", y_anim: str = "") -> Dict:
    """
    Classify a sentence and return detailed results.
    
    Args:
        sentence: The full sentence
        predicate: Main predicate (extracted)
        pred_comp: Predicate + complement
        y_phrase: Y argument
        y_anim: Animacy of Y
        
    Returns:
        Dictionary with classification results and explanation
    """
    classifier = get_classifier()
    label, confidence, reason = classifier.classify(
        sentence, predicate, pred_comp, y_phrase, y_anim
    )
    
    explanation = classifier.get_classification_explanation(
        label, predicate, y_phrase, y_anim, reason
    )
    
    return {
        'label': label,
        'confidence': confidence,
        'reason': reason,
        'explanation': explanation,
        'predicate': predicate,
        'y_phrase': y_phrase,
        'y_anim': y_anim
    }
