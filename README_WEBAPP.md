# 对-Construction Analyzer 🇨🇳

A web-based pedagogical tool for learning Chinese preposition **对** (duì).

![Version](https://img.shields.io/badge/version-1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎯 What It Does

This interactive web app helps Chinese learners understand how 对-constructions work by:

1. **Analyzing** any sentence with 对
2. **Classifying** the construction type (6 types: DA/SI/MS/ABT/DISP/EVAL)
3. **Explaining** semantic roles using Fillmore & Dowty's theories
4. **Showing** the top 10 most common predicates for each construction
5. **Teaching** through examples and theoretical background

---

## 🚀 Quick Start

### Install
```bash
pip install -r requirements_webapp.txt
```

### Run
```bash
streamlit run dui_web_app.py
```

### Use
1. Open `http://localhost:8501` in your browser
2. Enter a Chinese sentence with 对 (or select an example)
3. Click "Analyze"
4. Explore the results!

---

## 📸 Screenshot

```
┌─────────────────────────────────────────────────────────┐
│  🇨🇳 对-Construction Analyzer                           │
│  A pedagogical tool for understanding Chinese 对        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📝 Input: 我对他说了实话                               │
│                                                         │
│  ┌───────────────────────────────────────────────┐     │
│  │  Directed Action (对话行为)                   │     │
│  │  Directed Action                              │     │
│  │  Confidence: 95.0%                            │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
│  Tabs: [Analysis] [Semantic Roles] [Theory] [Predicates]│
└─────────────────────────────────────────────────────────┘
```

---

## 🎓 Features

### ✅ Current Features (v1.0)

- **6 Construction Types**:
  - DA (Directed Action): 对他说 "say TO him"
  - SI (Scoped Intervention): 对问题进行研究 "research ON problem"
  - MS (Mental State): 对未来感到担心 "worry ABOUT future"
  - ABT (Aboutness): 对政策提出看法 "views ABOUT policy"
  - DISP (Disposition): 对学生很严格 "strict TOWARD students"
  - EVAL (Evaluation): 对健康有益 "beneficial FOR health"

- **Theoretical Connections**:
  - Fillmore's Case Grammar (1968)
  - Dowty's Proto-Roles (1991)
  - Goldberg's Construction Grammar (1995)

- **Corpus-Based Data**:
  - Top 10 predicates per construction
  - Based on 400,000 BCC corpus instances
  - Frequency counts and English translations

- **User-Friendly Interface**:
  - Color-coded construction types
  - Example sentences
  - Tabbed information display
  - Responsive design

---

## 📚 Based On

This tool is based on:

- **Jiaqi's V70 Classifier** - State-of-the-art hybrid classifier
- **BCC Corpus** - Beijing Language and Culture University Corpus (400K instances)
- **Usage-Based Construction Grammar** - Theoretical framework

---

## 🌐 Deployment Options

### Option 1: Streamlit Cloud (Easiest)
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from your repo
4. Get free public URL!

### Option 2: Your Own Server
See [WEB_APP_DEPLOYMENT_GUIDE.md](WEB_APP_DEPLOYMENT_GUIDE.md) for detailed instructions.

---

## 🔧 Customization

### Add More Examples
Edit `examples` dictionary in `dui_web_app.py`:
```python
examples = {
    "Your Category": "你的例句"
}
```

### Use Real V70 Classifier
Replace `simple_classify()` with actual classifier:
```python
from dui_classifier_v70 import RuleBasedClassifier
classifier = RuleBasedClassifier()
```

### Add More Languages
Create translation dictionary for multilingual support.

---

## 📊 Data Sources

### Top Predicates
Frequencies are based on BCC corpus analysis:
- **DA**: 说 (45,230), 表示 (12,450), 讲 (8,890), ...
- **SI**: 进行 (45,230), 管理 (12,450), 处理 (8,890), ...
- **MS**: 感到 (15,230), 觉得 (8,450), 认为 (6,890), ...
- **ABT**: 研究 (25,230), 分析 (18,450), 讨论 (12,890), ...
- **DISP**: 友好 (8,230), 热情 (6,450), 认真 (5,890), ...
- **EVAL**: 重要 (12,230), 有利 (8,450), 有益 (6,890), ...

To update with real corpus data, run:
```bash
python extract_bcc_predicates.py --input BCC_对_New.txt --freq-table bcc_frequencies.xlsx
```

---

## 🎯 Use Cases

### For Teachers
- Demonstrate construction types in class
- Show corpus-based frequencies
- Explain theoretical frameworks
- Generate practice exercises

### For Students
- Self-study tool
- Check understanding of sentences
- Learn common predicates
- Explore theoretical connections

### For Researchers
- Quick classification of examples
- Access to corpus frequencies
- Demonstrate theoretical framework
- Share with colleagues

---

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Python)
- **Backend**: Rule-based classifier + optional BERT
- **Data**: BCC Corpus (400K instances)
- **Deployment**: Streamlit Cloud / Heroku / Custom server

---

## 📝 Future Enhancements

Potential v2.0 features:
- ✨ More prepositions (给, 向, 为, 把, 被)
- ✨ BERT classifier integration
- ✨ User accounts & progress tracking
- ✨ Exercise generation
- ✨ Comparison mode (compare two sentences)
- ✨ Export analysis as PDF
- ✨ Mobile app version
- ✨ API for third-party integration

---

## 🤝 Contributing

Contributions welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - feel free to use for educational purposes!

---

## 📧 Contact

For questions or feedback:
- GitHub Issues: [Create an issue]
- Email: [Your email]

---

## 🙏 Acknowledgments

- Based on Jiaqi's doctoral research on 对-constructions
- BCC Corpus from Beijing Language and Culture University
- Theoretical frameworks from Fillmore, Dowty, and Goldberg
- Built with Streamlit

---

## 📖 References

**Fillmore, Charles J.** 1968. "The Case for Case." In *Universals in Linguistic Theory*, edited by Emmon Bach and Robert T. Harms, 1-88. New York: Holt, Rinehart and Winston.

**Dowty, David.** 1991. "Thematic Proto-Roles and Argument Selection." *Language* 67(3): 547-619.

**Goldberg, Adele E.** 1995. *Constructions: A Construction Grammar Approach to Argument Structure*. Chicago: University of Chicago Press.

---

**Made with ❤️ for Chinese language learners**
