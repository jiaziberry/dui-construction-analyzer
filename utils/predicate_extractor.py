# -*- coding: utf-8 -*-
"""
Predicate Extractor Module
===========================
Extracts Y and predicate from 对-construction sentences.
Uses LTP (Language Technology Platform) for Chinese NLP.
"""

import re
from typing import Dict, Optional, Tuple, List
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
        Initialise the extractor.
        
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
    
    def _preprocess_sentence(self, sentence: str) -> str:
        """
        Preprocess sentence to handle whitespace, weird symbols, and corpus markers.
        
        Handles:
        - All whitespace (spaces, tabs, newlines, etc.)
        - Control characters
        - BCC corpus markers (NR, NS, NT, NZ)
        - Special punctuation and symbols
        - Unicode normalisation
        """
        if not sentence:
            return ''
        
        # 1. Strip all whitespace (regular and Unicode spaces)
        sentence = re.sub(r'\s+', '', sentence)
        sentence = re.sub(r'[\u00a0\u2000-\u200b\u2028\u2029\u202f\u205f\u3000]+', '', sentence)
        
        # 2. Remove control characters
        sentence = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sentence)
        
        # 3. Handle BCC corpus markers - replace with placeholder names
        # NR = person name, NS = place name, NT = organization, NZ = other proper noun
        sentence = re.sub(r'NRNR', '某某', sentence)  # Double NR
        sentence = re.sub(r'NR', '某人', sentence)     # Single person
        sentence = re.sub(r'NS', '某地', sentence)     # Place
        sentence = re.sub(r'NT', '某机构', sentence)   # Organisation  
        sentence = re.sub(r'NZ', '某某', sentence)     # Other proper noun
        
        # 4. Remove common noise symbols (but keep Chinese punctuation)
        # Keep: Chinese punctuation (。，！？、；：""''（）【】)
        # Remove: weird brackets, invisible chars, etc.
        sentence = re.sub(r'[「」『』〖〗〔〕]', '', sentence)  # Japanese brackets
        sentence = re.sub(r'[\u200c\u200d\ufeff]', '', sentence)  # Zero-width chars
        sentence = re.sub(r'[●○◎◇◆□■△▲▽▼★☆]', '', sentence)  # Symbols
        
        # 5. Normalise some common variants
        sentence = sentence.replace('　', '')  # Full-width space
        sentence = sentence.replace('︰', '：')  # Variant colon
        sentence = sentence.replace('︔', '；')  # Variant semicolon
        
        # 6. Remove leading/trailing punctuation that might interfere
        sentence = sentence.strip('。，！？；：、')
        
        return sentence
    
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
        # Comprehensive preprocessing
        sentence = self._preprocess_sentence(sentence)
        
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
        Uses semantic dependency parsing (SDP) to find the main predicate.
        """
        # Get segmentation and hidden states
        seg_result, hidden = self.ltp.seg([sentence])
        words = seg_result[0]
        
        # Get POS tags and dependency parse
        pos_result = self.ltp.pos(hidden)
        pos_tags = pos_result[0]
        
        dep_result = self.ltp.dep(hidden)
        dep = dep_result[0]  # List of (head_idx, child_idx, relation)
        
        # Find 对 position
        dui_idx = None
        for i, word in enumerate(words):
            if word == '对':
                dui_idx = i
                break
        
        if dui_idx is None:
            return self._extract_with_rules(sentence)
        
        # Build dependency graph
        # dep format: list of tuples (child_idx, head_idx, relation) - 1-indexed
        heads = {}  # child -> head
        relations = {}  # child -> relation
        children = {}  # head -> list of children
        
        for item in dep:
            child_idx = item[0] - 1  # Convert to 0-indexed
            head_idx = item[1] - 1   # -1 for root
            rel = item[2]
            heads[child_idx] = head_idx
            relations[child_idx] = rel
            if head_idx not in children:
                children[head_idx] = []
            children[head_idx].append(child_idx)
        
        # Find the root/main predicate (head_idx == -1 means root)
        root_idx = None
        for child_idx, head_idx in heads.items():
            if head_idx == -1:
                root_idx = child_idx
                break
        
        # Find what 对 modifies (its head)
        dui_head_idx = heads.get(dui_idx, -1)
        
        # The main predicate is usually:
        # 1. The root of the sentence, OR
        # 2. What 对 ultimately depends on
        main_pred_idx = root_idx if root_idx is not None else dui_head_idx
        
        # Find Y: words between 对 and the main predicate
        # But need to handle relative clauses (的 constructions)
        y_start = dui_idx + 1
        y_end = main_pred_idx if main_pred_idx > dui_idx else len(words) - 1
        
        # Adjust Y end: find the actual boundary
        # Y ends at main predicate, but if there's a 的 structure, include it
        for i in range(dui_idx + 1, len(words)):
            word = words[i]
            pos = pos_tags[i]
            
            # If we hit the main predicate (verb/adj not in 的-clause), stop
            if i == main_pred_idx:
                y_end = i
                break
            
            # If this word is a verb/adj and NOT followed by 的, it might be the pred
            if pos.startswith('v') or pos.startswith('a'):
                # Check if this is inside a 的 clause
                if i + 1 < len(words) and words[i + 1] == '的':
                    # Part of relative clause, include in Y
                    continue
                elif i + 1 < len(words) and pos_tags[i + 1].startswith('n'):
                    # Verb followed by noun, might be relative clause
                    continue
                else:
                    # This could be the main predicate
                    y_end = i
                    break
        
        # Build Y phrase
        y_phrase = ''.join(words[y_start:y_end])
        
        # Get predicate
        if y_end < len(words):
            predicate = words[y_end]
            pred_comp = ''.join(words[y_end:]).rstrip('。，！？；')
        else:
            predicate = ''
            pred_comp = ''
        
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
        Improved to handle complex sentences.
        Note: Sentence is already preprocessed by _preprocess_sentence()
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
        
        # Remove trailing punctuation
        after_dui = re.sub(r'[。，！？；、]+$', '', after_dui)
        
        # =============================================================
        # PATTERN MATCHING (order matters - most specific first)
        # =============================================================
        
        # Pattern A: 对 + Y + 体会/感受/印象 + 很/非常 + adj
        # e.g., "对这一点体会很深刻" → Y=这一点, pred=体会, comp=体会很深刻
        pattern_a = re.match(
            r'^(.+?)(体会|感受|印象|认识|了解|理解)(很|非常|十分|特别|极其|相当)?(.+)$',
            after_dui
        )
        if pattern_a:
            result['y_phrase'] = pattern_a.group(1)
            result['predicate'] = pattern_a.group(2)
            result['pred_comp'] = pattern_a.group(2) + (pattern_a.group(3) or '') + pattern_a.group(4)
            result['y_anim'] = self._detect_animacy(result['y_phrase'])
            return result
        
        # Pattern B: 对 + [time/relative clause]的事情/问题 + adj/verb
        # e.g., "对昨天发生的事情非常愤怒" → Y=昨天发生的事情, pred=愤怒
        pattern_b = re.match(
            r'^(.+?的(?:事情|问题|事|情况|现象|行为|做法|态度|结果|消息|决定))(很|非常|十分|特别|极其|相当)?(.+)$',
            after_dui
        )
        if pattern_b:
            result['y_phrase'] = pattern_b.group(1)
            pred_part = (pattern_b.group(2) or '') + pattern_b.group(3)
            result['predicate'], result['pred_comp'] = self._extract_predicate_from_rest(pred_part)
            result['y_anim'] = self._detect_animacy(result['y_phrase'])
            return result
        
        # Pattern C: 对 + Y + 的 + noun + predicate (possessive Y)
        # e.g., "对你的情况不太了解" → Y=你的情况, pred=了解
        pattern_c = re.match(
            r'^([\u4e00-\u9fff]{1,4})的([\u4e00-\u9fff]{1,2})(不太|非常|十分|特别|很|比较|相当|极其|更加|越来越)?(.+)$',
            after_dui
        )
        if pattern_c:
            result['y_phrase'] = pattern_c.group(1) + '的' + pattern_c.group(2)
            pred_part = (pattern_c.group(3) or '') + pattern_c.group(4)
            result['predicate'], result['pred_comp'] = self._extract_predicate_from_rest(pred_part)
            result['y_anim'] = self._detect_animacy(result['y_phrase'])
            return result
        
        # Pattern D: 对 + pronoun + adverb + predicate
        # e.g., "对我很不好" → Y=我, pred=不好
        pattern_d = re.match(
            r'^(我|你|他|她|它|我们|你们|他们|她们|自己|大家|别人|对方|谁)(很|非常|十分|特别|极其|相当|比较|更加|越来越|不太|不够)?(.+)$',
            after_dui
        )
        if pattern_d:
            result['y_phrase'] = pattern_d.group(1)
            pred_part = (pattern_d.group(2) or '') + pattern_d.group(3)
            result['predicate'], result['pred_comp'] = self._extract_predicate_from_rest(pred_part)
            result['y_anim'] = self._detect_animacy(result['y_phrase'])
            return result
        
        # Pattern E: 对 + demonstrative/这/那 + classifier + noun + predicate
        # e.g., "对这件事很生气" → Y=这件事, pred=生气
        # Pattern E1: 对 + 这个/那个 + common noun + adverb + predicate
        # e.g., "对这个问题很了解" → Y=这个问题, pred=了解
        # NOTE: Explicitly match common nouns to avoid greedy/non-greedy issues
        common_nouns = '问题|事情|事|情况|人|现象|结果|方案|计划|项目|政策|制度|国家|社会|工作|行为|做法|态度|观点|看法|意见|决定|消息'
        pattern_e1 = re.match(
            rf'^(这个|那个|这些|那些|这种|那种|这件|那件|这位|那位)({common_nouns})(很|非常|十分|特别|极其|相当|比较|不太)?(.+)$',
            after_dui
        )
        if pattern_e1:
            y_base = pattern_e1.group(1) + pattern_e1.group(2)
            pred_part = (pattern_e1.group(3) or '') + pattern_e1.group(4)
            pred, comp = self._extract_predicate_from_rest(pred_part)
            if pred:
                result['y_phrase'] = y_base
                result['predicate'] = pred
                result['pred_comp'] = comp
                result['y_anim'] = self._detect_animacy(result['y_phrase'])
                return result
        
        # Pattern E2: 对 + 这/那/此 + classifier + noun + predicate
        pattern_e = re.match(
            r'^(这|那|此|这一点|那一点)([\u4e00-\u9fff]{0,4}?)(很|非常|十分|特别|极其|相当|比较)?(.+)$',
            after_dui
        )
        if pattern_e:
            y_base = pattern_e.group(1) + pattern_e.group(2)
            pred_part = (pattern_e.group(3) or '') + pattern_e.group(4)
            
            # Check if pred_part starts with a known predicate
            pred, comp = self._extract_predicate_from_rest(pred_part)
            if pred:
                result['y_phrase'] = y_base
                result['predicate'] = pred
                result['pred_comp'] = comp
                result['y_anim'] = self._detect_animacy(result['y_phrase'])
                return result
        
        # Pattern F: 对 + noun phrase + 进行/实行/采取/给予 + action
        # e.g., "对企业采取措施" → Y=企业, pred=采取
        pattern_f = re.match(
            r'^(.+?)(进行|实行|实施|采取|给予|予以|加以|作出|做出|发起|展开|开展|提出|发表|表示)(.*)$',
            after_dui
        )
        if pattern_f:
            result['y_phrase'] = pattern_f.group(1)
            result['predicate'] = pattern_f.group(2)
            result['pred_comp'] = pattern_f.group(2) + pattern_f.group(3)
            result['y_anim'] = self._detect_animacy(result['y_phrase'])
            return result
        
        # Pattern G: 对 + noun + 说/讲/问/喊 (speech verbs)
        # e.g., "对我说了一番话" → Y=我, pred=说
        pattern_g = re.match(
            r'^(.+?)(说|讲|问|喊|叫|骂|笑|点头|挥手|鞠躬|道|说道|笑道|问道|叫道)(.*)$',
            after_dui
        )
        if pattern_g:
            result['y_phrase'] = pattern_g.group(1)
            result['predicate'] = pattern_g.group(2)
            result['pred_comp'] = pattern_g.group(2) + pattern_g.group(3)
            result['y_anim'] = self._detect_animacy(result['y_phrase'])
            return result
        
        # Pattern J: 对 + Y + effect predicate (EVAL) - MUST come before Pattern H!
        # e.g., "对健康有害" → Y=健康, pred=有害
        # These multi-char predicates starting with 有/无 must be checked before Pattern H
        pattern_j = re.match(
            r'^(.+?)(有害|有利|有益|有用|无用|无害|重要|必要|关键|危险|不利|有效|无效|合适)(.*)$',
            after_dui
        )
        if pattern_j:
            result['y_phrase'] = pattern_j.group(1)
            result['predicate'] = pattern_j.group(2)
            result['pred_comp'] = pattern_j.group(2) + pattern_j.group(3)
            result['y_anim'] = self._detect_animacy(result['y_phrase'])
            return result
        
        # Pattern H: 对 + Y + 有/没有/充满/缺乏 + noun
        # e.g., "对她充满信心" → Y=她, pred=充满
        pattern_h = re.match(
            r'^(.+?)(有|没有|没|充满|缺乏|怀有|抱有|富有|具有|拥有|享有|带有|含有|存有|持有|保有|失去|丧失|有所|毫无)(.+)$',
            after_dui
        )
        if pattern_h:
            result['y_phrase'] = pattern_h.group(1)
            result['predicate'] = pattern_h.group(2)
            result['pred_comp'] = pattern_h.group(2) + pattern_h.group(3)
            result['y_anim'] = self._detect_animacy(result['y_phrase'])
            return result
        
        # Pattern I: 对 + Y + psychological/evaluative predicate
        # e.g., "对他很满意" → Y=他, pred=满意
        psych_predicates = (
            '满意|不满|失望|生气|愤怒|高兴|感兴趣|有兴趣|好奇|担心|担忧|'
            '害怕|恐惧|喜欢|讨厌|厌恶|热爱|敬佩|佩服|尊重|信任|怀疑|'
            '了解|熟悉|理解|认识|知道|明白|清楚|'
            '热情|冷淡|客气|友好|好|不好|坏|严格|宽容|负责|认真'
        )
        pattern_i = re.match(
            rf'^(.+?)(很|非常|十分|特别|极其|相当|比较|不太|不够|更加|越来越)?({psych_predicates})(.*)$',
            after_dui
        )
        if pattern_i:
            result['y_phrase'] = pattern_i.group(1)
            result['predicate'] = pattern_i.group(3)
            result['pred_comp'] = (pattern_i.group(2) or '') + pattern_i.group(3) + pattern_i.group(4)
            result['y_anim'] = self._detect_animacy(result['y_phrase'])
            return result
        
        # Pattern K: Generic fallback - find first verb/adj boundary
        # Try to find where Y ends and predicate begins
        y_phrase, pred, pred_comp = self._generic_extraction(after_dui)
        if y_phrase and pred:
            result['y_phrase'] = y_phrase
            result['predicate'] = pred
            result['pred_comp'] = pred_comp
            result['y_anim'] = self._detect_animacy(result['y_phrase'])
            return result
        
        # Last resort: just split at a reasonable point
        result['y_phrase'] = after_dui[:len(after_dui)//2] if len(after_dui) > 2 else after_dui
        result['pred_comp'] = after_dui[len(after_dui)//2:] if len(after_dui) > 2 else ''
        result['predicate'] = result['pred_comp'][:2] if result['pred_comp'] else ''
        result['y_anim'] = self._detect_animacy(result['y_phrase'])
        
        return result
    
    def _extract_predicate_from_rest(self, text: str) -> Tuple[str, str]:
        """
        Extract predicate from remaining text after Y.
        Returns (predicate, pred_comp)
        """
        if not text:
            return '', ''
        
        # Remove leading adverbs
        adverbs = ['很', '非常', '十分', '特别', '极其', '相当', '比较', '不太', '不够', '更加', '越来越', '最']
        predicate_start = text
        adv_prefix = ''
        
        for adv in sorted(adverbs, key=len, reverse=True):
            if text.startswith(adv):
                adv_prefix = adv
                predicate_start = text[len(adv):]
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
            '不好', '不友好', '不客气', '没耐心', '不认真',  # negated DISP
            '愤怒', '生气', '高兴', '失望', '惊讶', '好奇',  # emotions
            '严格', '宽容', '认真', '体会', '印象', '感受',  # MS/DISP
        ]
        
        for pred in sorted(multi_preds, key=len, reverse=True):
            if predicate_start.startswith(pred):
                return pred, adv_prefix + text
        
        # Single char predicates
        single_preds = ['说', '讲', '问', '看', '听', '想', '做', '作', '有', '是', '像', '好', '坏', '怕', '爱', '恨']
        if predicate_start and predicate_start[0] in single_preds:
            return predicate_start[0], adv_prefix + text
        
        # Default: first 1-2 chars
        if len(predicate_start) >= 2:
            return predicate_start[:2], adv_prefix + text
        elif predicate_start:
            return predicate_start[0], adv_prefix + text
        
        return '', text
    
    def _generic_extraction(self, after_dui: str) -> Tuple[str, str, str]:
        """
        Generic extraction when no pattern matches.
        Try to find the boundary between Y and predicate.
        """
        # Known predicate starters (verbs/adj that commonly start predicates)
        pred_starters = [
            '进行', '实行', '实施', '采取', '给予', '予以', '表示', '提出',
            '作出', '做出', '感到', '产生', '造成', '充满', '缺乏', '失去',
            '有所', '毫无', '有', '没有', '没', '是', '很', '非常', '不',
            '说', '讲', '问', '看', '想', '做', '作',
            '喜欢', '讨厌', '害怕', '担心', '满意', '了解', '熟悉', '理解',
            '热情', '冷淡', '客气', '友好', '尊重', '信任', '怀疑',
            '体会', '感受', '认识', '印象',
        ]
        
        # Try to find where predicate starts
        for i in range(1, len(after_dui)):
            remaining = after_dui[i:]
            for pred in sorted(pred_starters, key=len, reverse=True):
                if remaining.startswith(pred):
                    y_phrase = after_dui[:i]
                    pred_comp = remaining
                    return y_phrase, pred, pred_comp
        
        return '', '', ''
    
    def _detect_animacy(self, y_phrase: str) -> str:
        """
        Detect if Y is animate or inanimate.
        """
        if not y_phrase:
            return 'inan'
        
        # Animate markers (pronouns, people words)
        animate_markers = {
            # Pronouns
            '我', '你', '他', '她', '它', '我们', '你们', '他们', '她们', '咱们',
            '自己', '本人', '人家', '别人', '大家', '各位', '谁', '某人', '有人', '对方',
            # People
            '人', '人们', '学生', '老师', '医生', '患者', '观众', '读者', '孩子',
            '父母', '朋友', '同事', '客人', '员工', '领导', '群众', '民众', '百姓',
            '父亲', '母亲', '儿子', '女儿', '妻子', '丈夫', '哥哥', '姐姐',
            # Titles
            '先生', '女士', '小姐', '同志', '老板', '经理', '主任', '校长',
        }
        
        for marker in animate_markers:
            if marker in y_phrase:
                return 'anim'
        
        # Inanimate markers
        inanimate_markers = {
            '事', '事情', '问题', '情况', '现象', '结果',
            '政策', '制度', '措施', '方法', '做法', '方案', '计划',
            '工作', '任务', '项目', '活动', '行动',
            '社会', '国家', '市场', '经济', '发展', '生活',
            '健康', '环境', '自然', '世界', '未来',
        }
        
        for marker in inanimate_markers:
            if y_phrase.endswith(marker):
                return 'inan'
        
        # Common surnames (Chinese names are animate)
        surnames = {
            '李', '王', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴',
            '徐', '孙', '马', '胡', '朱', '郭', '何', '林', '罗', '高',
        }
        if y_phrase and y_phrase[0] in surnames and len(y_phrase) <= 4:
            return 'anim'
        
        # Short phrases without inanimate markers tend to be animate
        if len(y_phrase) <= 3:
            return 'anim'
        
        return 'inan'


# Module-level helper functions for backwards compatibility
_extractor_instance = None

def get_extractor(use_ltp: bool = True) -> PredicateExtractor:
    """Get or create a PredicateExtractor instance."""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = PredicateExtractor(use_ltp=use_ltp)
    return _extractor_instance

def extract_components(sentence: str, use_ltp: bool = True) -> Dict[str, str]:
    """Extract components from a sentence."""
    extractor = get_extractor(use_ltp)
    return extractor.extract(sentence)
