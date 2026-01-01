#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对-Construction Rule-Based Classifier (v70 - Web App Lite Version)
==================================================================
Minimal version for web deployment - ONLY rule-based classification
NO BERT, NO torch, NO tqdm - just pure Python!

Author: Jiaqi's Dui-construction Project
Version: v70-lite-minimal
"""

import re
from typing import Tuple

# ============================================================================
# RULE-BASED CLASSIFIER (v70)
# ============================================================================

class RuleBasedClassifier:
    """
    Rule-based classifier for 对-constructions
    Version 70 with all critical fixes
    """
    
    def __init__(self):
        """Initialize classifier with predicate lists"""
        
        # Core predicate sets
        self.SPEECH_VERBS = {
            '说', '讲', '告诉', '问', '答', '回答', '解释', '说明', '介绍',
            '表示', '声明', '宣布', '通知', '报告', '汇报', '反映', '提及',
            '谈', '聊', '交谈', '交流', '沟通', '商谈', '商量', '商议',
            '承认', '否认', '坦白', '坦承', '招认', '供认', '透露', '泄露',
            '建议', '劝告', '劝说', '劝', '警告', '告诫', '忠告', '提醒',
            '夸', '赞', '称赞', '赞扬', '赞美', '表扬', '吹捧', '奉承',
            '骂', '责骂', '辱骂', '咒骂', '斥责', '批评', '指责', '责备',
            '喊', '叫', '呼喊', '呼叫', '叫喊', '大喊', '大叫', '呐喊',
            '嚷', '嚷嚷', '嘟囔', '嘟哝', '念叨', '唠叨', '絮叨'
        }
        
        self.PROCEDURAL_SI_VERBS = {
            '进行', '实行', '实施', '执行', '推行', '施行', '开展', '展开',
            '管理', '处理', '办理', '治理', '整治', '整顿', '管制', '控制',
            '采取', '实施', '施加', '加以', '予以', '给予', '赋予',
            '提供', '供给', '供应', '配给', '发放', '分配', '分发',
            '加强', '强化', '巩固', '改善', '改进', '改良', '完善',
            '监督', '监管', '监控', '检查', '审查', '核查', '查验'
        }
        
        self.MS_FEELING_VERBS = {
            '感到', '觉得', '认为', '以为', '感觉', '觉着',
            '担心', '忧虑', '忧心', '担忧', '发愁', '犯愁',
            '满意', '满足', '知足', '欣慰', '高兴', '开心',
            '喜欢', '喜爱', '爱', '钟爱', '热爱', '酷爱',
            '讨厌', '厌恶', '憎恨', '恨', '仇恨', '痛恨',
            '了解', '熟悉', '理解', '明白', '懂得', '知道',
            '信任', '相信', '信赖', '依赖', '怀疑', '疑惑',
            '关心', '在意', '重视', '看重', '珍惜', '珍视',
            '敬佩', '佩服', '钦佩', '羡慕', '嫉妒', '妒忌',
            '想念', '思念', '怀念', '留恋', '牵挂', '挂念',
            '感激', '感谢', '感恩', '抱歉', '歉疚', '内疚'
        }
        
        self.ABT_RESEARCH_VERBS = {
            '研究', '分析', '分析', '讨论', '调查', '调研',
            '考察', '考查', '探讨', '探究', '探索', '探寻',
            '观察', '观测', '检测', '检验', '测试', '测验',
            '审查', '审核', '审视', '鉴定', '评估', '评价'
        }
        
        self.PURE_MANNER_DISP_VERBS = {
            '友好', '友善', '善良', '和善', '和气', '和蔼',
            '热情', '热心', '热忱', '亲切', '亲热', '亲密',
            '认真', '严肃', '严格', '严厉', '严苛', '苛刻',
            '负责', '负责任', '尽责', '礼貌', '客气', '谦虚',
            '冷淡', '冷漠', '冷酷', '无情', '残忍', '残酷',
            '温柔', '温和', '和婉', '柔和', '粗暴', '粗鲁',
            '体贴', '关怀', '关照', '真诚', '诚恳', '诚实',
            '公平', '公正', '公道', '偏心', '偏袒', '袒护',
            '忠诚', '忠实', '忠心', '专一', '专情', '恩爱',
            '孝顺', '恭敬', '尊敬', '尊重', '顺从', '听话'
        }
        
        self.EVAL_PREDICATES = {
            '重要', '关键', '要紧', '紧要', '必要', '需要',
            '有利', '有益', '有用', '有效', '有好处', '有帮助',
            '有害', '不利', '无益', '无用', '无效', '有坏处',
            '危险', '安全', '致命', '严重', '宝贵', '珍贵'
        }
        
        self.GESTURE_DA_VERBS = {
            '点头', '摇头', '招手', '挥手', '摆手', '挥挥手',
            '鞠躬', '作揖', '磕头', '下跪', '示意', '打手势'
        }
        
        self.COMMUNICATIVE_VERBS = {
            '表达', '表白', '吐露', '倾诉', '诉说', '诉苦',
            '抱怨', '埋怨', '怨恨', '发牢骚', '叫苦'
        }
        
        # V68: Chinese surnames (百家姓 top 100)
        self.CHINESE_SURNAMES = {
            '李', '王', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴',
            '徐', '孙', '马', '朱', '胡', '郭', '何', '高', '林', '罗',
            '郑', '梁', '谢', '宋', '唐', '许', '韩', '冯', '邓', '曹',
            '彭', '曾', '肖', '田', '董', '袁', '潘', '于', '蒋', '蔡',
            '余', '杜', '叶', '程', '苏', '魏', '吕', '丁', '任', '沈',
            '姚', '卢', '姜', '崔', '钟', '谭', '陆', '汪', '范', '金',
            '石', '廖', '贾', '夏', '韦', '付', '方', '白', '邹', '孟',
            '熊', '秦', '邱', '江', '尹', '薛', '闫', '段', '雷', '侯',
            '龙', '史', '陶', '黎', '贺', '顾', '毛', '郝', '龚', '邵',
            '万', '钱', '严', '覃', '武', '戴', '莫', '孔', '向', '汤'
        }

    def _is_animate(self, y_phrase: str) -> bool:
        """Detect if Y is animate (person/animal)"""
        
        # Pronouns
        animate_pronouns = {'我', '你', '他', '她', '您', '咱', '俺', '它', '人家'}
        if y_phrase in animate_pronouns:
            return True
        
        # Chinese name pattern: Surname + 1-2 characters
        if len(y_phrase) >= 2 and y_phrase[0] in self.CHINESE_SURNAMES:
            return True
        
        # Title markers
        title_markers = {
            '老师', '教授', '博士', '先生', '女士', '小姐', '同志',
            '经理', '主任', '部长', '局长', '科长', '处长', '校长',
            '院长', '书记', '主席', '总理', '主管', '领导', '老板',
            '员工', '职工', '工人', '农民', '学生', '同学', '朋友'
        }
        if any(marker in y_phrase for marker in title_markers):
            return True
        
        # Plural marker
        if '们' in y_phrase:
            return True
        
        # Generic person words
        person_words = {
            '人', '孩子', '小孩', '父母', '爸爸', '妈妈', '儿子', '女儿',
            '兄弟', '姐妹', '亲人', '家人', '客户', '顾客', '观众', '读者'
        }
        if any(word in y_phrase for word in person_words):
            return True
        
        return False
    
    def _is_institution(self, y_phrase: str) -> bool:
        """Detect if Y is an institution/organization"""
        institution_markers = {
            '公司', '企业', '政府', '机关', '部门', '单位', '组织',
            '学校', '医院', '银行', '法院', '警察', '军队', '团队',
            '委员会', '协会', '学会', '研究所', '实验室', '中心'
        }
        return any(marker in y_phrase for marker in institution_markers)

    def classify(self, 
                 concordance: str, 
                 predicate: str, 
                 pred_comp: str, 
                 y_phrase: str, 
                 y_anim: str = "") -> Tuple[str, float, str]:
        """
        Classify a 对-construction
        
        Args:
            concordance: Full sentence
            predicate: Main predicate
            pred_comp: Predicate + complement
            y_phrase: Y phrase (object of 对)
            y_anim: Animacy label (optional)
            
        Returns:
            (label, confidence, reason)
        """
        
        # Detect animacy
        y_is_animate = self._is_animate(y_phrase) or y_anim.lower() == 'anim'
        y_is_institution = self._is_institution(y_phrase)
        
        # ================================================================
        # PRIORITY 1: 很/非常 + adjective → DISP (manner)
        # ================================================================
        degree_markers = ['很', '非常', '特别', '十分', '相当', '挺', '蛮', '太']
        for marker in degree_markers:
            if marker in pred_comp:
                manner_adjs = {
                    '好', '坏', '差', '友好', '热情', '认真', '严格', '负责',
                    '礼貌', '客气', '冷淡', '温柔', '粗暴', '体贴', '冷漠',
                    '真诚', '诚恳', '公平', '忠诚', '善良', '凶恶'
                }
                if any(adj in pred_comp for adj in manner_adjs):
                    return ('DISP', 0.94, f'{marker}+adjective=manner pattern (v70)')
        
        # ================================================================
        # PRIORITY 2: 进行 → ALWAYS SI
        # ================================================================
        if predicate == '进行':
            return ('SI', 0.94, '进行=procedural intervention (v67)')
        
        # ================================================================
        # PRIORITY 3: Speech verbs (V70 reversed logic)
        # ================================================================
        if predicate in self.SPEECH_VERBS:
            # Define CLEAR inanimate markers
            clear_inanimate_markers = {
                '问题', '事情', '情况', '现象', '事件', '话题', '议题',
                '观点', '看法', '意见', '主题', '内容',
                '政策', '制度', '措施', '方法', '方案', '计划',
                '工作', '任务', '项目', '活动', '研究', '调查'
            }
            
            is_clearly_inanimate = any(marker in y_phrase for marker in clear_inanimate_markers)
            topic_indicators = ['关于', '有关', '涉及', '针对', '就']
            has_topic_indicator = any(ind in concordance for ind in topic_indicators)
            
            if is_clearly_inanimate or has_topic_indicator:
                return ('ABT', 0.92, f'{predicate}=discourse ABOUT topic (v70)')
            else:
                return ('DA', 0.94, f'{predicate}=speech TO recipient (v70 default)')
        
        # ================================================================
        # PRIORITY 4: Procedural verbs → SI
        # ================================================================
        if predicate in self.PROCEDURAL_SI_VERBS:
            return ('SI', 0.94, f'{predicate}=procedural intervention (v70)')
        
        # ================================================================
        # PRIORITY 5: Mental state verbs → MS
        # ================================================================
        if predicate in self.MS_FEELING_VERBS:
            return ('MS', 0.93, f'{predicate}=internal mental state (v70)')
        
        # ================================================================
        # PRIORITY 6: Research verbs → ABT
        # ================================================================
        if predicate in self.ABT_RESEARCH_VERBS:
            return ('ABT', 0.92, f'{predicate}=discourse/research ABOUT topic (v70)')
        
        # ================================================================
        # PRIORITY 7: Pure manner verbs → DISP
        # ================================================================
        if predicate in self.PURE_MANNER_DISP_VERBS and y_is_animate:
            return ('DISP', 0.94, f'{predicate}=manner toward person (v70)')
        
        # ================================================================
        # PRIORITY 8: Evaluative predicates → EVAL
        # ================================================================
        if predicate in self.EVAL_PREDICATES:
            return ('EVAL', 0.88, f'{predicate}=evaluative property (v70)')
        
        # ================================================================
        # PRIORITY 9: Gesture verbs + animate → DA
        # ================================================================
        if predicate in self.GESTURE_DA_VERBS and y_is_animate:
            return ('DA', 0.92, f'{predicate}=gesture TO person (v70)')
        
        # ================================================================
        # PRIORITY 10: Communicative verbs
        # ================================================================
        if predicate in self.COMMUNICATIVE_VERBS:
            if y_is_animate or y_is_institution:
                return ('DA', 0.90, f'{predicate}=communication TO recipient (v70)')
            else:
                return ('ABT', 0.85, f'{predicate}=discourse ABOUT topic (v70)')
        
        # ================================================================
        # PRIORITY 11: 是 patterns
        # ================================================================
        if predicate == '是':
            # DISP: 是 + manner adjective + 的
            disp_de = {'真诚的', '友好的', '认真的', '严格的', '负责的'}
            if any(comp in pred_comp for comp in disp_de):
                return ('DISP', 0.93, f'是+{pred_comp}=manner (v70)')
            
            # EVAL: 是 + evaluative noun
            eval_nouns = {'威胁', '危险', '挑战', '帮助', '好处', '坏处'}
            if any(noun in pred_comp for noun in eval_nouns):
                return ('EVAL', 0.88, f'是+{pred_comp}=evaluative (v70)')
        
        # ================================================================
        # PRIORITY 12: 有 patterns
        # ================================================================
        if predicate == '有':
            # EVAL: 有益/有害/有利
            if any(word in pred_comp for word in ['益', '害', '利', '用', '好处', '坏处']):
                return ('EVAL', 0.92, f'有+{pred_comp}=evaluative (v70)')
            
            # MS: 有感情/有好感
            if any(word in pred_comp for word in ['感情', '好感', '兴趣', '印象', '了解']):
                return ('MS', 0.90, f'有+{pred_comp}=mental state (v70)')
        
        # ================================================================
        # DEFAULT: ABT (safest fallback)
        # ================================================================
        return ('ABT', 0.70, 'Default classification (v70)')


# For testing
if __name__ == "__main__":
    print("V70 Lite Classifier - Rule-Based Only (Minimal Version)")
    classifier = RuleBasedClassifier()
    print("✅ Classifier loaded successfully")
    
    # Test cases
    test_cases = [
        ("他对我很坏", "我", "很坏", "坏"),
        ("我对他很了解", "他", "很了解", "了解"),
        ("专家对问题进行研究", "问题", "进行研究", "进行"),
    ]
    
    print("\n🧪 Running test cases:")
    for sent, y, pred_comp, pred in test_cases:
        label, conf, reason = classifier.classify(sent, pred, pred_comp, y)
        print(f"\n'{sent}'")
        print(f"  → {label} ({conf:.0%}) - {reason}")
