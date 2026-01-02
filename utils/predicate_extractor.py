# -*- coding: utf-8 -*-
"""
Predicate Extractor Module
===========================
Extracts Y and predicate from 对-construction sentences.
Uses LTP (Language Technology Platform) for Chinese NLP.
"""

import re
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Try to import LTP
try:
    from ltp import LTP
    LTP_AVAILABLE = True
except ImportError:
    LTP_AVAILABLE = False
    logger.warning("LTP not available. Using rule-based extraction only.")


class PredicateExtractor:
    """Extract Y phrase and predicate from 对-construction sentences."""
    
    def __init__(self, use_ltp: bool = True):
        """
        Initialize the extractor.
        
        Args:
            use_ltp: Whether to use LTP for parsing (requires ltp package)
        """
        self.use_ltp = use_ltp and LTP_AVAILABLE
        self.ltp = None
        
        if self.use_ltp:
            try:
                logger.info("Loading LTP model...")
                self.ltp = LTP("LTP/small")  # Use small model for speed
                logger.info("LTP model loaded successfully.")
            except Exception as e:
                logger.warning(f"Failed to load LTP: {e}. Using rule-based extraction.")
                self.use_ltp = False
                self.ltp = None
    
    def extract(self, sentence: str) -> Dict[str, str]:
        """
        Extract components from a 对-construction sentence.
        
        Args:
            sentence: Chinese sentence containing 对
            
        Returns:
            Dictionary with:
            - x_phrase: Subject (before 对)
            - y_phrase: Y argument (after 对, before predicate)
            - predicate: Main predicate
            - pred_comp: Predicate + complement
            - y_anim: Animacy of Y ('anim' or 'inan')
        """
        if '对' not in sentence:
            return {
                'x_phrase': '',
                'y_phrase': '',
                'predicate': '',
                'pred_comp': '',
                'y_anim': 'inan',
                'error': 'No 对 found in sentence'
            }
        
        # Try LTP-based extraction first
        if self.use_ltp and self.ltp is not None:
            try:
                result = self._extract_with_ltp(sentence)
                if result.get('predicate'):
                    return result
            except Exception as e:
                logger.warning(f"LTP extraction failed: {e}")
        
        # Fall back to rule-based extraction
        return self._extract_with_rules(sentence)
    
    def _extract_with_ltp(self, sentence: str) -> Dict[str, str]:
        """
        Extract using LTP dependency parsing.
        """
        # Segment and parse
        output = self.ltp.pipeline([sentence], tasks=["cws", "pos", "dep", "sdp"])
        
        words = output.cws[0]
        pos_tags = output.pos[0]
        dep = output.dep[0]  # Dependency parse
        
        # Find 对 position
        dui_idx = None
        for i, word in enumerate(words):
            if word == '对':
                dui_idx = i
                break
        
        if dui_idx is None:
            return self._extract_with_rules(sentence)
        
        # Find Y (usually the noun phrase immediately after 对)
        y_phrase = ''
        y_end_idx = dui_idx
        
        for i in range(dui_idx + 1, len(words)):
            # Y typically ends when we hit a verb
            if pos_tags[i].startswith('v') and i > dui_idx + 1:
                break
            # Y typically ends at punctuation
            if pos_tags[i] in ['w', 'wp', 'ws']:
                break
            y_phrase += words[i]
            y_end_idx = i
        
        # Find predicate (first verb after Y)
        predicate = ''
        pred_idx = None
        for i in range(y_end_idx + 1, len(words)):
            if pos_tags[i].startswith('v'):
                predicate = words[i]
                pred_idx = i
                break
        
        # If no verb found, try to find the first non-noun after Y
        if not predicate:
            for i in range(y_end_idx + 1, len(words)):
                if not pos_tags[i].startswith('n') and pos_tags[i] not in ['w', 'wp', 'ws']:
                    predicate = words[i]
                    pred_idx = i
                    break
        
        # Build pred_comp (predicate + everything after)
        pred_comp = ''
        if pred_idx is not None:
            for i in range(pred_idx, len(words)):
                if pos_tags[i] not in ['w', 'wp', 'ws']:
                    pred_comp += words[i]
        
        # Get X (before 对)
        x_phrase = ''.join(words[:dui_idx])
        
        # Detect Y animacy
        y_anim = self._detect_animacy(y_phrase)
        
        return {
            'x_phrase': x_phrase,
            'y_phrase': y_phrase,
            'predicate': predicate,
            'pred_comp': pred_comp,
            'y_anim': y_anim,
            'method': 'ltp'
        }
    
    def _extract_with_rules(self, sentence: str) -> Dict[str, str]:
        """
        Extract using rule-based heuristics.
        """
        result = {
            'x_phrase': '',
            'y_phrase': '',
            'predicate': '',
            'pred_comp': '',
            'y_anim': 'inan',
            'method': 'rules'
        }
        
        # Split by 对
        parts = sentence.split('对', 1)
        if len(parts) < 2:
            return result
        
        result['x_phrase'] = parts[0].strip()
        after_dui = parts[1].strip()
        
        # Pattern 1a: 对 + pronoun + 的 + noun phrase + predicate (possessive)
        # e.g., "对你的情况不太了解" → Y = "你的情况"
        # Note: Noun after 的 is typically 1-2 chars, not more (情况, 问题, 事情, etc.)
        # Use non-greedy match and place longer adverbs first
        poss_match = re.match(r'^(我|你|他|她|它|我们|你们|他们|她们|它们|自己|大家|别人|对方)(的)([\u4e00-\u9fff]{1,2})(不太|非常|特别|十分|比较|已经|正在|没有|很|更|最|太|挺|不|没)?([\u4e00-\u9fff]+.*)', after_dui)
        if poss_match:
            result['y_phrase'] = poss_match.group(1) + poss_match.group(2) + poss_match.group(3)
            rest = (poss_match.group(4) or '') + poss_match.group(5)
            result['predicate'], result['pred_comp'] = self._extract_predicate_from_rest(rest)
            result['y_anim'] = 'inan'  # The possessed thing is usually inanimate
            return result
        
        # Pattern 1b: 对 + pronoun + predicate (direct)
        pronoun_match = re.match(r'^(我|你|他|她|它|我们|你们|他们|她们|它们|自己|大家|别人|对方)(.+)', after_dui)
        if pronoun_match:
            result['y_phrase'] = pronoun_match.group(1)
            rest = pronoun_match.group(2)
            result['predicate'], result['pred_comp'] = self._extract_predicate_from_rest(rest)
            result['y_anim'] = 'anim'
            return result
        
        # Pattern 2: 对 + demonstrative + noun + predicate
        # Strategy: Find known predicate in text and work backwards to find Y boundary
        
        # Common predicates to look for (ordered by length, longest first)
        known_predicates = [
            # 4+ char
            '进行调查', '进行讨论', '进行分析', '进行研究', '发表意见', '发表看法',
            '言听计从', '视而不见', '不予置评',
            # 3 char
            '感兴趣', '有兴趣', '不满意', '很满意', '充满了',
            # 2 char (common)
            '进行', '实行', '实施', '采取', '给予', '予以', '表示', '提出', '作出', '做出',
            '感到', '产生', '造成', '具有', '带来', '形成', '构成', '充满', '怀有', '抱有',
            '满意', '不满', '了解', '熟悉', '关心', '重视', '负责',
            '有所', '毫无', '缺乏', '失去', '保持', '展开', '开展',
            '发表', '表现', '体现', '显示', '热情', '冷淡', '客气', '友好', '尊重', '信任',
            '严格', '严厉', '严肃', '宽容', '认真', '讨论', '研究', '分析', '调查',
            '喜欢', '讨厌', '害怕', '担心', '怀疑', '佩服', '崇拜', '敬佩',
            '有害', '有利', '有用', '无用', '重要', '有益', '有效',
            '说道', '笑道', '问道', '叫道', '答道',
        ]
        
        # Also check for adverb + predicate patterns (很了解, 非常满意, etc.)
        adverbs = ['很', '非常', '特别', '十分', '比较', '更', '最', '太', '挺', '不', '没', '已经', '正在']
        core_predicates = [
            '了解', '熟悉', '满意', '负责', '认真', '热情', '冷淡', '客气', '友好', 
            '尊重', '信任', '重视', '关心', '喜欢', '讨厌', '害怕', '担心', '怀疑',
            '严格', '严厉', '宽容', '敬佩', '佩服', '崇拜',
        ]
        
        # Build patterns: adv + predicate
        for adv in adverbs:
            for pred in core_predicates:
                known_predicates.append(adv + pred)
        
        # Remove duplicates and sort by length (longest first)
        known_predicates = sorted(set(known_predicates), key=len, reverse=True)
        
        # Try to find predicate in text
        for pred in known_predicates:
            idx = after_dui.find(pred)
            if idx > 0:  # Found predicate after some Y phrase
                y_phrase = after_dui[:idx].strip()
                rest = after_dui[idx:]
                
                # Validate Y is reasonable (1-8 chars, valid structure)
                if 1 <= len(y_phrase) <= 8 and self._is_valid_y(y_phrase):
                    result['y_phrase'] = y_phrase
                    result['predicate'], result['pred_comp'] = self._extract_predicate_from_rest(rest)
                    result['y_anim'] = self._detect_animacy(y_phrase)
                    return result
        
        # Pattern 2b: Demonstrative patterns (fallback)
        dem_patterns = [
            r'^(这个|那个|这些|那些)([\u4e00-\u9fff]{1,4})(很|非常|特别|十分|比较|更|最|太|挺|不|没|已经|正在)?([\u4e00-\u9fff]+.*)',
            r'^(这|那|此|该)(个|种|些|项|件|位|类)?([\u4e00-\u9fff]{1,4})(很|非常|特别|十分|比较|更|最|太|挺|不|没|已经|正在)?([\u4e00-\u9fff]+.*)',
        ]
        
        for pattern in dem_patterns:
            match = re.match(pattern, after_dui)
            if match:
                groups = match.groups()
                if len(groups) == 4:  # Pattern 1: dem + noun + adv + rest
                    result['y_phrase'] = groups[0] + groups[1]
                    rest = (groups[2] or '') + groups[3]
                elif len(groups) == 5:  # Pattern 2: dem + classifier + noun + adv + rest
                    result['y_phrase'] = groups[0] + (groups[1] or '') + groups[2]
                    rest = (groups[3] or '') + groups[4]
                else:
                    continue
                result['predicate'], result['pred_comp'] = self._extract_predicate_from_rest(rest)
                result['y_anim'] = self._detect_animacy(result['y_phrase'])
                return result
        
        # Pattern 3: 对 + 此/这/那 (single demonstrative) + predicate
        single_dem_match = re.match(r'^(此|这|那)(很|非常|特别|十分|比较|更|最|太|挺|不|没|已经|正在)?([\u4e00-\u9fff]+.*)', after_dui)
        if single_dem_match:
            result['y_phrase'] = single_dem_match.group(1)
            rest = (single_dem_match.group(2) or '') + single_dem_match.group(3)
            result['predicate'], result['pred_comp'] = self._extract_predicate_from_rest(rest)
            result['y_anim'] = 'inan'
            return result
        
        # Pattern 4: 对 + noun phrase (1-6 chars) + predicate
        # Try to find where Y ends and predicate begins
        y_phrase, rest = self._split_y_and_predicate(after_dui)
        result['y_phrase'] = y_phrase
        result['predicate'], result['pred_comp'] = self._extract_predicate_from_rest(rest)
        result['y_anim'] = self._detect_animacy(y_phrase)
        
        return result
    
    def _split_y_and_predicate(self, text: str) -> Tuple[str, str]:
        """
        Split text into Y phrase and rest (predicate + complement).
        Uses heuristics based on common predicate patterns.
        """
        # Remove adverbs that might be between Y and predicate
        adverb_markers = ['很', '非常', '特别', '十分', '比较', '更', '最', '太', '挺', 
                         '相当', '极', '极其', '格外', '不', '没', '已经', '正在']
        
        # Common predicate starters (verbs and adj that often follow Y)
        predicate_starters = [
            # Multi-char predicates (check first)
            '进行', '实行', '实施', '采取', '给予', '予以', '表示', '提出', '作出', '做出',
            '感到', '产生', '造成', '具有', '带来', '形成', '构成', '充满', '怀有', '抱有',
            '满意', '不满', '了解', '熟悉', '关心', '重视', '负责', '言听计从',
            '有所', '毫无', '缺乏', '失去', '保持', '采取', '展开', '开展',
            '发表', '表现', '体现', '显示', '感兴趣', '有兴趣',
            '热情', '冷淡', '客气', '友好', '尊重', '信任',
            '严格', '严厉', '严肃', '宽容', '认真',
            '讨论', '研究', '分析', '调查',
            # Single-char common predicates
            '说', '讲', '笑', '道', '有', '是', '作', '做', '看', '想', '问', '答',
            '好', '坏', '冷', '热', '客', '亲', '像', '如',
        ]
        
        # Also check for adverb + predicate patterns
        adverb_pred_patterns = []
        for adv in adverb_markers:
            for pred in predicate_starters:
                adverb_pred_patterns.append(adv + pred)
        
        all_patterns = adverb_pred_patterns + predicate_starters
        
        # Try to find predicate starter in text
        for pred in sorted(all_patterns, key=len, reverse=True):
            idx = text.find(pred)
            if idx > 0 and idx <= 10:  # Y should be 1-10 chars
                y = text[:idx]
                rest = text[idx:]
                # Validate Y looks reasonable
                if self._is_valid_y(y):
                    return y, rest
        
        # Try splitting by common demonstratives
        dem_match = re.match(r'^(这个|那个|此|这|那|该)(.+?)(很|非常|特别|十分|比较|更|最|太|挺|不|没|已经|正在)?(.+)', text)
        if dem_match:
            y = dem_match.group(1) + dem_match.group(2)[:2]  # Demonstrative + up to 2 chars
            rest = text[len(y):]
            if self._is_valid_y(y):
                return y, rest
        
        # Fallback: assume Y is first 2-4 characters
        for length in [2, 3, 4, 1]:
            if len(text) > length:
                y = text[:length]
                rest = text[length:]
                if self._is_valid_y(y):
                    return y, rest
        
        return text, ''
    
    def _is_valid_y(self, y: str) -> bool:
        """Check if Y looks like a valid noun phrase."""
        if not y:
            return False
        # Should not start with certain particles
        invalid_starts = ['的', '地', '得', '了', '着', '过', '也', '都', '就', '才', '又']
        if y[0] in invalid_starts:
            return False
        return True
    
    def _extract_predicate_from_rest(self, rest: str) -> Tuple[str, str]:
        """
        Extract main predicate from the rest of the sentence.
        Returns (predicate, pred_comp).
        """
        if not rest:
            return '', ''
        
        rest = rest.strip()
        pred_comp = rest  # Full predicate + complement
        
        # Remove leading adverbs/modifiers to find core predicate
        adverbs = ['很', '非常', '特别', '十分', '比较', '更', '最', '太', '挺', '相当', 
                   '极', '极其', '格外', '尤其', '不', '没', '没有', '不太', '不够', '已经',
                   '正在', '开始', '继续', '一直', '仍然', '依然', '也', '都', '就', '才']
        
        predicate_start = rest
        for adv in sorted(adverbs, key=len, reverse=True):
            if predicate_start.startswith(adv):
                predicate_start = predicate_start[len(adv):]
                break
        
        # Common multi-char predicates (check these first)
        multi_preds = [
            '进行', '实行', '实施', '采取', '给予', '予以', '表示', '提出',
            '作出', '做出', '感到', '产生', '造成', '具有', '带来', '形成',
            '构成', '充满', '怀有', '抱有', '满意', '不满', '了解', '熟悉',
            '关心', '重视', '负责', '有所', '毫无', '缺乏', '失去', '保持',
            '言听计从', '视而不见', '不予置评', '感兴趣', '有兴趣',
            '发表', '热情', '冷淡', '客气', '友好', '尊重', '信任',
            '喜欢', '讨厌', '害怕', '担心', '怀疑', '佩服',
            '有害', '有利', '有用', '无用', '重要',
            '说道', '笑道', '问道', '叫道',
        ]
        
        for pred in sorted(multi_preds, key=len, reverse=True):
            if predicate_start.startswith(pred):
                return pred, pred_comp
        
        # Single char predicate (common verbs/adjectives)
        single_preds = '说讲笑道有是作做看想问答好坏冷热客亲像如爱恨怕惧喜悲'
        if predicate_start and predicate_start[0] in single_preds:
            return predicate_start[0], pred_comp
        
        # Default: first 1-2 chars
        if len(predicate_start) >= 2:
            return predicate_start[:2], pred_comp
        elif predicate_start:
            return predicate_start[0], pred_comp
        
        return '', pred_comp
    
    def _detect_animacy(self, y_phrase: str) -> str:
        """
        Detect if Y is animate or inanimate.
        """
        if not y_phrase:
            return 'inan'
        
        # Animate markers
        animate_markers = {
            # Pronouns
            '我', '你', '他', '她', '它', '我们', '你们', '他们', '她们', '它们',
            '自己', '大家', '别人', '对方', '咱', '咱们', '某人', '有人',
            # People
            '人', '人们', '群众', '民众', '百姓', '公民', '居民', '市民',
            '男人', '女人', '男子', '女子', '男孩', '女孩', '儿童', '孩子',
            '老人', '青年', '学生', '教师', '医生', '警察', '士兵',
            # Titles/roles
            '先生', '女士', '小姐', '同志', '朋友', '家人', '亲人',
            '父亲', '母亲', '儿子', '女儿', '兄弟', '姐妹',
            '员工', '领导', '干部', '职工', '同事', '客户', '患者',
            # Collective entities (can be addressees)
            '政府', '公司', '企业', '学校', '医院', '法院', '机构',
        }
        
        for marker in animate_markers:
            if marker in y_phrase:
                return 'anim'
        
        # Common surnames (2-3 char names)
        surnames = ['李', '王', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴',
                    '徐', '孙', '马', '胡', '朱', '郭', '何', '林', '罗', '高']
        if len(y_phrase) >= 2 and len(y_phrase) <= 4:
            if y_phrase[0] in surnames:
                return 'anim'
        
        # Inanimate markers
        inanimate_markers = {
            '问题', '事情', '情况', '现象', '事件', '案件',
            '工作', '任务', '项目', '计划', '方案', '政策',
            '法律', '规定', '制度', '条例', '办法',
            '技术', '科学', '理论', '观点', '意见', '建议',
            '产品', '商品', '物品', '材料', '设备',
        }
        
        for marker in inanimate_markers:
            if marker in y_phrase:
                return 'inan'
        
        # Default to inanimate for longer phrases
        if len(y_phrase) > 4:
            return 'inan'
        
        return 'inan'


# Singleton instance
_extractor = None

def get_extractor(use_ltp: bool = True) -> PredicateExtractor:
    """Get or create the predicate extractor instance."""
    global _extractor
    if _extractor is None:
        _extractor = PredicateExtractor(use_ltp=use_ltp)
    return _extractor


def extract_components(sentence: str) -> Dict[str, str]:
    """
    Convenience function to extract components from a sentence.
    
    Args:
        sentence: Chinese sentence containing 对
        
    Returns:
        Dictionary with x_phrase, y_phrase, predicate, pred_comp, y_anim
    """
    extractor = get_extractor(use_ltp=False)  # Use rules by default for speed
    return extractor.extract(sentence)
