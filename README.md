# 对-Construction Analyser (对构式分析器)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

A web application for analyzing Chinese 对-constructions based on Usage-Based Construction Grammar principles.

![App Screenshot](static/screenshot.png)

## Features

- **🔍 Sentence Analyser**: Enter any Chinese sentence with 对 to:
  - Identify the construction type (DA, SI, MS, ABT, DISP, EVAL)
  - View semantic roles (Fillmore and Dowty proto-roles)
  - Understand the classification reasoning
  - See similar predicates from corpus data

- **📚 Construction Guide**: Comprehensive educational content about:
  - The six 对-construction types
  - Key characteristics and typical patterns
  - Example sentences with analysis
  - Decision tree for classification

- **📊 Corpus Statistics**: Based on 394,355 annotated instances from the BCC corpus:
  - Distribution by construction type
  - Top 20 predicates for each type
  - Frequency data visualization

- **❓ MS vs ABT Distinction**: Special focus on the critical distinction between Mental-State and Aboutness constructions

## The Six 对-Constructions

| Type | Name | Description | Example |
|------|------|-------------|---------|
| **DA** | Directed-Action | X performs action directed TO Y | 他对我说了一番话 |
| **SI** | Scoped-Intervention | X carries out intervention UPON Y | 警方对案件进行调查 |
| **MS** | Mental-State | Y triggers psychological state IN X | 我对这个问题很了解 |
| **ABT** | Aboutness | X produces discourse ABOUT Y | 专家对此发表意见 |
| **DISP** | Disposition | X exhibits manner TOWARD Y | 她对客人很热情 |
| **EVAL** | Evaluation | X is evaluated relative to Y | 吸烟对健康有害 |

## Quick Start

### Local Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/dui-construction-analyser.git
cd dui-construction-analyser

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Deploy to Streamlit Cloud

1. Fork this repository
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app" and select your forked repository
4. Set the main file path to `app.py`
5. Click "Deploy"

## Project Structure

```
dui-construction-app/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── data/
│   └── frequency_data.json   # BCC corpus frequency data
├── utils/
│   ├── __init__.py
│   ├── classifier.py         # Rule-based classifier
│   ├── predicate_extractor.py # Extract Y and predicate
│   └── construction_info.py  # Construction definitions
└── static/
    └── screenshot.png
```

## Theoretical Framework

This tool is based on the v70 classification framework developed for doctoral dissertation research on Chinese 对-constructions. The framework combines:

- **Usage-Based Construction Grammar** principles
- **Fillmore's Case Grammar** for semantic role analysis
- **Dowty's Proto-Role Theory** for agent/patient properties
- **Hybrid rule-based + ML classification** trained on BCC corpus data

### Key Distinctions

**DA vs SI**: V他 test
- DA: Cannot take direct object (*说他, *笑他) → 对 marks direction
- SI: Can take direct object (帮助他✓, 保护他✓) → 对 sets scope

**MS vs ABT**: Internal vs External
- MS: Y triggers internal state (not observable)
- ABT: X produces external discourse (observable)

**DISP vs MS**: Observable vs Internal
- DISP: Observable behavioral manner
- MS: Internal psychological state

### Example Analyses

| Sentence | Y | Predicate | Type |
|----------|---|-----------|------|
| 我对这一点体会很深刻 | 这一点 | 体会 | MS |
| 这对健康有害 | 健康 | 有害 | EVAL |
| 她对我不友好 | 我 | 不友好 | DISP |
| 政府对企业进行检查 | 企业 | 进行 | SI |
| 他对我说了一番话 | 我 | 说 | DA |

## Data Source

The frequency data comes from the **BCC Corpus** (北京语言大学现代汉语语料库), containing:
- **394,355** total 对-construction instances
- **8,191** unique predicates
- Annotated using the v70 hybrid classifier

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{dui_construction_analyser,
  title = {对-Construction Analyser},
  author = {Jiaqi},
  year = {2026},
  url = {https://github.com/yourusername/dui-construction-analyser}
}
```

## Changelog

### v1.1.0 (January 2026)

**Predicate Extraction Fixes:**
- Fixed Pattern J ordering: EVAL predicates (有害/有利/有益) now correctly extracted before generic 有 pattern
- Added whitespace stripping for sentences with irregular spacing
- New Pattern A: Handles experiential verbs (体会/感受/印象) + degree adverbs
- New Pattern B: Correctly parses relative clauses ending in 的事情/的问题/的情况

**Classifier Improvements:**
- Expanded MS_VERBS with ~20 emotion verbs: 愤怒, 生气, 高兴, 惊讶, 好奇, etc.
- Added experiential cognition verbs: 体会, 感受, 领会, 领悟, 体验

**Test Coverage:**
- All 13 core test cases passing
- Improved handling of edge cases like "这对健康有害" → EVAL

### v1.0.0 (December 2025)

- Initial release with v70 classifier framework
- Six construction types: DA, SI, MS, ABT, DISP, EVAL
- BCC corpus frequency data (394,355 instances)
- Streamlit web interface

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- BCC Corpus (北京语言大学语料库中心)
- Anthropic Claude for development assistance
- Streamlit for the web framework
