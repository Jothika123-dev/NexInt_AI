"""
PDF to Text Extractor — Professional Streamlit App
Run: streamlit run app_streamlit.py
"""

import os
import io
import time
import fitz
import pdfplumber
from PIL import Image
import streamlit as st

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# ── Folder Setup ──────────────────────────────────────────────
for folder in ["uploads", "outputs", "extracted_images"]:
    os.makedirs(folder, exist_ok=True)

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="PDF Extractor Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# CUSTOM CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&display=swap');

/* ── Root & Base ── */
:root {
    --primary: #6C63FF;
    --primary-dark: #4B44CC;
    --accent: #FF6584;
    --success: #43D9AD;
    --warning: #FFB547;
    --bg-dark: #0F0F1A;
    --bg-card: #1A1A2E;
    --bg-card2: #16213E;
    --text-main: #FFFFFF;
    --text-sub: #D0D0E8;
    --border: rgba(108,99,255,0.2);
}

html, body, [class*="css"] {
    font-family: 'Times New Roman', Times, serif !important;
    background-color: var(--bg-dark);
    color: var(--text-main);
}

/* ── Hide Streamlit defaults ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem; }

/* ── Hero Banner ── */
.hero {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 3rem;
    text-align: center;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(ellipse at center, rgba(108,99,255,0.12) 0%, transparent 60%);
    pointer-events: none;
}
.hero h1 {
    font-family: 'Times New Roman', Times, serif;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6C63FF, #FF6584, #43D9AD);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.5rem 0;
}
.hero p {
    color: #FFFFFF;
    font-size: 1.1rem;
    margin: 0;
    font-family: 'Times New Roman', Times, serif;
}

/* ── Stat Cards ── */
.stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
}
.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.25rem;
    text-align: center;
    transition: transform 0.2s;
}
.stat-card:hover { transform: translateY(-4px); }
.stat-value {
    font-family: 'Times New Roman', Times, serif;
    font-size: 2rem;
    font-weight: 800;
    color: var(--primary);
    display: block;
}
.stat-label {
    font-size: 0.78rem;
    color: #FFFFFF;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-family: 'Times New Roman', Times, serif;
}

/* ── Section Headers ── */
.section-header {
    font-family: 'Times New Roman', Times, serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #FFFFFF;
    padding: 0.6rem 1rem;
    background: var(--bg-card);
    border-left: 4px solid var(--primary);
    border-radius: 0 8px 8px 0;
    margin: 1.5rem 0 1rem 0;
}

