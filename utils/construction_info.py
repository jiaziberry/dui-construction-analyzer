# -*- coding: utf-8 -*-
"""
Construction Information Module
================================
Educational content about the six 对-construction types.
"""

CONSTRUCTION_INFO = {
    "DA": {
        "name_en": "Directed-Action",
        "name_zh": "指向型动作构式",
        "short_description": "X intentionally performs an action directed toward Y",
        "full_description": """
**Directed-Action (DA)** is a construction where the subject (X) intentionally performs 
an action **directed toward** Y. The action flows TO/AT Y as recipient, addressee, or target. 
Y receives the action but is not necessarily transformed.

This is the most common 对-construction, accounting for about 32% of all instances.
It primarily includes speech acts (说, 讲, 问), gestures (笑, 点头), and communicative acts.
        """,
        "dui_meaning": "toward / to (PATH → GOAL)",
        "dui_function": "Marks the direction or endpoint of X's action",
        "key_characteristics": [
            "Directional: Action has inherent direction toward Y",
            "Animate Y: Y is typically a person or group",
            "V他✗ test: Many DA verbs cannot take direct object (*说他, *笑他)",
            "Speech acts: Most common pattern - communicative acts TO addressee",
            "Gestures: Physical actions directed AT person"
        ],
        "typical_patterns": [
            ("Speech 道 verbs", "对NR 笑道/说道/问道", "Quoted speech TO person"),
            ("Communicative verbs", "对他 说/讲/解释/批评", "Speech act TO animate Y"),
            ("Gestures", "对她 点头/挥手/鞠躬", "Physical action AT person"),
            ("Display", "对观众 展示/表演", "Performance directed AT audience")
        ],
        "semantic_roles": {
            "fillmore": {
                "X": "Agent / Communicator",
                "Y": "Goal / Recipient / Addressee"
            },
            "dowty": {
                "X": {
                    "proto_agent": ["✓ Volitional", "✓ Causative", "✓ Controls event"],
                    "proto_patient": []
                },
                "Y": {
                    "proto_agent": [],
                    "proto_patient": ["○ May receive something", "○ May be gently affected", "✗ Not transformed"]
                }
            }
        },
        "example_sentences": [
            {"zh": "他对我说了一番话。", "en": "He said something to me.", "analysis": "说 is a speech act directed TO me (recipient)"},
            {"zh": "她对观众微笑。", "en": "She smiled at the audience.", "analysis": "微笑 is a gesture directed AT the audience"},
            {"zh": "老师对学生解释道。", "en": "The teacher explained to the students.", "analysis": "解释 is an explanation directed TO students"}
        ],
        "color": "#4CAF50"
    },
    
    "SI": {
        "name_en": "Scoped-Intervention",
        "name_zh": "范围干预构式",
        "short_description": "X carries out bounded intervention upon Y",
        "full_description": """
**Scoped-Intervention (SI)** is a construction where X (often institutional) carries out 
**bounded, procedural intervention** upon Y. Y is treated as a domain, scope, or patient 
under X's operational control. Y undergoes change or is affected by the intervention.

This construction accounts for about 23% of all instances and is dominated by 进行 
(carry out/conduct), which appears in 37% of SI cases. Other common verbs include 
实行, 负责, 采取, and 实施.
        """,
        "dui_meaning": "upon / on / over (CONTACT / DOMAIN)",
        "dui_function": "Marks Y as the bounded scope of intervention",
        "key_characteristics": [
            "Bounded scope: Y is a delimited operational domain",
            "Y affected: Y undergoes status change (被检查, 被处罚, 被保护)",
            "V他✓ test: SI verbs CAN take direct object (帮助他✓, 保护他✓)",
            "Institutional: Often involves authority, policy, procedure",
            "Procedural: Action is bounded, can be completed"
        ],
        "typical_patterns": [
            ("进行 + action", "对Y 进行 调查/研究/处理", "Conduct procedural action ON scope"),
            ("Institutional verbs", "对Y 检查/监督/整顿/管理", "Procedural intervention ON scope"),
            ("Policy application", "对Y 实行/实施/执行/采取", "Applying regime TO bounded domain"),
            ("Care/Help verbs", "对Y 帮助/照顾/保护/培训", "Bounded intervention (V他✓)"),
            ("Tolerance verbs", "对Y 原谅/包容/宽恕/体谅", "Bounded act ON recipient (V他✓)")
        ],
        "semantic_roles": {
            "fillmore": {
                "X": "Agent / Authority / Implementer",
                "Y": "Patient / Scope / Domain"
            },
            "dowty": {
                "X": {
                    "proto_agent": ["✓ Volitional", "✓ Causative", "✓ Controls intervention"],
                    "proto_patient": []
                },
                "Y": {
                    "proto_agent": [],
                    "proto_patient": ["✓ Undergoes change of state", "✓ Causally affected", "✓ Domain of operation"]
                }
            }
        },
        "example_sentences": [
            {"zh": "警方对这个案件进行调查。", "en": "The police are conducting an investigation into this case.", "analysis": "进行调查 is a procedural intervention ON the case (scope)"},
            {"zh": "公司对员工实行培训。", "en": "The company implements training for employees.", "analysis": "实行培训 is an institutional intervention ON employees (affected)"},
            {"zh": "他对朋友很负责。", "en": "He is accountable to his friends.", "analysis": "负责 indicates accountability/obligation TO scope"}
        ],
        "color": "#2196F3"
    },
    
    "MS": {
        "name_en": "Mental-State",
        "name_zh": "心理状态构式",
        "short_description": "Y triggers an internal psychological state in X",
        "full_description": """
**Mental-State (MS)** is a construction where X as Experiencer has an **internal psychological, 
emotional, or cognitive state** where Y serves as the **stimulus** that triggers or is the 
reference point for that state. Y causes or elicits the psychological response in X.

This construction accounts for about 24% of all instances. The key feature is that Y 
**triggers** something internal in X's mind - it's not observable from outside. Common 
patterns include emotional states (喜欢, 害怕), cognitive states (了解, 熟悉), and 
attentional states (关心, 重视).
        """,
        "dui_meaning": "toward / concerning (PSYCHOLOGICAL ORIENTATION)",
        "dui_function": "Marks Y as the stimulus/trigger of X's mental state",
        "key_characteristics": [
            "Internal (内心): Not directly observable - describes what X thinks/feels",
            "Y as stimulus: Y triggers, causes, or elicits the psychological state",
            "State-based: Can emerge, disappear, be maintained, intensify",
            "Y unaffected: Y does not change due to X's state",
            "Range: Includes emotions, cognition, attention, attitudes, trust"
        ],
        "typical_patterns": [
            ("感/觉得 + state", "对Y 感到 高兴/满意/失望", "Feeling marker + emotional state"),
            ("存/抱 + state", "对Y 抱 希望/怀疑", "State marker + psych noun"),
            ("产生 + state", "对Y 产生 好感/兴趣/怀疑", "State arising from Y"),
            ("有 + state", "对Y 有 兴趣/信心/好感/印象", "Having psychological state"),
            ("缺乏 + state", "对Y 缺乏 兴趣/信心/了解", "Absence of psychological state")
        ],
        "semantic_roles": {
            "fillmore": {
                "X": "Experiencer / Cognizer",
                "Y": "Stimulus / Trigger"
            },
            "dowty": {
                "X": {
                    "proto_agent": ["✓ Sentient", "○ May or may not be volitional", "✗ Not strongly causative"],
                    "proto_patient": []
                },
                "Y": {
                    "proto_agent": [],
                    "proto_patient": ["✗ Not affected by X's state", "✓ Properties trigger X's state", "✓ Stimulus for psychological response"]
                }
            }
        },
        "example_sentences": [
            {"zh": "我对这个问题很了解。", "en": "I understand this problem well.", "analysis": "Y (问题) triggers a knowledge state IN X"},
            {"zh": "他对她充满信心。", "en": "He is full of confidence in her.", "analysis": "Y (她) triggers confidence state IN X"},
            {"zh": "学生对老师很尊重。", "en": "The students respect the teacher.", "analysis": "Y (老师) triggers internal respect IN students"}
        ],
        "color": "#9C27B0"
    },
    
    "ABT": {
        "name_en": "Aboutness",
        "name_zh": "论及构式",
        "short_description": "X produces external discourse ABOUT Y",
        "full_description": """
**Aboutness (ABT)** is a construction where X engages in **external cognitive or discursive 
activity ABOUT** Y. Y is the topic, subject matter, or content of X's discourse - not a 
stimulus that triggers a state. X **produces** speech, writing, or commentary.

This construction accounts for about 8.5% of all instances. The key distinction from MS 
is that ABT involves **external, observable** discourse production (评价, 分析, 研究), 
while MS involves **internal, non-observable** psychological states (了解, 怀疑, 尊重).
        """,
        "dui_meaning": "about / concerning / regarding (TOPIC FRAME)",
        "dui_function": "Marks Y as the subject matter of discourse",
        "key_characteristics": [
            "External activity: Observable speech/writing/analytical acts",
            "Y as topic: Y is what X talks/writes/comments about",
            "Y unaffected: Y does not change due to X's discourse",
            "Discourse verbs: Verbs of speaking, writing, analyzing, commenting",
            "Produces output: The activity results in discourse (words, analysis)"
        ],
        "typical_patterns": [
            ("Commentary", "对Y 评价/评论/评述/点评", "Produce evaluative discourse"),
            ("Analysis", "对Y 分析/研究/探讨/考察", "Produce analytical discourse"),
            ("Discussion", "对Y 讨论/辩论/争论/商议", "Engage in discussion about Y"),
            ("提出 + discourse", "对Y 提出 建议/意见/批评/质疑", "Put forward discourse about Y"),
            ("作/做 + discourse", "对Y 作/做 分析/评论/说明", "Perform discourse act")
        ],
        "semantic_roles": {
            "fillmore": {
                "X": "Agent / Communicator",
                "Y": "Topic / Theme"
            },
            "dowty": {
                "X": {
                    "proto_agent": ["✓ Volitional", "○ Causative in speaking", "✓ Controls discourse"],
                    "proto_patient": []
                },
                "Y": {
                    "proto_agent": [],
                    "proto_patient": ["✗ No change of state", "✗ Not 'operated on'", "✓ Non-affected Theme"]
                }
            }
        },
        "example_sentences": [
            {"zh": "专家对这个问题提出了看法。", "en": "The expert put forward views on this issue.", "analysis": "提出看法 is external discourse ABOUT the topic (问题)"},
            {"zh": "记者对事件进行了报道。", "en": "The reporter covered the event.", "analysis": "报道 is external discourse activity ABOUT the event"},
            {"zh": "学者对此不予置评。", "en": "The scholar declined to comment on this.", "analysis": "置评 is a refusal to produce discourse ABOUT the topic"}
        ],
        "color": "#FF9800"
    },
    
    "DISP": {
        "name_en": "Disposition",
        "name_zh": "态度处置构式",
        "short_description": "X exhibits behavioral manner toward Y",
        "full_description": """
**Disposition (DISP)** is a construction where X exhibits a characteristic **behavioral manner 
or social attitude** toward Y in interpersonal interaction. This describes HOW X behaves, 
treats, or relates to Y in observable social ways - the manner or style of interaction.

This is the rarest construction, accounting for only about 2.2% of all instances. DISP 
uses **stative predicates** (adjectives/manner expressions) and answers the question 
"对Y怎么样?" (How does X treat Y?). Common predicates include 好, 客气, 热情, 冷淡.
        """,
        "dui_meaning": "toward (BEHAVIORAL/SOCIAL ORIENTATION)",
        "dui_function": "Marks Y as the target of X's behavioral manner",
        "key_characteristics": [
            "Behavioral (行为态度): Observable manner of interaction",
            "Social context: Describes how X treats/relates to Y",
            "Manner-based: Focus on style/way of behaving",
            "Stative predicate: Uses adjectives, not active verbs",
            "Animate Y: Typically requires animate social partner",
            "Answers: '对Y怎么样?' (How does X treat Y?)"
        ],
        "typical_patterns": [
            ("Warm manner", "对Y 热情/热心/亲切/友善", "Warm behavioral manner"),
            ("Cold manner", "对Y 冷淡/冷漠/疏远", "Cold behavioral manner"),
            ("Polite manner", "对Y 客气/礼貌/恭敬", "Polite treatment"),
            ("Treatment", "对Y 好/善待/厚待", "How X treats Y"),
            ("Simile", "对Y 像/如同 (某人)", "Treatment comparison")
        ],
        "semantic_roles": {
            "fillmore": {
                "X": "Agent / Actor",
                "Y": "Social Partner / Recipient"
            },
            "dowty": {
                "X": {
                    "proto_agent": ["✓ Volitional", "✓ Controls behavior", "✓ Can be praised/blamed"],
                    "proto_patient": []
                },
                "Y": {
                    "proto_agent": [],
                    "proto_patient": ["✗ Not typically affected in state", "✓ Receives/experiences X's manner"]
                }
            }
        },
        "example_sentences": [
            {"zh": "他对客人很客气。", "en": "He is very polite to guests.", "analysis": "客气 describes X's observable manner toward Y"},
            {"zh": "她对孩子像亲生的一样。", "en": "She treats the child like her own.", "analysis": "像 compares X's treatment manner toward Y"},
            {"zh": "老板对员工很好。", "en": "The boss treats employees well.", "analysis": "好 describes X's behavioral manner toward Y"}
        ],
        "color": "#E91E63"
    },
    
    "EVAL": {
        "name_en": "Evaluation",
        "name_zh": "评价构式",
        "short_description": "X is evaluated as good/bad/useful FOR Y",
        "full_description": """
**Evaluation (EVAL)** is a construction where X as Theme is **evaluated as good/bad/useful/harmful 
FOR** Y. 对 introduces the perspective, beneficiary, or frame of reference from which X is judged. 
Y is the entity affected by or benefiting/suffering from X.

This construction accounts for about 10% of all instances. The key feature is that X (not Y!) 
is being evaluated, and 对Y provides the perspective "for whom" the evaluation applies. Common 
predicates include 有 (benefit/harm), 产生 (produce effect), 造成 (cause), 重要 (important).
        """,
        "dui_meaning": "for / with regard to / in terms of (PERSPECTIVE / BENEFICIARY FRAME)",
        "dui_function": "Marks Y as the perspective from which X is evaluated",
        "key_characteristics": [
            "Evaluative: X has property (good/bad/useful) relative to Y",
            "Y as perspective: Y is 'for whom' the evaluation applies",
            "X as Theme: X is what is being evaluated (not Agent)",
            "Effect semantics: Often involves benefit/harm to Y",
            "Stative: Describes a property, not an action"
        ],
        "typical_patterns": [
            ("Beneficial", "对Y 有用/有益/有利/有帮助", "X is beneficial FOR Y"),
            ("Harmful", "对Y 有害/不利/危险", "X is harmful FOR Y"),
            ("Important", "对Y 重要/必要/关键", "X is important FOR Y"),
            ("Effect verbs", "对Y 造成/导致/带来 影响", "X causes effect ON Y"),
            ("具有+意义", "对Y 具有 重要意义/积极作用", "X has significance FOR Y")
        ],
        "semantic_roles": {
            "fillmore": {
                "X": "Theme / Evaluated Entity",
                "Y": "Experiencer / Beneficiary / Perspective"
            },
            "dowty": {
                "X": {
                    "proto_agent": ["✗ X is not Agent", "✗ X has a property"],
                    "proto_patient": []
                },
                "Y": {
                    "proto_agent": [],
                    "proto_patient": ["✗ Not causally affected in event", "✓ Frame relative to which X is evaluated", "✓ May benefit or suffer"]
                }
            }
        },
        "example_sentences": [
            {"zh": "吸烟对健康有害。", "en": "Smoking is harmful to health.", "analysis": "X (吸烟) is evaluated as harmful FOR Y (健康)"},
            {"zh": "这个决定对公司很重要。", "en": "This decision is important for the company.", "analysis": "X (决定) is evaluated as important FOR Y (公司)"},
            {"zh": "暴雨对农业造成了影响。", "en": "The heavy rain had an impact on agriculture.", "analysis": "X (暴雨) causes effect ON Y (农业)"}
        ],
        "color": "#795548"
    }
}

