# -*- coding: utf-8 -*-
"""
对-Construction Analyzer
==========================
A Streamlit web application for analyzing Chinese 对-constructions.

This educational tool helps learners and teachers understand:
- The six types of 对-constructions (DA, SI, MS, ABT, DISP, EVAL)
- Semantic roles (Fillmore and Dowty proto-roles)
- Classification reasoning
- Frequency data from the BCC corpus (394,355 instances)
"""

import streamlit as st
import json
import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import local modules
from utils.classifier import classify_sentence, get_classifier
from utils.predicate_extractor import extract_components
from utils.construction_info import (
    CONSTRUCTION_INFO, 
    MS_VS_ABT_DISTINCTION, 
    DECISION_TREE,
    get_construction_info
)

# Page configuration
st.set_page_config(
    page_title="对-Construction Analyzer",
    page_icon="🇨🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load frequency data
@st.cache_data
def load_frequency_data():
    """Load frequency data from JSON file."""
    data_path = Path(__file__).parent / "data" / "frequency_data.json"
    if data_path.exists():
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

FREQUENCY_DATA = load_frequency_data()

# Custom CSS
st.markdown("""
<style>
    .construction-box {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .da-box { background-color: #E8F5E9; border-left: 5px solid #4CAF50; }
    .si-box { background-color: #E3F2FD; border-left: 5px solid #2196F3; }
    .ms-box { background-color: #F3E5F5; border-left: 5px solid #9C27B0; }
    .abt-box { background-color: #FFF3E0; border-left: 5px solid #FF9800; }
    .disp-box { background-color: #FCE4EC; border-left: 5px solid #E91E63; }
    .eval-box { background-color: #EFEBE9; border-left: 5px solid #795548; }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    
    .highlight {
        background-color: #FFEB3B;
        padding: 2px 5px;
        border-radius: 3px;
    }
    
    .role-table {
        font-size: 14px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #f0f2f6;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application function."""
    
    # Sidebar
    with st.sidebar:
        st.title("🇨🇳 对-Construction Analyzer")
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["🔍 Analyze Sentence", "📚 Construction Guide", "📊 Corpus Statistics", "❓ MS vs ABT"]
        )
        
        st.markdown("---")
        st.markdown("""
        ### About
        This tool analyzes Chinese 对-constructions based on:
        - **394,355** annotated instances from the BCC corpus
        - **v70** hybrid classifier
        - Usage-Based Construction Grammar framework
        
        ### Construction Types
        - **DA**: Directed-Action
        - **SI**: Scoped-Intervention  
        - **MS**: Mental-State
        - **ABT**: Aboutness
        - **DISP**: Disposition
        - **EVAL**: Evaluation
        """)
    
    # Main content
    if page == "🔍 Analyze Sentence":
        show_analyzer_page()
    elif page == "📚 Construction Guide":
        show_guide_page()
    elif page == "📊 Corpus Statistics":
        show_statistics_page()
    elif page == "❓ MS vs ABT":
        show_ms_abt_page()


def show_analyzer_page():
    """Display the sentence analyzer page."""
    st.title("🔍 Analyze a 对-Construction")
    
    st.markdown("""
    Enter a Chinese sentence containing **对** to analyze its construction type.
    The analyzer will identify:
    - The construction type and its meaning
    - Semantic roles of X (subject) and Y (对-phrase)
    - Classification reasoning
    - Similar predicates from corpus data
    """)
    
    # Input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        sentence = st.text_input(
            "Enter sentence (with 对):",
            placeholder="例如: 他对我说了一番话。",
            help="Enter a Chinese sentence containing 对"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)
    
    # Example sentences
    st.markdown("#### 📝 Example Sentences")
    example_cols = st.columns(3)
    
    examples = [
        ("他对我说了一番话。", "DA - Speech act TO person"),
        ("警方对案件进行调查。", "SI - Intervention ON scope"),
        ("我对这个问题很了解。", "MS - Knowledge state"),
        ("专家对此发表意见。", "ABT - Discourse ABOUT topic"),
        ("她对客人很热情。", "DISP - Manner toward person"),
        ("吸烟对健康有害。", "EVAL - Harmful FOR health"),
    ]
    
    for i, (ex, desc) in enumerate(examples):
        with example_cols[i % 3]:
            if st.button(f"{ex[:10]}...", key=f"ex_{i}", help=desc):
                sentence = ex
                analyze_button = True
    
    # Analysis results
    if analyze_button and sentence:
        if '对' not in sentence:
            st.error("⚠️ Sentence must contain 对")
            return
        
        with st.spinner("Analyzing..."):
            # Extract components
            components = extract_components(sentence)
            
            # Classify
            result = classify_sentence(
                sentence,
                components.get('predicate', ''),
                components.get('pred_comp', ''),
                components.get('y_phrase', ''),
                components.get('y_anim', '')
            )
        
        # Display results
        st.markdown("---")
        
        # Construction type header
        label = result['label']
        info = get_construction_info(label)
        
        if info:
            # Main result card
            box_class = label.lower() + "-box"
            st.markdown(f"""
            <div class="construction-box {box_class}">
                <h2 style="color: {info['color']}; margin: 0;">
                    {label}: {info['name_en']} ({info['name_zh']})
                </h2>
                <p style="font-size: 18px; margin: 10px 0;">
                    {info['short_description']}
                </p>
                <p><strong>Confidence:</strong> {result['confidence']:.1%}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Analysis details
            st.markdown("### 📋 Analysis Details")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### Extracted Components")
                st.markdown(f"""
                - **Y (对-phrase):** {components.get('y_phrase', 'N/A')}
                - **Predicate:** {components.get('predicate', 'N/A')}
                - **Pred+Complement:** {components.get('pred_comp', 'N/A')}
                - **Y Animacy:** {components.get('y_anim', 'N/A')}
                """)
            
            with col2:
                st.markdown("#### 对's Meaning")
                st.markdown(f"""
                - **Meaning:** {info['dui_meaning']}
                - **Function:** {info['dui_function']}
                """)
            
            with col3:
                st.markdown("#### Classification Rule")
                st.info(result['reason'])
            
            # Semantic roles
            st.markdown("### 🎭 Semantic Roles")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Fillmore Case Roles")
                roles = info['semantic_roles']['fillmore']
                st.markdown(f"""
                | Role | Assignment |
                |------|------------|
                | **X (Subject)** | {roles['X']} |
                | **Y (对-phrase)** | {roles['Y']} |
                """)
            
            with col2:
                st.markdown("#### Dowty Proto-Roles")
                dowty = info['semantic_roles']['dowty']
                
                st.markdown("**X's Proto-Roles:**")
                for prop in dowty['X'].get('proto_agent', []):
                    st.markdown(f"- {prop}")
                
                st.markdown("**Y's Proto-Roles:**")
                for prop in dowty['Y'].get('proto_patient', []):
                    st.markdown(f"- {prop}")
            
            # Detailed explanation
            st.markdown("### 💡 Why This Classification?")
            st.markdown(result['explanation']['detailed_explanation'])
            
            # Top predicates for this type
            st.markdown("### 📊 Top 20 Predicates for This Construction")
            
            if FREQUENCY_DATA and label in FREQUENCY_DATA.get('top_predicates', {}):
                predicates = FREQUENCY_DATA['top_predicates'][label][:20]
                
                # Create DataFrame
                df = pd.DataFrame(predicates)
                
                # Bar chart
                fig = px.bar(
                    df, 
                    x='predicate', 
                    y='count',
                    text='percentage',
                    title=f"Top 20 Predicates in {label} ({info['name_en']})",
                    labels={'predicate': 'Predicate', 'count': 'Count'},
                    color_discrete_sequence=[info['color']]
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                
                # Table
                with st.expander("View Full Table"):
                    st.dataframe(
                        df,
                        column_config={
                            "predicate": "Predicate (谓语)",
                            "count": st.column_config.NumberColumn("Count", format="%d"),
                            "percentage": st.column_config.NumberColumn("Percentage", format="%.2f%%")
                        },
                        hide_index=True
                    )


def show_guide_page():
    """Display the construction guide page."""
    st.title("📚 对-Construction Guide")
    
    st.markdown("""
    This guide explains the six types of 对-constructions in Mandarin Chinese,
    based on the Usage-Based Construction Grammar framework.
    """)
    
    # Overview
    st.markdown("### Overview")
    
    if FREQUENCY_DATA:
        summary = FREQUENCY_DATA.get('summary', {})
        
        # Distribution chart
        labels = ['DA', 'SI', 'MS', 'ABT', 'DISP', 'EVAL']
        values = [summary.get(l, {}).get('instances', 0) for l in labels]
        colors = [CONSTRUCTION_INFO[l]['color'] for l in labels]
        
        fig = go.Figure(data=[go.Pie(
            labels=[f"{l} ({CONSTRUCTION_INFO[l]['name_en']})" for l in labels],
            values=values,
            marker_colors=colors,
            textinfo='percent+label',
            hole=0.3
        )])
        fig.update_layout(title="Distribution of 对-Constructions in BCC Corpus (394,355 instances)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Decision tree
    st.markdown("### 🌳 Decision Tree for Classification")
    st.code(DECISION_TREE, language=None)
    
    # Detailed guides for each type
    st.markdown("### 📖 Construction Types")
    
    tabs = st.tabs([f"{k} - {v['name_en']}" for k, v in CONSTRUCTION_INFO.items()])
    
    for i, (label, info) in enumerate(CONSTRUCTION_INFO.items()):
        with tabs[i]:
            # Header
            st.markdown(f"""
            <div class="construction-box {label.lower()}-box">
                <h2 style="color: {info['color']}; margin: 0;">
                    {label}: {info['name_en']} ({info['name_zh']})
                </h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Description
            st.markdown(info['full_description'])
            
            # Key characteristics
            st.markdown("#### Key Characteristics")
            for char in info['key_characteristics']:
                st.markdown(f"- {char}")
            
            # Typical patterns
            st.markdown("#### Typical Patterns")
            pattern_df = pd.DataFrame(
                info['typical_patterns'],
                columns=['Pattern', 'Example', 'Analysis']
            )
            st.dataframe(pattern_df, hide_index=True, use_container_width=True)
            
            # Semantic roles
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Fillmore Roles")
                roles = info['semantic_roles']['fillmore']
                st.markdown(f"- **X:** {roles['X']}")
                st.markdown(f"- **Y:** {roles['Y']}")
            
            with col2:
                st.markdown("#### Dowty Proto-Roles")
                dowty = info['semantic_roles']['dowty']
                st.markdown("**X (Proto-Agent):**")
                for prop in dowty['X'].get('proto_agent', []):
                    st.markdown(f"  - {prop}")
                st.markdown("**Y (Proto-Patient):**")
                for prop in dowty['Y'].get('proto_patient', []):
                    st.markdown(f"  - {prop}")
            
            # Example sentences
            st.markdown("#### Example Sentences")
            for ex in info['example_sentences']:
                st.markdown(f"""
                > **Chinese:** {ex['zh']}  
                > **English:** {ex['en']}  
                > **Analysis:** {ex['analysis']}
                """)


def show_statistics_page():
    """Display corpus statistics page."""
    st.title("📊 BCC Corpus Statistics")
    
    st.markdown("""
    Statistics from the annotated BCC corpus containing **394,355** instances 
    of 对-constructions, with **8,191** unique predicates.
    """)
    
    if not FREQUENCY_DATA:
        st.error("Frequency data not available.")
        return
    
    summary = FREQUENCY_DATA.get('summary', {})
    
    # Summary metrics
    st.markdown("### Overview")
    
    cols = st.columns(6)
    for i, label in enumerate(['DA', 'SI', 'MS', 'ABT', 'DISP', 'EVAL']):
        data = summary.get(label, {})
        with cols[i]:
            st.metric(
                label=f"{label}",
                value=f"{data.get('instances', 0):,}",
                delta=f"{data.get('percentage', 0):.1f}%"
            )
    
    # Distribution chart
    st.markdown("### Distribution by Construction Type")
    
    labels = ['DA', 'SI', 'MS', 'ABT', 'DISP', 'EVAL']
    instances = [summary.get(l, {}).get('instances', 0) for l in labels]
    unique_preds = [summary.get(l, {}).get('unique_predicates', 0) for l in labels]
    colors = [CONSTRUCTION_INFO[l]['color'] for l in labels]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Instances',
        x=labels,
        y=instances,
        marker_color=colors,
        text=instances,
        textposition='auto'
    ))
    fig.update_layout(
        title="Number of Instances by Construction Type",
        xaxis_title="Construction Type",
        yaxis_title="Count"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Unique predicates chart
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        name='Unique Predicates',
        x=labels,
        y=unique_preds,
        marker_color=colors,
        text=unique_preds,
        textposition='auto'
    ))
    fig2.update_layout(
        title="Number of Unique Predicates by Construction Type",
        xaxis_title="Construction Type",
        yaxis_title="Count"
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # Top predicates by type
    st.markdown("### Top Predicates by Type")
    
    type_select = st.selectbox(
        "Select Construction Type",
        options=['OVERALL'] + list(CONSTRUCTION_INFO.keys()),
        format_func=lambda x: f"{x} - {CONSTRUCTION_INFO[x]['name_en']}" if x in CONSTRUCTION_INFO else "Overall"
    )
    
    predicates = FREQUENCY_DATA.get('top_predicates', {}).get(type_select, [])
    
    if predicates:
        df = pd.DataFrame(predicates)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            color = CONSTRUCTION_INFO.get(type_select, {}).get('color', '#1f77b4')
            fig = px.bar(
                df,
                x='predicate',
                y='count',
                title=f"Top 20 Predicates in {type_select}",
                color_discrete_sequence=[color]
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(
                df,
                column_config={
                    "predicate": "谓语",
                    "count": st.column_config.NumberColumn("次数", format="%d"),
                    "percentage": st.column_config.NumberColumn("百分比", format="%.2f%%")
                },
                hide_index=True,
                height=400
            )


def show_ms_abt_page():
    """Display MS vs ABT distinction page."""
    st.title("❓ MS vs ABT: The Critical Distinction")
    
    st.markdown("""
    The distinction between **Mental-State (MS)** and **Aboutness (ABT)** is one of 
    the most important and challenging aspects of 对-construction classification.
    
    The key question to ask is:
    
    > **Does Y TRIGGER a psychological state IN X?**
    """)
    
    # Comparison table
    st.markdown("### Side-by-Side Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="construction-box ms-box">
            <h3 style="color: #9C27B0;">MS: Mental-State</h3>
            <p><strong>Y triggers internal state IN X</strong></p>
            <ul>
                <li>Internal psychological state</li>
                <li>Y is stimulus that triggers state</li>
                <li>NOT observable from outside</li>
                <li>State verbs (knowing, feeling)</li>
                <li>X has a state</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="construction-box abt-box">
            <h3 style="color: #FF9800;">ABT: Aboutness</h3>
            <p><strong>X produces discourse ABOUT Y</strong></p>
            <ul>
                <li>External discourse activity</li>
                <li>Y is topic of discourse</li>
                <li>Observable (speech/writing)</li>
                <li>Activity verbs (commenting, analyzing)</li>
                <li>X produces discourse</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature comparison table
    st.markdown("### Feature Comparison")
    
    comparison_df = pd.DataFrame(MS_VS_ABT_DISTINCTION['comparison'])
    st.dataframe(comparison_df, hide_index=True, use_container_width=True)
    
    # Examples
    st.markdown("### Example Comparisons")
    
    examples_df = pd.DataFrame(MS_VS_ABT_DISTINCTION['examples'])
    
    for _, row in examples_df.iterrows():
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            st.markdown(f"**{row['verb']}**")
        with col2:
            color = "#9C27B0" if row['type'] == 'MS' else "#FF9800"
            st.markdown(f"<span style='color: {color}; font-weight: bold;'>{row['type']}</span>", 
                       unsafe_allow_html=True)
        with col3:
            st.markdown(row['reason'])
    
    # Quick test
    st.markdown("### 🧪 Quick Self-Test")
    
    test_sentences = [
        ("我对他很了解。", "MS", "Y (他) triggers knowledge state IN X"),
        ("记者对事件进行分析。", "ABT", "X produces analytical discourse ABOUT Y"),
        ("她对结果感到满意。", "MS", "Y (结果) triggers satisfaction IN X"),
        ("专家对此不予置评。", "ABT", "X refuses to produce discourse ABOUT Y"),
        ("他对她充满信任。", "MS", "Y (她) triggers trust state IN X"),
    ]
    
    for i, (sent, correct, explanation) in enumerate(test_sentences):
        with st.expander(f"Test {i+1}: {sent}"):
            answer = st.radio(
                "What type is this?",
                ["MS", "ABT"],
                key=f"test_{i}",
                horizontal=True
            )
            
            if st.button("Check Answer", key=f"check_{i}"):
                if answer == correct:
                    st.success(f"✅ Correct! {explanation}")
                else:
                    st.error(f"❌ Incorrect. The answer is {correct}. {explanation}")


if __name__ == "__main__":
    main()
