# -*- coding: utf-8 -*-
"""
Classifier Wrapper Module (v70 Enhanced)
=========================================
Comprehensive rule-based classifier for Chinese 对-constructions.
Implements the complete v70 framework with 1,000+ linguistic rules.
"""

import sys
import os
from typing import Dict, Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)


class DuiClassifier:
    """
    Classifier for 对-constructions.
    Implements the comprehensive v70 rule-based classification framework.
    """
    
    def __init__(self):
        self._init_lexicons()
    
    def _init_lexicons(self):
        """Initialise all lexicons for classification."""
        
        # ================================================================
        # DA (Directed-Action) LEXICONS
        # ================================================================
        
        # Speech 道 verbs (always DA - quoted speech TO person)
        self.SPEECH_DAO_VERBS = {
            '笑道', '哭道', '说道', '问道', '答道', '叫道', '喊道',
            '骂道', '怒道', '冷道', '淡道', '道',
            '低声道', '大声道', '高声道', '轻声道', '厉声道',
            '冷冷道', '淡淡道', '怒喝道', '冷声道',
        }
        
        # Inherent addressee verbs (always DA - require recipient)
        self.INHERENT_ADDRESSEE_VERBS = {
            '呵斥', '斥责', '训斥', '责骂', '怒斥', '痛斥',
            '喝止', '喝令', '骂', '辱骂', '臭骂',
            '请求', '祈求', '央求', '哀求', '乞求',
        }
        
        # Gesture verbs (DA with animate Y)
        self.GESTURE_DA_VERBS = {
            '摇', '点', '摇头', '点头', '挥手', '招手', '摆手',
            '瞪', '瞥', '盯', '注视', '凝视',
            '微笑', '笑', '冷笑', '苦笑', '傻笑', '嘲笑',
        }
        
        # Speech action verbs (DA with animate Y)
        self.SPEECH_ACTION_TO_DA = {
            '提供', '感谢', '致歉', '下达', '送', '赞美', '嘲弄',
            '顶撞', '献计', '指责', '表扬', '批评',
            '说明', '解释', '交代', '隐瞒', '否认', '告诉', '汇报',
            '报告', '通知', '宣布', '说', '讲', '介绍', '启发',
        }
        
        # Comprehensive communicative verbs
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
            '道歉', '致歉',  # v60.8: speech acts TO person
        }
        
        # 给予 action complements (DA with animate Y)
        self.JIYU_ACTION_DA = {
            '指导', '帮助', '关照', '支持', '资助', '奖励',
        }
        
        # Institutions that can receive speech acts (metonymy)
        self.INSTITUTION_Y = {
            # Government/political bodies
            '朝廷', '政府', '当局', '官方', '国会', '议会', '人大', '政协',
            # Legal institutions
            '法院', '法庭', '检察院', '公安', '警方',
            # Media organisations
            '媒体', '报馆', '报社', '电视台', '记者', '新闻界',
            # Organisations/enterprises
            '公司', '企业', '单位', '机构', '组织', '委员会', '协会',
            '学校', '医院', '银行', '工厂', '部门',
            # Abstract collectives (addressable via metonymy)
            '世界', '社会', '公众', '外界', '舆论',
        }
        
        # ================================================================
        # SI (Scoped-Intervention) LEXICONS
        # ================================================================
        
        # Institutional intervention verbs
        self.INSTITUTIONAL_SI_VERBS = {
            '保护', '监管', '管制', '软禁', '限制', '约束',
            '审查', '审批', '批准', '核准', '许可', '授权',
            '整顿', '改革', '治理', '管控', '管辖', '督促',
            '处理', '处置', '处罚', '惩罚', '惩处',
            '制裁', '打击', '整治', '查处',
            '检查', '核查', '稽查', '督查',
            '使用', '采用', '运用', '利用',
        }
        
        # Care/help verbs (V他✓ - bounded intervention)
        self.CARE_SI_VERBS = {
            '照顾', '照料', '关照', '照看', '照应', '看护', '护理', '伺候',
            '服侍', '侍奉', '侍候', '奉养', '赡养', '抚养', '养育',
            '帮助', '援助', '救助', '扶助', '协助', '辅助',
            '保护', '维护', '捍卫', '守护', '呵护', '爱护',
            '慰问', '安慰', '劝慰', '感谢', '致谢',
            '培训', '训练', '教育', '培养',
        }
        
        # Opposition verbs
        self.OPPOSITION_SI_VERBS = {
            '反抗', '抵抗', '对抗', '抗争', '斗争', '抵制', '反对', '违抗',
            '攻击', '袭击', '进攻', '打击', '拒绝', '抗拒', '排斥',
        }
        
        # Tolerance verbs (V他✓ - bounded scope)
        self.TOLERANCE_SI_VERBS = {
            '担待', '原谅', '包容', '宽恕', '体谅', '迁就', '忍让',
            '谅解', '饶恕', '宽待', '宽宥', '容忍', '忍受', '容纳', '宽容',
        }
        
        # Policy application verbs
        self.POLICY_SI_VERBS = {
            '实行', '实施', '执行', '施行', '采用',
            '推行', '贯彻', '落实', '开展', '展开',
            '征收', '加征', '设限', '开放', '投资',
        }
        
        # Control verbs
        self.CONTROL_SI_VERBS = {
            '控制', '管', '管理', '掌控', '操控', '驾驭', '把控',
            '约束', '规范', '制约', '支配', '主宰', '左右',
            '奈何', '丢', '弃', '抛弃', '放弃',
        }
        
        # V60.8 reclassified: DISP → SI (active verbs V他✓)
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
        
        # Combined SI verbs
        self.SI_VERBS = (
            self.INSTITUTIONAL_SI_VERBS |
            self.CARE_SI_VERBS |
            self.OPPOSITION_SI_VERBS |
            self.TOLERANCE_SI_VERBS |
            self.POLICY_SI_VERBS |
            self.CONTROL_SI_VERBS |
            self.FORMER_DISP_NOW_SI_VERBS |
            {'进行', '负责', '负', '给予', '予以', '施加', '施以', '加以'}
        )
        
        # ================================================================
        # MS (Mental-State) LEXICONS
        # ================================================================
        
        # Feeling markers (always MS)
        self.FEELING_MARKERS = {'感到', '觉得', '感觉', '深感', '倍感', '感'}
        
        # Emotional response verbs (Y triggers emotion in X)
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
        
        # Cognitive STATE verbs (Y triggers knowledge in X)
        self.COGNITIVE_STATE_MS_VERBS = {
            # Core knowledge states
            '了解', '理解', '认识', '熟悉', '知道', '知晓', '明白', '懂', '懂得',
            '掌握', '把握', '洞悉', '洞察', '通晓', '深知', '获悉', '悉知',
            # Memory states
            '记得', '记住', '忆起', '想起', '回忆', '回想', '追忆',
            # Complete knowledge idioms
            '一无所知', '略知', '略知一二', '心知肚明', '了若指掌',
            # Internal deliberation (no output)
            '考虑', '估计', '琢磨', '思量', '思考', '斟酌',
        }
        
        # Conscious engagement verbs (Y triggers attention)
        self.CONSCIOUS_ENGAGEMENT_MS_VERBS = {
            '重视', '注意', '关注', '留意', '在意', '在乎', '介意',
            '忽视', '无视', '漠视',
        }
        
        # Internal psychological verbs
        self.INTERNAL_PSYCH_MS_VERBS = {
            '尊重', '尊敬', '敬重', '不敬', '敬畏', '尊崇', '崇敬', '崇尚',
            '器重', '看重', '重视', '珍视', '珍重', '青睐', '眷顾', '垂青',
            '关心', '关怀', '关切', '挂心', '怜悯', '同情', '慈悲', '悲悯',
            '信任', '信赖', '依赖', '倚重', '蔑视', '鄙视', '轻视', '藐视',
            '不屑', '瞧不起', '看不起', '冷落', '疏远', '疏忽', '赞赏', '欣赏',
        }
        
        # Loyalty verbs
        self.LOYALTY_MS_VERBS = {
            '忠', '忠诚', '忠心', '忠实', '忠贞', '效忠', '尽忠', '赤胆忠心', '忠心耿耿',
        }
        
        # V60.8 reclassified: DISP → MS (internal states)
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
            '疼爱',  # Emotional love
            '敬',  # Internal respect
            '敬爱',  # Internal respect
            '吝于',  # Internal reluctance
        }
        
        # Emotional states
        self.EMOTIONAL_STATES_MS = {
            '屈服', '迷惑',
            '好感', '感情', '保留',
            '持态度', '抱着', '怀揣', '期盼', '狂热', '死心',
            '生闷气', '戒备', '防备', '警惕', '放松警惕',
            '弄懂', '没概念',
            '注重', '用心', '有意向',
        }
        
        # Cognitive state idioms (MS)
        self.COGNITIVE_STATE_IDIOMS_MS = {
            '了如指掌',  # Training: MS=14, ABT=5
            '心知肚明',  # Training: MS=2
            '心中有数',  # state of understanding
        }
        
        # Emotional avoidance idioms (MS)
        self.EMOTIONAL_AVOIDANCE_MS = {
            '讳莫如深',  # emotional avoidance
        }
        
        # Combined MS verbs
        self.MS_VERBS = (
            self.EMOTIONAL_RESPONSE_VERBS |
            self.COGNITIVE_STATE_MS_VERBS |
            self.CONSCIOUS_ENGAGEMENT_MS_VERBS |
            self.INTERNAL_PSYCH_MS_VERBS |
            self.LOYALTY_MS_VERBS |
            self.FORMER_DISP_NOW_MS_VERBS |
            {'充满', '充斥', '弥漫', '印象', '有印象', '感兴趣', '有兴趣'}
        )
        
        # ================================================================
        # ABT (Aboutness) LEXICONS
        # ================================================================
        
        # Cognitive ACTIVITY verbs (produce output)
        self.COGNITIVE_ABT_VERBS = {
            '判断', '推测', '预测', '预料', '预期', '预见', '猜测',
        }
        
        # Discourse verbs
        self.DISCOURSE_ABT_VERBS = {
            # Research/study
            '研究', '调查', '考察', '探讨', '分析', '调研', '考证',
            # Evaluation
            '评价', '评论', '评述', '评判', '唱评', '点评',
            '评估', '评定', '评分', '评级',
            # Discussion
            '讨论', '辩论', '争论', '争议', '议论', '商议', '商讨',
            # Reporting
            '报道', '陈述', '叙述', '阐述', '论述',
            '置评', '发言', '表态', '发表意见', '发表看法',
        }
        
        # Stance verbs
        self.STANCE_ABT_VERBS = {
            '负有', '负有责任', '承担责任', '担负', '肩负', '背负',
            '适用', '适用于', '针对', '面向', '涉及',
        }
        
        # ABT idioms
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
        
        # 提出 discourse complements
        self.TICHU_DISCOURSE_ABT = {
            '建议', '方案', '批评', '抗议', '意见',
            '看法', '观点', '主张', '提案', '议案', '质疑',
        }
        
        # 作出 discourse complements
        self.ZUOCHU_DISCOURSE_ABT = {
            # Judgement/evaluation outputs
            '预报', '决定', '定位', '再现', '判断',
            '评价', '解释', '说明', '分析', '结论', '诊断',
            # Expanded discourse outputs
            '回应', '回答', '答复', '表态', '表示', '声明', '阐述',
            '预测', '预言', '推测', '估计', '推断', '论断', '判定',
            '总结', '概括', '归纳', '描述', '叙述', '陈述',
            '评论', '评估', '鉴定', '认定', '裁定',
            '反应', '反馈', '响应',  # response outputs
        }
        
        # 给予 discourse complements
        self.JIYU_DISCOURSE_ABT = {
            '肯定', '评价', '关注', '重视', '高度评价', '充分肯定', '好评', '高度',
        }
        
        # 不予 patterns
        self.BUYU_ABT_PATTERNS = {
            '理睬', '理会', '置评', '评论', '回应',
        }
        
        # Combined ABT verbs
        self.ABT_VERBS = (
            self.COGNITIVE_ABT_VERBS |
            self.DISCOURSE_ABT_VERBS |
            self.STANCE_ABT_VERBS
        )
        
        # ================================================================
        # DISP (Disposition) LEXICONS
        # ================================================================
        
        # Pure manner predicates (stative)
        self.PURE_MANNER_DISP_VERBS = {
            '热情', '冷淡', '冷漠', '热心', '客气', '礼貌', '有礼貌', '没礼貌',
            '温柔', '柔和', '和蔼', '亲切', '慈祥',
            '粗暴', '粗鲁', '蛮横', '野蛮', '霸道',
            '体贴', '细心', '周到', '殷勤',
            '严厉', '苛刻', '严苛', '严酷', '刻薄',
            '真诚', '诚恳', '虔诚', '直率', '坦白', '坦率',
            '公道', '厚道', '地道',
            '不理不睬', '言听计从', '唯命是从', '百依百顺',
            '呼来唤去', '说打就打', '颐指气使', '克尽妇道',
            '恭敬', '恭顺', '毕恭毕敬', '孝顺', '顺从', '服从',
            '敷衍', '漠视', '无视', '忽视',
            '松', '紧', '严', '宽', '软', '硬',
            # V69 manner idioms
            '恩爱', '专情', '真心', '袒护', '袒护', '严肃',
        }
        
        # Treatment verbs (stative manner)
        self.TREATMENT_VERBS = {
            '待', '对待', '善待', '厚待', '薄待', '优待', '虐待', '款待', '招待',
            '相待', '看待', '接待', '应付', '应对',
        }
        
        # Simile verbs
        self.SIMILE_VERBS = {
            '像', '象', '如', '如同', '宛如', '犹如', '好像', '好似', '仿佛',
            '类似', '相似', '相像', '近似', '形似', '神似',
            '酷似', '酷肖', '活像', '活似',
        }
        
        # Manner expressions
        self.MANNER_EXPRESSIONS_DISP = {
            '一样', '不苟言笑', '真心实意', '惺惺相惜', '刮目相视',
            '视而不见', '视若无睹', '不予理睬', '不予理会',
        }
        
        # Combined DISP predicates
        self.DISP_PREDICATES = (
            self.PURE_MANNER_DISP_VERBS |
            self.SIMILE_VERBS |
            {'好', '不好', '坏', '友好', '不友好', '友善', '善意', '恶意',
             '认真', '不认真', '宽容', '宽厚',
             '客气', '不客气', '耐心', '没耐心', '温和', '凶'}
        )
        
        # ================================================================
        # EVAL (Evaluation) LEXICONS
        # ================================================================
        
        # Basic evaluative predicates
        self.EVAL_PREDICATES = {
            '灵', '不灵', '有效', '无效', '有用', '无用', '管用', '好使',
            '重要', '必要', '关键', '至关重要',
            '有利', '有害', '有益', '有意义',
            '适用', '实用', '中用', '顶用', '可行', '不行', '适合', '合适',
            '微不足道',
        }
        
        # Fairness predicates
        self.FAIRNESS_EVAL_PREDICATES = {
            '公平', '公正', '平等', '不公', '不公平', '不公正', '一视同仁',
        }
        
        # Effect verbs
        self.EFFECT_VERBS = {
            '造成', '导致', '引起', '带来', '促进', '阻碍', '构成', '影响', '触动', '刺激',
        }
        
        # 具有 significance complements (EVAL)
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
        # 有 (HAVE) PATTERN LEXICONS
        # ================================================================
        
        # 有 + EVAL complements
        self.YOU_EVAL_COMPS = {
            # Effect/impact
            '影响', '作用', '效果', '效应', '意义', '价值', '贡献',
            '好处', '益处', '害处', '坏处', '危害', '损害', '利', '弊',
            '用', '用处', '用途', '帮助', '启发', '启示', '借鉴',
            # Significance
            '吸引力', '说服力', '感染力', '约束力', '执行力',
            '可能', '前途', '前景', '出路', '市场',
            # Pressure/support
            '压力', '支撑', '冲击', '威胁',
            # Obligation FOR Y
            '义务',
            # V69: Benefit patterns
            '恩', '恩德', '恩惠', '大恩', '恩情', '功劳', '功德',
            '救命之恩', '救命大恩', '养育之恩',
        }
        
        # 有 + SI complements
        self.YOU_SI_COMPS = {
            # Institutional control
            '管辖权', '控制权', '所有权', '主权', '决定权', '否决权',
            '监护权', '处分权', '裁判权', '管理权', '支配权',
            # Regulations/constraints
            '规范', '限制', '约束', '制约', '束缚',
            # Administrative actions
            '反馈', '安排', '部署', '处理', '调整',
            # Resistance
            '抗性', '耐药性', '抵抗力', '免疫力',
            # Targets/goals
            '目标', '指标',
        }
        
        # 有 + DA complements
        self.YOU_DA_COMPS = {
            '交代', '暗示', '指示', '嘱咐', '婉告',
            '答复', '回复', '回应',
            '建议', '指导', '批评', '表扬',
        }
        
        # 有 + DISP complements
        self.YOU_DISP_COMPS = {
            '距离', '隔阂', '隔膜',  # interpersonal distance
            '礼貌', '礼', '耐心', '耐性', '诚意', '敬意', '善意', '恶意',
            '笑意', '笑容', '好脸色',
            '义气', '情义', '恩情',  # interpersonal manner
        }
        
        # 有 + ABT complements
        self.YOU_ABT_COMPS = {
            # Knowledge production
            '研究', '心得', '体验', '发现', '认知',
            # Analysis/evaluation
            '评价', '分析', '判断', '论述', '总结', '描述',
            # Method/approach
            '招', '招数', '手段', '对策', '措施',
            # Institutional discourse
            '规定', '规则', '定论',
            # Critique
            '微词', '批判', '揭露',
        }
        
        # 有 + MS complements (comprehensive)
        self.YOU_MS_COMPS = {
            # Opinion/view
            '看法', '观点', '见解', '高见', '见地', '主张', '意见',
            # Cognitive states
            '了解', '认识', '理解', '印象', '记忆', '概念', '把握',
            '成见', '偏见',
            # Internal ability
            '办法', '方法', '能力', '天分', '才能',
            # Emotional states
            '好感', '恶感', '反感', '厌恶', '敌意', '戒心', '戒备',
            '好奇', '好奇心', '兴趣', '热情', '激情', '感情', '深情',
            '信心', '信任', '信赖', '依赖', '依恋', '眷恋', '留恋',
            '同情', '同情心', '怜悯', '慈悲',
            '期待', '期望', '期盼', '向往', '憧憬', '幻想', '希望',
            '怀疑', '疑虑', '疑惧', '顾虑', '担忧', '担心',
            '不满', '怨言', '怨气', '异议',
            # Feeling/sensation
            '感觉', '感受', '感触', '体会', '反应',
            # Internal planning
            '想法', '念头', '打算', '意向', '意愿', '企图', '野心',
            '准备',
            # Heart-related states
            '心思', '心意', '心理', '心态',
            '虚荣心', '进取心', '上进心', '责任心', '事业心',
            # Evaluative states
            '讲究', '追求',
            # V69: Additional MS nouns
            '索求', '抗拒', '抗拒力', '防范', '防范之心', '疑义',
            '盘算', '要求', '注意', '罪恶感', '事业心', '义务',
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
        
        # 有所 + selection → ABT
        self.YOUSUO_ABT_COMPS = {
            '选择', '侧重', '偏重', '取舍',
        }
        
        # ================================================================
        # ANIMACY DETECTION
        # ================================================================
        
        self.ANIMATE_MARKERS = {
            '我', '你', '他', '她', '您', '咱', '它', '我们', '你们', '他们', '她们', '咱们',
            '自己', '本人', '人家', '别人', '大家', '各位', '谁', '某人', '有人', '对方',
            '人', '人们', '学生', '老师', '医生', '患者', '观众', '读者', '孩子',
            '父母', '朋友', '同事', '客人', '员工', '领导', '群众', '民众', '百姓',
            '父亲', '母亲', '儿子', '女儿', '妻子', '丈夫', '哥哥', '姐姐',
        }
        
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
        
        self.INANIMATE_MARKERS = {
            '事', '事情', '问题', '情况', '现象', '结果',
            '政策', '制度', '措施', '方法', '做法', '方案', '计划',
            '工作', '任务', '项目', '活动', '行动',
            '社会', '国家', '市场', '经济', '发展', '生活', '婚姻', '利率', '反应',
        }
        
        # Clear inanimate markers for 说 verb logic
        self.CLEAR_INANIMATE_MARKERS = {
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
    
    def classify(self, concordance: str, predicate: str, pred_comp: str,
                 y_phrase: str, y_anim: str) -> Tuple[str, float, str]:
        """
        Classify a 对-construction instance using v70 rules.
        
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
        y_is_institution = y_phrase in self.INSTITUTION_Y
        
        # ================================================================
        # PRIORITY 0: V60.8 Reclassifications
        # ================================================================
        
        # Former DISP → MS idioms (internal states)
        for idiom in self.FORMER_DISP_NOW_MS_IDIOMS:
            if idiom in pred_comp or predicate == idiom:
                return ('MS', 0.92, f'{idiom} = internal disregard state (v60.8)')
        
        # Former DISP → MS verbs
        if predicate in self.FORMER_DISP_NOW_MS_VERBS:
            return ('MS', 0.90, f'{predicate} = internal state (v60.8)')
        
        # Former DISP → SI verbs (active verbs V他✓)
        if predicate in self.FORMER_DISP_NOW_SI_VERBS:
            if predicate == '摆':
                if '架子' in pred_comp or '姿态' in pred_comp:
                    return ('DISP', 0.85, '摆架子/姿态 = manner expression (v60.8)')
            return ('SI', 0.90, f'{predicate} = active intervention V他✓ (v60.8)')
        
        # ================================================================
        # PRIORITY 1: Speech 道 verbs → DA
        # ================================================================
        if predicate in self.SPEECH_DAO_VERBS:
            return ('DA', 0.95, f'{predicate} = speech/narration TO Y')
        
        # Inherent addressee verbs → DA
        if predicate in self.INHERENT_ADDRESSEE_VERBS:
            return ('DA', 0.95, f'{predicate} = inherent addressee verb TO')
        
        # ================================================================
        # PRIORITY 2: Feeling markers → MS
        # ================================================================
        if predicate in self.FEELING_MARKERS:
            return ('MS', 0.92, f'{predicate} = affective response marker')
        
        # ================================================================
        # PRIORITY 3: 进行 → always SI (v60.9 critical fix)
        # ================================================================
        if predicate == '进行':
            return ('SI', 0.94, '进行 = procedural intervention ON scope (v70)')
        
        # ================================================================
        # PRIORITY 4: Predicate-priority discourse verbs (ABT regardless of complement)
        # ================================================================
        discourse_priority = {
            '采访': ('ABT', 0.91, '采访 = interview/investigate ABOUT'),
            '调查': ('ABT', 0.91, '调查 = investigate ABOUT'),
            '研究': ('ABT', 0.90, '研究 = research ABOUT'),
            '分析': ('ABT', 0.90, '分析 = analyse ABOUT'),
            '探讨': ('ABT', 0.90, '探讨 = discuss ABOUT'),
            '讨论': ('ABT', 0.90, '讨论 = discuss ABOUT'),
        }
        if predicate in discourse_priority:
            return discourse_priority[predicate]
        
        # ================================================================
        # PRIORITY 5: 具有 patterns
        # ================================================================
        if predicate == '具有':
            # EVAL: significance/effect
            for sig in self.JUYOU_SIGNIFICANCE_EVAL:
                if sig in pred_comp:
                    return ('EVAL', 0.94, f'具有+{sig} = significance FOR Y (v60.2)')
            # Check concordance for significance
            significance_in_conc = ['意义', '作用', '价值', '影响', '效果', '吸引力', '指导']
            for sig in significance_in_conc:
                if sig in concordance:
                    return ('EVAL', 0.92, f'具有+{sig}(in conc) = significance FOR Y')
            # SI: control/rights
            si_rights = ['控制权', '管辖权', '所有权', '支配权', '决定权', '否决权', '监护权']
            for sr in si_rights:
                if sr in pred_comp or sr in concordance:
                    return ('SI', 0.92, f'具有+{sr} = bounded authority OVER Y')
            # MS: psychological state
            psych_states = ['经验', '感情', '感', '同感', '责任感', '事业心', '信心', '热情', '兴趣', '好感']
            for ps in psych_states:
                if ps in pred_comp or ps in concordance:
                    return ('MS', 0.90, f'具有+{ps} = psychological state')
            # Default: ABT
            return ('ABT', 0.80, '具有 = possession REGARDING')
        
        # ================================================================
        # PRIORITY 6: 表示 patterns (v70 fix: check internal emotions FIRST)
        # ================================================================
        if predicate == '表示':
            # Check for INTERNAL emotions first
            internal_emotions = {
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
            for emotion in internal_emotions:
                if emotion in pred_comp:
                    # Exception: speech_to_person is DA
                    speech_to_markers = ['祝贺', '感谢', '慰问', '欢迎', '致谢', '谢意', '问候', '致敬']
                    is_speech_to = any(m in pred_comp for m in speech_to_markers) and y_is_animate
                    if not is_speech_to:
                        return ('MS', 0.92, f'表示+{emotion} = internal emotion (v70)')
            
            # Animacy-based logic for non-internal expressions
            if y_is_animate or y_is_institution:
                return ('DA', 0.85, '表示 + animate Y = express TO recipient')
            else:
                return ('ABT', 0.85, '表示 + inanimate Y = express ABOUT topic')
        
        # ================================================================
        # PRIORITY 7: 提出 patterns
        # ================================================================
        if predicate == '提出':
            # Legal action patterns → SI
            legal_markers = ['抗诉', '起诉', '诉讼', '控告', '申诉', '上诉',
                            '处罚', '惩罚', '警告', '抗议']
            if any(m in pred_comp for m in legal_markers):
                return ('SI', 0.92, '提出+legal action ON')
            # 异议 → ABT
            if '异议' in pred_comp or '异议' in concordance:
                return ('ABT', 0.92, '提出+异议 = raise objection ABOUT Y')
            # 要求 patterns
            if '要求' in pred_comp or '要求' in concordance:
                if y_is_animate:
                    return ('SI', 0.90, '提出+要求+anim Y = impose requirements ON')
                else:
                    return ('ABT', 0.88, '提出+要求+inan Y = discourse ABOUT')
            # Discourse complements
            for dc in self.TICHU_DISCOURSE_ABT:
                if dc in pred_comp:
                    return ('ABT', 0.90, f'提出+{dc} = put forward discourse ABOUT')
            if y_is_animate:
                return ('DA', 0.88, '提出+anim Y = speech TO')
            return ('ABT', 0.88, '提出 = put forward discourse ABOUT Y')
        
        # ================================================================
        # PRIORITY 8: 作出/做出 patterns
        # ================================================================
        if predicate in ['作出', '做出']:
            # 贡献 → EVAL
            if '贡献' in pred_comp or '贡献' in concordance:
                return ('EVAL', 0.92, f'{predicate}+贡献 = contribution FOR Y')
            # Speech/gesture with animate Y → DA
            speech_gesture_comps = {'表示', '回应', '回答', '答复'}
            if y_is_animate or y_is_institution:
                for sgc in speech_gesture_comps:
                    if sgc in pred_comp:
                        return ('DA', 0.90, f'{predicate}+{sgc}+recipient = gesture TO')
            # Action response → SI
            action_response_markers = {'应急', '联动', '处置', '紧急', '快速', '及时', '协同'}
            if '反应' in pred_comp or '响应' in pred_comp:
                if any(m in pred_comp for m in action_response_markers):
                    return ('SI', 0.92, f'{predicate}+action response = intervention ON')
            # Discourse complements
            for dc in self.ZUOCHU_DISCOURSE_ABT:
                if dc in pred_comp:
                    return ('ABT', 0.90, f'{predicate}+{dc} = produce discourse ABOUT')
            # Intervention complements
            intervention_comps = [
                '处理', '规定', '处罚', '部署', '判决', '调整',
                '约定', '规划', '补充', '安排', '承诺', '保证', '让步',
                '牺牲', '努力', '准备',
                '拘留', '宣告', '反击', '反弹', '赔偿', '裁决',
                '处置', '批示', '指示', '调解', '仲裁', '惩罚', '惩处',
            ]
            for ic in intervention_comps:
                if ic in pred_comp or ic in concordance:
                    return ('SI', 0.90, f'{predicate}+{ic} = intervention ON')
            return ('ABT', 0.80, f'{predicate} = produce discourse ABOUT Y')
        
        # ================================================================
        # PRIORITY 9: 给予/予以 patterns
        # ================================================================
        if predicate in ['给予', '予以']:
            # Mental objects → MS
            if predicate == '给予':
                mental_objects = {'厚望', '期望', '希望', '信任', '支持', '关注', '重视'}
                for obj in mental_objects:
                    if obj in pred_comp:
                        return ('MS', 0.88, f'给予+{obj} = internal expectation (v70)')
            # Discourse complements → ABT
            for dc in self.JIYU_DISCOURSE_ABT:
                if dc in pred_comp:
                    return ('ABT', 0.90, f'{predicate}+{dc} = give evaluation ABOUT')
            # Action with animate Y → DA
            if y_is_animate:
                for da in self.JIYU_ACTION_DA:
                    if da in pred_comp:
                        return ('DA', 0.90, f'{predicate}+{da}+anim = give TO')
            return ('SI', 0.85, f'{predicate} = intervention ON')
        
        # ================================================================
        # PRIORITY 10: 不予 patterns
        # ================================================================
        if predicate == '不予' or '不予' in pred_comp:
            for pattern in self.BUYU_ABT_PATTERNS:
                if pattern in pred_comp:
                    return ('ABT', 0.90, f'不予+{pattern} = refuse to engage ABOUT')
            return ('SI', 0.85, '不予 = refusal ON scope')
        
        # ================================================================
        # PRIORITY 11: 施以 → always SI
        # ================================================================
        if predicate == '施以':
            return ('SI', 0.92, '施以 = inflict/apply ON Y (v60.8)')
        
        # ================================================================
        # PRIORITY 12: 负责 patterns
        # ================================================================
        if predicate == '负责' or '负责' in pred_comp:
            # Casual degree adverbs → DISP (manner)
            casual_advs = ['很', '挺', '蛮', '太', '非常', '特别', '十分', '比较', '相当']
            for adv in casual_advs:
                if adv + '负责' in concordance:
                    return ('DISP', 0.88, f'{adv}+负责 = responsible manner')
            # Default: SI (accountability)
            return ('SI', 0.94, '负责 = accountability ON scope (v60.8)')
        
        # ================================================================
        # PRIORITY 13: EVAL predicates
        # ================================================================
        if predicate in self.EVAL_PREDICATES:
            return ('EVAL', 0.90, f'{predicate} = evaluative FOR Y')
        
        if predicate in self.FAIRNESS_EVAL_PREDICATES:
            return ('EVAL', 0.92, f'{predicate} = fairness evaluation FOR')
        
        if predicate in self.EFFECT_VERBS:
            return ('EVAL', 0.94, f'{predicate} = effect ON')
        
        # ================================================================
        # PRIORITY 14: 有 patterns (comprehensive)
        # ================================================================
        if predicate in ['有', '没有', '没', '有着', '有所', '持有', '抱有', '怀有',
                         '应有', '保有', '具有', '拥有', '享有', '富有']:
            
            # 有所 patterns
            if '有所' in pred_comp or predicate == '有所':
                for comp in self.YOUSUO_SI_COMPS:
                    if comp in pred_comp:
                        return ('SI', 0.90, f'有所+{comp} = bounded action ON')
                for comp in self.YOUSUO_MS_COMPS:
                    if comp in pred_comp:
                        return ('MS', 0.90, f'有所+{comp} = cognitive state')
                for comp in self.YOUSUO_ABT_COMPS:
                    if comp in pred_comp:
                        return ('ABT', 0.88, f'有所+{comp} = selective attitude ABOUT')
            
            # Check complements in order of specificity
            for comp in self.YOU_EVAL_COMPS:
                if comp in pred_comp:
                    return ('EVAL', 0.92, f'有+{comp} = effect/benefit FOR Y')
            
            for comp in self.YOU_SI_COMPS:
                if comp in pred_comp:
                    return ('SI', 0.90, f'有+{comp} = bounded control ON Y')
            
            for comp in self.YOU_DA_COMPS:
                if comp in pred_comp and y_is_animate:
                    return ('DA', 0.88, f'有+{comp} = speech result TO Y')
            
            for comp in self.YOU_DISP_COMPS:
                if comp in pred_comp and y_is_animate:
                    return ('DISP', 0.88, f'有+{comp} = manner toward Y')
            
            for comp in self.YOU_ABT_COMPS:
                if comp in pred_comp:
                    return ('ABT', 0.88, f'有+{comp} = discourse ABOUT Y')
            
            for comp in self.YOU_MS_COMPS:
                if comp in pred_comp:
                    return ('MS', 0.90, f'有+{comp} = psychological state')
            
            # Default 有
            return ('MS', 0.75, '有 = having state (default)')
        
        # ================================================================
        # PRIORITY 15: 寄予/寄托 → MS
        # ================================================================
        if predicate in ['寄予', '寄托']:
            return ('MS', 0.93, f'{predicate} = project hope/expectation (v69)')
        
        # ================================================================
        # PRIORITY 16: MS verbs
        # ================================================================
        if predicate in self.MS_VERBS:
            return ('MS', 0.90, f'{predicate} = psychological state triggered by Y')
        
        # Emotional states
        for pattern in self.EMOTIONAL_STATES_MS:
            if pattern in pred_comp or predicate == pattern:
                return ('MS', 0.90, f'{pattern} = emotional state')
        
        # Cognitive state idioms
        for idiom in self.COGNITIVE_STATE_IDIOMS_MS:
            if idiom in pred_comp or predicate == idiom:
                return ('MS', 0.92, f'{idiom} = cognitive STATE')
        
        # Emotional avoidance
        for idiom in self.EMOTIONAL_AVOIDANCE_MS:
            if idiom in pred_comp or predicate == idiom:
                return ('MS', 0.90, f'{idiom} = emotional avoidance')
        
        # ABT idioms
        for idiom in self.ABT_IDIOMS:
            if idiom in pred_comp or predicate == idiom:
                return ('ABT', 0.94, f'{idiom} = cognitive stance ABOUT')
        
        # ================================================================
        # PRIORITY 17: ABT verbs
        # ================================================================
        if predicate in self.ABT_VERBS:
            return ('ABT', 0.90, f'{predicate} = discourse ABOUT Y')
        
        # ================================================================
        # PRIORITY 18: SI verbs
        # ================================================================
        if predicate in self.SI_VERBS:
            return ('SI', 0.90, f'{predicate} = intervention ON Y')
        
        # ================================================================
        # PRIORITY 19: Simile verbs → DISP
        # ================================================================
        if predicate in self.SIMILE_VERBS:
            return ('DISP', 0.96, f'{predicate} = simile manner')
        
        # ================================================================
        # PRIORITY 20: 引起+psychological response → MS
        # ================================================================
        if predicate == '引起':
            psych_responses = {'重视', '关注', '注意', '警惕', '警觉', '兴趣', '好奇'}
            for resp in psych_responses:
                if resp in pred_comp or resp in concordance:
                    return ('MS', 0.90, f'引起+{resp} = trigger psychological response')
            return ('EVAL', 0.90, '引起 = effect ON')
        
        # ================================================================
        # PRIORITY 21: DISP predicates (with animate Y)
        # ================================================================
        if predicate in self.DISP_PREDICATES and y_is_animate:
            return ('DISP', 0.94, f'{predicate} = external manner toward Y')
        
        # Manner expressions
        for pattern in self.MANNER_EXPRESSIONS_DISP:
            if pattern in pred_comp or predicate == pattern:
                return ('DISP', 0.90, f'{pattern} = manner expression')
        
        # ================================================================
        # PRIORITY 22: 说 verb - reversed logic (v70 critical fix)
        # ================================================================
        if predicate in {'说', '讲', '喊', '叫', '问', '答', '骂', '嚷', '嘟'}:
            # Check if Y is CLEARLY inanimate
            is_clearly_inanimate = any(m in y_phrase for m in self.CLEAR_INANIMATE_MARKERS)
            
            # Topic indicators in concordance
            topic_indicators = ['关于', '有关', '涉及', '针对', '就']
            has_topic_indicator = any(ind in concordance for ind in topic_indicators)
            
            if is_clearly_inanimate or has_topic_indicator:
                return ('ABT', 0.92, f'{predicate} = discourse ABOUT topic (v70)')
            else:
                # Default: DA (speak TO recipient) - catches names/people
                return ('DA', 0.94, f'{predicate} = speech TO recipient (v70 default)')
        
        # ================================================================
        # PRIORITY 23: 抱怨 patterns
        # ================================================================
        if predicate == '抱怨':
            if y_is_animate or y_is_institution:
                return ('DA', 0.90, '抱怨 = complain TO recipient')
            else:
                return ('ABT', 0.80, '抱怨 = complain ABOUT inanimate Y')
        
        # ================================================================
        # PRIORITY 24: Gesture verbs
        # ================================================================
        if predicate in self.GESTURE_DA_VERBS and y_is_animate:
            return ('DA', 0.92, f'{predicate} = gesture TO animate Y')
        
        # ================================================================
        # PRIORITY 25: 反映 patterns
        # ================================================================
        if predicate == '反映':
            quality_words = ['不错', '很大', '较大', '很好', '很差', '强烈', '不好', '一般']
            for qw in quality_words:
                if qw in pred_comp:
                    return ('ABT', 0.90, '反映+quality = feedback ABOUT')
            if y_is_animate or y_is_institution:
                return ('DA', 0.85, '反映 = report TO recipient')
            else:
                return ('ABT', 0.85, '反映 = reflect ABOUT topic')
        
        # ================================================================
        # PRIORITY 26: Communicative verbs
        # ================================================================
        if predicate in self.COMMUNICATIVE_VERBS:
            if y_is_animate or y_is_institution:
                return ('DA', 0.90, f'{predicate} = speech TO recipient')
            else:
                return ('ABT', 0.85, f'{predicate} = discourse ABOUT inanimate Y')
        
        # ================================================================
        # PRIORITY 27: 是 patterns
        # ================================================================
        if predicate == '是':
            # ABT 的 patterns
            abt_de = {'了解的', '熟悉的', '清楚的', '知道的', '明白的', '理解的',
                      '熟知的', '深知的', '认识的', '懂的', '懂得的',
                      '确定的', '肯定的', '相信的', '怀疑的', '负责的', '负责任的'}
            for comp in abt_de:
                if comp in pred_comp:
                    return ('ABT', 0.90, f'是+{comp} = cognitive aboutness')
            
            # DISP 的 patterns
            disp_de = {'真心的', '真诚的', '诚心的', '诚恳的', '诚实的',
                       '友好的', '友善的', '善意的', '热心的', '热情的',
                       '冷淡的', '冷漠的', '无情的', '残忍的', '残酷的',
                       '公平的', '公正的', '公开的', '虔诚的', '坦白的',
                       '认真的', '严肃的', '严格的', '宽容的', '宽厚的',
                       '忠诚的', '忠心的', '忠实的'}
            for comp in disp_de:
                if comp in pred_comp:
                    return ('DISP', 0.93, f'是+{comp} = manner toward Y')
            
            # EVAL nouns
            eval_nouns = {'干扰', '打扰', '骚扰', '例外', '特例', '特殊',
                          '威胁', '危险', '危害', '隐患', '挑战', '考验', '难题',
                          '负担', '累赘', '包袱', '损失', '损害', '伤害',
                          '帮助', '好处', '益处', '利益', '安慰', '鼓励', '支持',
                          '打击', '刺激', '冲击', '侮辱', '羞辱', '耻辱'}
            for noun in eval_nouns:
                if noun in pred_comp:
                    return ('EVAL', 0.88, f'是+{noun} = X is {noun} FOR Y')
        
        # ================================================================
        # PRIORITY 28: 作/做 patterns
        # ================================================================
        if predicate in ['作', '做']:
            discourse_comp = {'分析', '研究', '探讨', '考察', '调查', '评估', '评价',
                              '介绍', '鉴定', '结论', '诊断', '裁判'}
            for dc in discourse_comp:
                if dc in pred_comp:
                    return ('ABT', 0.90, f'{predicate}+{dc} = discourse ABOUT')
            
            intervention_comp = {'处理', '决定', '判决', '处罚', '裁决', '安排'}
            for ic in intervention_comp:
                if ic in pred_comp:
                    return ('SI', 0.88, f'{predicate}+{ic} = intervention ON')
        
        if '作出' in pred_comp or '做出' in pred_comp:
            if '贡献' in pred_comp:
                return ('SI', 0.90, '作出贡献 = contribution affecting Y')
        
        # ================================================================
        # FALLBACK: Based on Y animacy and predicate characters
        # ================================================================
        if y_is_animate:
            # Manner characters
            manner_chars = set('冷热亲疏远近松紧严宽软硬')
            if any(c in predicate for c in manner_chars):
                return ('DISP', 0.70, 'manner char + animate Y → DISP')
            # Emotion characters
            emotion_chars = set('爱恨怕惧怒喜悲哀忧愁烦厌羡慕嫉')
            if any(c in predicate for c in emotion_chars):
                return ('MS', 0.70, 'emotion char + animate Y → MS')
            # Default for animate Y
            return ('DA', 0.60, 'animate Y default → DA')
        else:
            # Cognitive characters
            cog_chars = set('想思考虑知道认识了解明白懂悟解析研究')
            if any(c in predicate for c in cog_chars):
                return ('ABT', 0.70, 'cognitive char + inanimate Y → ABT')
            # Effect characters
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
        
        # Check explicit animate markers
        for marker in self.ANIMATE_MARKERS:
            if marker in y_phrase:
                return True
        
        # Check explicit inanimate markers
        for marker in self.INANIMATE_MARKERS:
            if marker in y_phrase:
                return False
        
        # Check for Chinese name patterns
        if y_phrase and len(y_phrase) >= 2 and len(y_phrase) <= 4:
            # Starts with common surname
            if y_phrase[0] in self.COMMON_SURNAMES:
                return True
            
            # Contains title markers
            title_markers = ['先生', '女士', '小姐', '老师', '主任', '经理',
                           '厂长', '校长', '院长', '部长', '总统', '总理', '书记']
            if any(marker in y_phrase for marker in title_markers):
                return True
            
            # Ends with plural marker 们
            if y_phrase.endswith('们'):
                base = y_phrase[:-1]
                if base in self.COMMON_SURNAMES or base in self.ANIMATE_MARKERS:
                    return True
        
        # Short phrases without inanimate markers → likely animate
        if y_phrase and len(y_phrase) <= 3:
            if not any(char in y_phrase for char in ['性', '化', '度', '率', '量']):
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
- The predicate '{predicate}' indicates a behavioural manner TOWARD Y
- Y ('{y_phrase}') is the target of X's behavioural attitude
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