# MS vs ABT distinction - critical for teaching
MS_VS_ABT_DISTINCTION = {
    "title": "MS vs ABT: The Critical Distinction",
    "key_question": "Does Y TRIGGER a psychological state IN X?",
    "comparison": [
        {
            "feature": "Nature",
            "MS": "Internal psychological state",
            "ABT": "External discourse activity"
        },
        {
            "feature": "Y's role",
            "MS": "Stimulus that triggers state IN X",
            "ABT": "Topic of X's discourse"
        },
        {
            "feature": "Observable?",
            "MS": "No (in X's mind)",
            "ABT": "Yes (speech/writing)"
        },
        {
            "feature": "Verb type",
            "MS": "State verbs",
            "ABT": "Activity verbs"
        },
        {
            "feature": "Output",
            "MS": "X has a state",
            "ABT": "X produces discourse"
        }
    ],
    "examples": [
        {"verb": "了解", "type": "MS", "reason": "Y triggers knowledge state IN X (internal)"},
        {"verb": "分析", "type": "ABT", "reason": "X produces analytical discourse ABOUT Y (external)"},
        {"verb": "怀疑", "type": "MS", "reason": "Y triggers doubt/skepticism IN X (internal)"},
        {"verb": "质疑", "type": "ABT", "reason": "X raises questions ABOUT Y (external discourse)"},
        {"verb": "尊重", "type": "MS", "reason": "Y triggers respect feeling IN X (internal)"},
        {"verb": "评价", "type": "ABT", "reason": "X produces evaluative discourse ABOUT Y (external)"}
    ]
}

