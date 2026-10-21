import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_document():
    doc = docx.Document()

    # Page setup - Standard Letter, 0.9-inch margins to guarantee 1 page
    sections = doc.sections
    for section in sections:
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(0.95)
        section.right_margin = Inches(0.95)
        
        # Header setup - subtle and clean
        header = section.header
        header.is_linked_to_previous = False
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("DaeMon Compute Grid — Project Abstract")
        hrun.font.name = "Arial"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(130, 130, 130)

    # Project Title
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(12)
    title_run = title_p.add_run("DaeMon: A Frictionless, Containerized Distributed Compute Grid for Volunteer Resource Aggregation")
    title_run.font.name = "Arial"
    title_run.font.size = Pt(15.5)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(18, 30, 49)

    # Stylish horizontal divider line
    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_before = Pt(0)
    p_line.paragraph_format.space_after = Pt(14)
    p_line_border = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="1" w:color="0052CC"/></w:pBdr>')
    p_line._p.get_or_add_pPr().append(p_line_border)

    # Abstract Heading
    abs_head_p = doc.add_paragraph()
    abs_head_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    abs_head_p.paragraph_format.space_before = Pt(0)
    abs_head_p.paragraph_format.space_after = Pt(6)
    abs_head_run = abs_head_p.add_run("ABSTRACT")
    abs_head_run.font.name = "Times New Roman"
    abs_head_run.font.size = Pt(11.5)
    abs_head_run.font.bold = True
    abs_head_run.font.color.rgb = RGBColor(20, 20, 20)

    # THE SINGLE PARAGRAPH ABSTRACT: Problem -> Solution -> How it works -> Stack
    # Strictly one single continuous paragraph containing all 4 components.
    abstract_text = (
        "Modern computational workloads—such as high-resolution artificial intelligence processing, cryptographic analysis, "
        "large-scale data transformations, and complex mathematical simulations—demand immense hardware resources, yet access to "
        "high-performance compute infrastructure remains severely constrained by the prohibitive financial expense, rigid vendor "
        "lock-in, and centralized architectural bottlenecks of commercial hyperscaler cloud platforms, while simultaneously billions "
        "of gigacycles of compute capacity sit completely dormant across personal workstations, laptops, and local enterprise edge devices. "
        "To resolve this systemic inefficiency and bridge the computational divide, DaeMon is engineered as a frictionless, containerized, "
        "volunteer-powered distributed compute grid that aggregates heterogeneous, idle hardware across networked environments to collaboratively "
        "execute massive polymorphic workloads at near-zero incremental infrastructure cost. The system operates through an active-push orchestration "
        "pipeline where administrators submit arbitrary computational tasks via an intuitive web dashboard to a centralized master orchestrator, "
        "which dynamically registers the job, executes domain-specific task-splitting algorithms to partition monolithic workloads into independent, "
        "atomic micro-tasks, and offloads heavy binary payloads directly to a dedicated distributed object storage cluster to ensure the message "
        "bus remains lightweight and responsive. Heterogeneous volunteer worker nodes, running as headless containerized background daemons across "
        "local or wide-area networks, establish connectivity, transmit high-frequency heartbeats, and receive targeted micro-task assignments pushed "
        "directly into dedicated asynchronous queues; upon assignment, each worker autonomously pulls its corresponding data slice from object storage, "
        "executes the specialized compute strategy within an isolated execution sandbox, uploads intermediate artifacts back to the storage cluster, "
        "and acknowledges completion. A fault-tolerant state aggregator continuously monitors node health, automatically redistributing stalled or "
        "orphaned tasks in the event of worker disconnection, intelligently reassembles and stitches finished micro-task artifacts into the final unified "
        "output, and broadcasts real-time telemetry, worker statistics, and job progress back to the user interface via persistent WebSocket channels. "
        "The end-to-end technology stack is constructed using Python with FastAPI for the high-performance asynchronous orchestrator and REST/WebSocket API "
        "engine, RabbitMQ as the enterprise message broker facilitating active task routing and worker queuing, Redis for real-time heartbeat caching and live "
        "worker registry management, MongoDB for flexible document persistence of polymorphic job metadata, MinIO for high-throughput self-hosted S3-compatible "
        "object storage, Docker for reproducible zero-configuration worker daemon containerization, and Next.js (React) paired with Tailwind CSS for the "
        "real-time monitoring and administrative command dashboard."
    )

    abs_p = doc.add_paragraph()
    abs_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    abs_p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    abs_p.paragraph_format.line_spacing = 1.18
    abs_p.paragraph_format.space_before = Pt(0)
    abs_p.paragraph_format.space_after = Pt(14)

    run_body = abs_p.add_run(abstract_text)
    run_body.font.name = "Times New Roman"
    run_body.font.size = Pt(10.5)
    run_body.font.color.rgb = RGBColor(35, 35, 35)

    # KEYWORDS (In a distinctly different font: Consolas)
    kw_p = doc.add_paragraph()
    kw_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    kw_p.paragraph_format.space_before = Pt(0)
    kw_p.paragraph_format.space_after = Pt(0)
    kw_p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    kw_p.paragraph_format.line_spacing = 1.15

    # Keywords label in distinct font
    kw_label = kw_p.add_run("Keywords: ")
    kw_label.font.name = "Consolas"
    kw_label.font.size = Pt(10)
    kw_label.font.bold = True
    kw_label.font.color.rgb = RGBColor(0, 82, 204) # Deep Blue accent

    # Keywords list in distinct font (Consolas)
    keywords_list = (
        "Distributed Computing; Volunteer Computing; Task Partitioning; Fault-Tolerant Orchestration; "
        "Active Push Scheduling; Micro-Tasks; Message Queuing; RabbitMQ; FastAPI; Docker Containerization; "
        "MinIO Object Storage; Redis Heartbeat Registry; MongoDB; WebSockets; Next.js; Polymorphic Workloads."
    )
    kw_run = kw_p.add_run(keywords_list)
    kw_run.font.name = "Consolas"
    kw_run.font.size = Pt(9.5)
    kw_run.font.italic = False
    kw_run.font.color.rgb = RGBColor(40, 50, 65)

    docx_path = os.path.abspath("DaeMon_Project_Abstract.docx")
    doc.save(docx_path)
    print(f"Word document saved to: {docx_path}")
    return docx_path

def convert_to_pdf(docx_path):
    import win32com.client
    pdf_path = os.path.splitext(docx_path)[0] + ".pdf"
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(docx_path)
        page_count = doc.ComputeStatistics(2) # 2 = wdStatisticPages
        print(f"Word document page count: {page_count}")
        # 17 = wdFormatPDF
        doc.SaveAs(pdf_path, FileFormat=17)
        doc.Close()
        print(f"PDF document saved to: {pdf_path}")
    finally:
        word.Quit()
    return pdf_path

if __name__ == "__main__":
    docx_file = create_document()
    convert_to_pdf(docx_file)