/* ── Upload Box ── */
.upload-zone {
    border: 2px dashed var(--primary);
    border-radius: 20px;
    padding: 2.5rem;
    text-align: center;
    background: rgba(108,99,255,0.04);
    margin-bottom: 1.5rem;
}
.upload-icon { font-size: 3rem; margin-bottom: 0.5rem; }
.upload-text { color: #FFFFFF; font-size: 0.95rem; font-family: 'Times New Roman', Times, serif; }

/* ── Badges ── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    margin: 0.2rem;
}
.badge-purple { background: rgba(108,99,255,0.2); color: #9D97FF; border: 1px solid rgba(108,99,255,0.3); }
.badge-green  { background: rgba(67,217,173,0.15); color: #43D9AD; border: 1px solid rgba(67,217,173,0.3); }
.badge-pink   { background: rgba(255,101,132,0.15); color: #FF6584; border: 1px solid rgba(255,101,132,0.3); }
.badge-yellow { background: rgba(255,181,71,0.15); color: #FFB547; border: 1px solid rgba(255,181,71,0.3); }

/* ── Preview Box ── */
.preview-box {
    background: var(--bg-card2);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    line-height: 1.7;
    color: #C8C8E0;
    max-height: 400px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── Info Boxes ── */
.info-box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin: 0.5rem 0;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.info-icon { font-size: 1.4rem; }
.info-text { font-size: 0.9rem; color: #FFFFFF; font-family: 'Times New Roman', Times, serif; }
.info-text strong { color: #FFFFFF; }

/* ── Progress Bar ── */
.stProgress > div > div { background: var(--primary) !important; border-radius: 99px; }

/* ── Streamlit Overrides ── */
.stButton > button {
    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.7rem 2rem;
    font-family: 'Times New Roman', Times, serif;
    font-weight: 700;
    font-size: 1rem;
    width: 100%;
    transition: all 0.2s;
    cursor: pointer;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(108,99,255,0.4);
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Times New Roman', Times, serif;
    font-weight: 600;
    color: #FFFFFF;
}
.stTabs [aria-selected="true"] { color: var(--primary) !important; }
.stTextArea textarea {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: #FFFFFF !important;
    font-family: 'Courier New', monospace !important;
}
div[data-testid="stFileUploader"] {
    background: rgba(108,99,255,0.04);
    border: 2px dashed rgba(108,99,255,0.4);
    border-radius: 16px;
    padding: 1rem;
}
.stSidebar { background: var(--bg-card) !important; }
.stSidebar .block-container { padding: 1.5rem; }

/* ── Sidebar all text white ── */
.stSidebar, .stSidebar * {
    color: #FFFFFF !important;
    font-family: 'Times New Roman', Times, serif !important;
}
.stSidebar .stCheckbox label {
    color: #FFFFFF !important;
    font-family: 'Times New Roman', Times, serif !important;
    font-size: 1rem !important;
}
.stSidebar h3 {
    color: #FFFFFF !important;
    font-family: 'Times New Roman', Times, serif !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: #FFFFFF !important;
    font-family: 'Times New Roman', Times, serif !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# EXTRACTION FUNCTIONS
# ══════════════════════════════════════════════════════════════

def inspect_pdf(pdf_path):
    doc          = fitz.open(pdf_path)
    total_pages  = doc.page_count
    total_images = sum(len(p.get_images()) for p in doc)
    has_text     = any(p.get_text().strip() for p in doc)
    total_tables = 0
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_tables()
            if t: total_tables += len(t)
    return {
        "total_pages" : total_pages,
        "total_images": total_images,
        "total_tables": total_tables,
        "has_text"    : has_text,
        "is_scanned"  : not has_text,
        "file_size_kb": round(os.path.getsize(pdf_path) / 1024, 1),
    }

def extract_text(pdf_path):
    doc  = fitz.open(pdf_path)
    text = ""
    for i, page in enumerate(doc):
        t = page.get_text("text")
        if t.strip():
            text += f"\n\n--- PAGE {i+1} ---\n{t}"
    return text

def extract_tables(pdf_path):
    result = ""
    with pdfplumber.open(pdf_path) as pdf:
        for pn, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            if not tables: continue
            for tn, table in enumerate(tables):
                result += f"\n\n[TABLE {tn+1} — PAGE {pn+1}]\n" + "-"*50 + "\n"
                for row in table:
                    result += " | ".join([str(c).strip() if c else "" for c in row]) + "\n"
                result += "-"*50
    return result

def extract_images_fn(pdf_path, base_name):
    doc   = fitz.open(pdf_path)
    log   = ""
    saved = []
    for pn, page in enumerate(doc):
        for ii, img in enumerate(page.get_images(full=True)):
            try:
                xref  = img[0]
                bimg  = doc.extract_image(xref)
                ext   = bimg["ext"]
                fname = f"{base_name}_p{pn+1}_i{ii+1}.{ext}"
                fpath = os.path.join("extracted_images", fname)
                with open(fpath, "wb") as f:
                    f.write(bimg["image"])
                pil   = Image.open(io.BytesIO(bimg["image"]))
                w, h  = pil.size
                log  += f"\n[Page {pn+1} | Img {ii+1}] {fname} — {w}×{h}px\n"
                saved.append({"path": fpath, "name": fname, "pil": pil, "page": pn+1})
            except: pass
    return log, saved

def extract_ocr(pdf_path):
    if not OCR_AVAILABLE: return ""
    doc = fitz.open(pdf_path)
    out = ""
    for i, page in enumerate(doc):
        mat = fitz.Matrix(300/72, 300/72)
        pix = page.get_pixmap(matrix=mat)
        pil = Image.open(io.BytesIO(pix.tobytes("png")))
        out += f"\n\n--- PAGE {i+1} (OCR) ---\n{pytesseract.image_to_string(pil)}"
    return out

def save_output(base_name, text, tables, image_log, ocr_text):
    path = os.path.join("outputs", f"{base_name}_extracted.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("="*60 + "\n  PDF EXTRACTION REPORT\n" + "="*60 + "\n")
        if text.strip():
            f.write("\n\n" + "="*60 + "\n  SECTION 1 — TEXT\n" + "="*60 + "\n" + text)
        if ocr_text.strip():
            f.write("\n\n" + "="*60 + "\n  SECTION 2 — OCR TEXT\n" + "="*60 + "\n" + ocr_text)
        if tables.strip():
            f.write("\n\n" + "="*60 + "\n  SECTION 3 — TABLES\n" + "="*60 + "\n" + tables)
        if image_log.strip():
            f.write("\n\n" + "="*60 + "\n  SECTION 4 — IMAGE LOG\n" + "="*60 + "\n" + image_log)
    return path


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0;'>
        <div style='font-size:2.5rem;'>📄</div>
        <div style='font-family:"Times New Roman",Times,serif; font-size:1.2rem; font-weight:800; color:#6C63FF;'>PDF Extractor Pro</div>
        <div style='font-size:0.75rem; color:#FFFFFF; margin-top:0.3rem; font-family:"Times New Roman",Times,serif;'>Version 2.0</div>
    </div>
    <hr style='border-color:rgba(108,99,255,0.2); margin: 1rem 0;'>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ Options")
    extract_text_opt   = st.checkbox("📝 Extract Text",   value=True)
    extract_table_opt  = st.checkbox("📊 Extract Tables", value=True)
    extract_image_opt  = st.checkbox("🖼️ Extract Images", value=True)
    use_ocr            = st.checkbox("🔍 OCR (Scanned PDFs)", value=True)

    st.markdown("<hr style='border-color:rgba(108,99,255,0.2);'>", unsafe_allow_html=True)
    st.markdown("### 📋 How to Use")
    st.markdown("""
    <div style='font-size:0.95rem; color:#FFFFFF; line-height:2; font-family:"Times New Roman",Times,serif;'>
    1. Upload your PDF file<br>
    2. Select extraction options<br>
    3. Click Extract button<br>
    4. Preview the results<br>
    5. Download output file
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(108,99,255,0.2);'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.85rem; color:#FFFFFF; text-align:center; font-family:"Times New Roman",Times,serif;'>
    Supports: Text · Tables · Images · OCR<br>
    Multi-column · Scanned PDFs
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# MAIN PAGE
# ══════════════════════════════════════════════════════════════

# Hero
st.markdown("""
<div class='hero'>
    <h1>📄 PDF Extractor Pro</h1>
    <p>Extract text, tables, and images from any PDF — including scanned documents</p>
</div>
""", unsafe_allow_html=True)

# Upload Section
st.markdown("<div class='section-header'>📤 Upload PDF</div>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

if uploaded_file:
    # File info badges
    size_kb = round(len(uploaded_file.getvalue()) / 1024, 1)
    st.markdown(f"""
    <div style='margin: 0.75rem 0;'>
        <span class='badge badge-purple'>📄 {uploaded_file.name}</span>
        <span class='badge badge-green'>💾 {size_kb} KB</span>
        <span class='badge badge-pink'>✅ Ready</span>
    </div>
    """, unsafe_allow_html=True)

    # Extract Button
    if st.button("🚀 Extract Now"):

        # Save PDF
        pdf_path  = os.path.join("uploads", uploaded_file.name)
        base_name = os.path.splitext(uploaded_file.name)[0]
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        # Progress
        prog  = st.progress(0)
        status = st.empty()

        start = time.time()

        status.markdown("🔍 **Inspecting PDF...**")
        info = inspect_pdf(pdf_path)
        prog.progress(15)

        text = ""
        if extract_text_opt:
            status.markdown("📝 **Extracting text...**")
            text = extract_text(pdf_path)
        prog.progress(35)

        tables = ""
        if extract_table_opt:
            status.markdown("📊 **Extracting tables...**")
            tables = extract_tables(pdf_path)
        prog.progress(55)

        image_log = ""
        saved_images = []
        if extract_image_opt:
            status.markdown("🖼️ **Extracting images...**")
            image_log, saved_images = extract_images_fn(pdf_path, base_name)
        prog.progress(75)

        ocr_text = ""
        if use_ocr and info["is_scanned"]:
            status.markdown("🔍 **Running OCR...**")
            ocr_text = extract_ocr(pdf_path)
        prog.progress(90)

        status.markdown("💾 **Saving output...**")
        output_path = save_output(base_name, text, tables, image_log, ocr_text)
        prog.progress(100)

        duration = round(time.time() - start, 2)
        status.empty()
        prog.empty()

        st.success(f"✅ Extraction complete in {duration} seconds!")

        # ── Stats ──
        st.markdown("<div class='section-header'>📊 Extraction Summary</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='stats-row'>
            <div class='stat-card'>
                <span class='stat-value'>{info['total_pages']}</span>
                <span class='stat-label'>Pages</span>
            </div>
            <div class='stat-card'>
                <span class='stat-value'>{len(text.split()) if text else 0}</span>
                <span class='stat-label'>Words</span>
            </div>
            <div class='stat-card'>
                <span class='stat-value'>{info['total_tables']}</span>
                <span class='stat-label'>Tables</span>
            </div>
            <div class='stat-card'>
                <span class='stat-value'>{info['total_images']}</span>
                <span class='stat-label'>Images</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Info Boxes ──
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class='info-box'>
                <span class='info-icon'>{'🔍' if info['is_scanned'] else '📝'}</span>
                <span class='info-text'>PDF Type: <strong>{'Scanned (OCR Used)' if info['is_scanned'] else 'Text-Based'}</strong></span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='info-box'>
                <span class='info-icon'>⏱️</span>
                <span class='info-text'>Processing Time: <strong>{duration}s</strong></span>
            </div>
            """, unsafe_allow_html=True)

        # ── Tabs ──
        st.markdown("<div class='section-header'>📋 Results</div>", unsafe_allow_html=True)
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Text", "📊 Tables", "🖼️ Images", "💾 Download"])

        with tab1:
            if text.strip():
                preview = text[:3000]
                st.markdown(f"<div class='preview-box'>{preview}{'...' if len(text)>3000 else ''}</div>", unsafe_allow_html=True)
            elif ocr_text.strip():
                st.markdown(f"<div class='preview-box'>{ocr_text[:3000]}</div>", unsafe_allow_html=True)
            else:
                st.info("No text extracted from this PDF.")

        with tab2:
            if tables.strip():
                st.markdown(f"<div class='preview-box'>{tables}</div>", unsafe_allow_html=True)
            else:
                st.info("No tables found in this PDF.")

        with tab3:
            if saved_images:
                cols = st.columns(3)
                for i, img_data in enumerate(saved_images):
                    with cols[i % 3]:
                        st.image(img_data["pil"], caption=f"Page {img_data['page']} — Image {i+1}", use_container_width=True)
            else:
                st.info("No images found in this PDF.")

        with tab4:
            st.markdown(f"""
            <div class='info-box' style='margin-bottom:1rem;'>
                <span class='info-icon'>📁</span>
                <span class='info-text'>Output file: <strong>{os.path.basename(output_path)}</strong></span>
            </div>
            """, unsafe_allow_html=True)
            with open(output_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download Extracted Text File",
                    data=f,
                    file_name=os.path.basename(output_path),
                    mime="text/plain",
                )

else:
    # Empty state
    st.markdown("""
    <div class='upload-zone'>
        <div class='upload-icon'>📂</div>
        <div style='font-family:Syne,sans-serif; font-size:1.2rem; font-weight:700; color:#E8E8F0; margin-bottom:0.5rem;'>
            Drop your PDF here
        </div>
        <div class='upload-text'>Supports text-based and scanned PDFs · Max 200MB</div>
    </div>
    """, unsafe_allow_html=True)

    # Feature Cards
    cols = st.columns(4)
    features = [
        ("📝", "Text Extraction", "Multi-column & reading order preserved"),
        ("📊", "Table Detection", "Rows & columns extracted accurately"),
        ("🖼️", "Image Saving",   "All embedded images saved as PNG"),
        ("🔍", "OCR Support",    "Scanned PDFs read via Tesseract"),
    ]
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(f"""
            <div class='stat-card' style='padding:1.5rem 1rem;'>
                <div style='font-size:2rem; margin-bottom:0.5rem;'>{icon}</div>
                <div style='font-family:"Times New Roman",Times,serif; font-weight:700; font-size:0.95rem; color:#FFFFFF; margin-bottom:0.4rem;'>{title}</div>
                <div style='font-size:0.85rem; color:#FFFFFF; font-family:"Times New Roman",Times,serif;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)