# Decision tree for classification
DECISION_TREE = """
1. Is X evaluated as good/bad/useful/harmful FOR Y?
   │
   ├─ YES → EVAL (有用, 有害, 重要, 公平, 造成影响)
   │
   └─ NO ↓

2. Does Y CHANGE (affected by bounded intervention)?
   │
   ├─ YES → Can V take direct object? (V他✓?)
   │        │
   │        ├─ YES (帮助他✓, 保护他✓) → SI
   │        │
   │        └─ NO (说他✗, 笑他✗) → DA
   │
   └─ NO ↓

3. Is it observable BEHAVIOR/MANNER toward Y?
   │
   ├─ YES (热情, 冷淡, 客气, 像) → DISP
   │
   └─ NO ↓

4. ★ KEY TEST: Does Y TRIGGER a psychological state IN X? ★
   │
   ├─ YES (Y causes state in X's mind) → MS
   │   (了解, 怀疑, 喜欢, 尊重, 感到高兴, 有印象)
   │
   └─ NO (Y is just topic, X produces discourse) → ABT
       (评价, 分析, 讨论, 报道, 进行研究)
"""


def get_construction_info(construction_type: str) -> dict:
    """Get information about a construction type."""
    return CONSTRUCTION_INFO.get(construction_type.upper(), None)


def get_all_construction_names() -> list:
    """Get list of all construction names."""
    return [(k, v["name_en"], v["name_zh"]) for k, v in CONSTRUCTION_INFO.items()]
