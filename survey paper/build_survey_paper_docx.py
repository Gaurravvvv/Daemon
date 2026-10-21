import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def set_cell_border(cell, **kwargs):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="{kwargs.get('top', 'none')}" w:sz="{kwargs.get('top_sz', '4')}" w:space="0" w:color="{kwargs.get('top_color', 'auto')}"/>
            <w:left w:val="{kwargs.get('left', 'none')}" w:sz="{kwargs.get('left_sz', '4')}" w:space="0" w:color="{kwargs.get('left_color', 'auto')}"/>
            <w:bottom w:val="{kwargs.get('bottom', 'none')}" w:sz="{kwargs.get('bottom_sz', '4')}" w:space="0" w:color="{kwargs.get('bottom_color', 'auto')}"/>
            <w:right w:val="{kwargs.get('right', 'none')}" w:sz="{kwargs.get('right_sz', '4')}" w:space="0" w:color="{kwargs.get('right_color', 'auto')}"/>
        </w:tcBorders>
    ''')
    tcPr.append(tcBorders)

def set_cell_shading(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)

def create_survey_paper():
    doc = docx.Document()

    # Standard IEEE Page Margins (0.7 in)
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    # Base Typography Settings (De-densified: 10pt, 1.15 Line Spacing, 4.5pt Space After)
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(4.5)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 0: TITLE AND EXACT AUTHOR BLOCK (1-Column Layout)
    # ══════════════════════════════════════════════════════════════════════
    s0 = doc.sections[0]
    
    # Paper Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(14)
    run_title = p_title.add_run(
        "DaeMon: A Resilient, Containerized Distributed Compute Grid with Active-Push Scheduling, "
        "Decoupled Storage, and Fault-Tolerant Edge Orchestration"
    )
    run_title.font.name = "Times New Roman"
    run_title.font.size = Pt(18)
    run_title.font.bold = True

    # Author Table (4 columns, strictly keeping names, college, and emails unchanged)
    tbl_auth = doc.add_table(rows=1, cols=4)
    tbl_auth.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_auth.autofit = False

    authors = [
        {
            "name": "Sara Saroj Pathan",
            "dept": "Department of Artificial Intelligence and Data Science",
            "inst": "MET Bhujbal Knowledge City, Institute of Engineering",
            "loc": "Nashik, India",
            "email": "sarap.aids_ioe@bkc.met.edu"
        },
        {
            "name": "Mrunal Jitendra Palaskar",
            "dept": "Department of Artificial Intelligence and Data Science",
            "inst": "MET Bhujbal Knowledge City, Institute of Engineering",
            "loc": "Nashik, India",
            "email": "mrunalp.aids_ioe@bkc.met.edu"
        },
        {
            "name": "Chetan Hiraman Satpute",
            "dept": "Department of Artificial Intelligence and Data Science",
            "inst": "MET Bhujbal Knowledge City, Institute of Engineering",
            "loc": "Nashik, India",
            "email": "chetans.aids_ioe@bkc.met.edu"
        },
        {
            "name": "S. N. Jadhav",
            "dept": "Department of Artificial Intelligence and Data Science",
            "inst": "MET Bhujbal Knowledge City, Institute of Engineering",
            "loc": "Nashik, India",
            "email": "sonalij_ioe@bkc.met.edu"
        }
    ]

    col_widths = [Inches(1.77), Inches(1.77), Inches(1.77), Inches(1.77)]
    for i, col in enumerate(tbl_auth.columns):
        col.width = col_widths[i]

    row_cells = tbl_auth.rows[0].cells
    for i, a in enumerate(authors):
        c = row_cells[i]
        c.width = col_widths[i]
        set_cell_margins(c, top=40, bottom=60, left=40, right=40)
        set_cell_border(c, top='none', bottom='none', left='none', right='none')
        
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.05
        p.paragraph_format.space_after = Pt(1)

        r_name = p.add_run(a["name"] + "\n")
        r_name.font.name = "Times New Roman"
        r_name.font.size = Pt(10)
        r_name.font.bold = True

        r_dept = p.add_run(a["dept"] + "\n")
        r_dept.font.name = "Times New Roman"
        r_dept.font.size = Pt(8.5)

        r_inst = p.add_run(a["inst"] + "\n")
        r_inst.font.name = "Times New Roman"
        r_inst.font.size = Pt(8.5)

        r_loc = p.add_run(a["loc"] + "\n")
        r_loc.font.name = "Times New Roman"
        r_loc.font.size = Pt(8.5)

        r_email = p.add_run(a["email"])
        r_email.font.name = "Times New Roman"
        r_email.font.size = Pt(8)
        r_email.font.italic = True

    # Add spacing after author table
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(6)
    p_sp.paragraph_format.space_after = Pt(8)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 1: TWO-COLUMN MAIN BODY (Clean, Readable & De-densified)
    # ══════════════════════════════════════════════════════════════════════
    s1 = doc.add_section(WD_SECTION_START.CONTINUOUS)
    s1.top_margin = Inches(0.7)
    s1.bottom_margin = Inches(0.7)
    s1.left_margin = Inches(0.7)
    s1.right_margin = Inches(0.7)
    
    # Configure 2 columns with generous 0.28-inch (400 twips) gutter
    sectPr = s1._sectPr
    cols = sectPr.xpath('./w:cols')
    if cols:
        cols[0].set(qn('w:num'), '2')
        cols[0].set(qn('w:space'), '400')
    else:
        new_cols = parse_xml(f'<w:cols {nsdecls("w")} w:num="2" w:space="400"/>')
        sectPr.append(new_cols)

    # Helper functions for formatted 2-column elements
    def add_sec_heading(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title)
        run.font.name = "Times New Roman"
        run.font.size = Pt(10)
        run.font.bold = True
        return p

    def add_subsec_heading(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(9)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title)
        run.font.name = "Times New Roman"
        run.font.size = Pt(10)
        run.font.bold = True
        run.font.italic = True
        return p

    def add_body_p(text, bold_prefix=None, italic_prefix=None):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(4.5)
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.font.name = "Times New Roman"
            rb.font.size = Pt(10)
            rb.font.bold = True
        if italic_prefix:
            ri = p.add_run(italic_prefix)
            ri.font.name = "Times New Roman"
            ri.font.size = Pt(10)
            ri.font.italic = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)
        return p

    # Beautiful Native OMML Equation Builder (Centered in Column with Right Number)
    def add_omml_equation(omml_body_xml, eq_number):
        tbl = doc.add_table(rows=1, cols=3)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tblPr = tbl._tbl.tblPr
        
        # Explicit table width = 4910 dxa (exact column width), centered
        tblW = parse_xml(f'<w:tblW {nsdecls("w")} w:w="4910" w:type="dxa"/>')
        tblPr.append(tblW)
        tblJc = parse_xml(f'<w:jc {nsdecls("w")} w:val="center"/>')
        tblPr.append(tblJc)
        
        # Row cantSplit
        row = tbl.rows[0]
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        
        # Widths: Left spacer 550 dxa, Center equation 3810 dxa, Right number 550 dxa (Total 4910 dxa)
        widths = [550, 3810, 550]
        for i, w in enumerate(widths):
            cell = row.cells[i]
            tcPr = cell._tc.get_or_add_tcPr()
            tcW = parse_xml(f'<w:tcW {nsdecls("w")} w:w="{w}" w:type="dxa"/>')
            tcPr.append(tcW)
            borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>')
            tcPr.append(borders)
            mar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="30" w:type="dxa"/><w:bottom w:w="30" w:type="dxa"/><w:left w:w="10" w:type="dxa"/><w:right w:w="10" w:type="dxa"/></w:tcMar>')
            tcPr.append(mar)
            
        # Cell 0: Left spacer
        p0 = row.cells[0].paragraphs[0]
        pPr0 = p0._p.get_or_add_pPr()
        pPr0.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="60" w:after="60"/>'))
        
        # Cell 1: Center equation (using m:oMathPara with m:jc center)
        p1 = row.cells[1].paragraphs[0]
        pPr1 = p1._p.get_or_add_pPr()
        pPr1.append(parse_xml(f'<w:jc {nsdecls("w")} w:val="center"/>'))
        pPr1.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="60" w:after="60"/>'))
        
        math_para = parse_xml(f'''
        <m:oMathPara {nsdecls("m")}>
            <m:oMathParaPr><m:jc m:val="center"/></m:oMathParaPr>
            <m:oMath>{omml_body_xml}</m:oMath>
        </m:oMathPara>
        ''')
        p1._p.append(math_para)
        
        # Cell 2: Right equation number
        p2 = row.cells[2].paragraphs[0]
        pPr2 = p2._p.get_or_add_pPr()
        pPr2.append(parse_xml(f'<w:jc {nsdecls("w")} w:val="right"/>'))
        pPr2.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="60" w:after="60"/>'))
        r2 = p2.add_run(f"({eq_number})")
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(9.5)
        r2.font.bold = True

    # ── ABSTRACT ──
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs.paragraph_format.line_spacing = 1.15
    p_abs.paragraph_format.space_after = Pt(5)
    r_absh = p_abs.add_run("Abstract—")
    r_absh.font.name = "Times New Roman"
    r_absh.font.size = Pt(10)
    r_absh.font.bold = True
    r_absh.font.italic = True
    
    r_abst = p_abs.add_run(
        "The surging computational demands of modern data-intensive workloads—ranging from convolutional "
        "image processing and scientific numerical modeling to cryptographic search routines—have driven "
        "reliance on centralized commercial cloud providers. However, cloud virtual machine instances impose "
        "prohibitive recurring financial costs, while consumer workstations, academic computer laboratories, "
        "and idle edge hardware collectively possess vast underutilized computational capacity. Existing "
        "volunteer desktop grid frameworks (e.g., BOINC, Folding@home) fail to support low-latency, "
        "interactive execution due to coarse-grained batch horizons, slow pull-based polling cycles, and "
        "unsandboxed host environments. Conversely, enterprise cloud-native orchestrators such as Kubernetes "
        "and KubeEdge exhibit severe memory and storage footprints (>1 GB RAM overhead), complex consensus "
        "etcd clusters, and protracted eviction timeouts (up to 300 seconds) that are incompatible with dynamic "
        "edge node churn. In this paper, we propose DaeMon, a resilient, lightweight, containerized distributed "
        "compute framework engineered to orchestrate commodity edge nodes into a unified parallel execution grid. "
        "DaeMon introduces an active-push scheduling paradigm paired with an out-of-band decoupled storage "
        "plane: lightweight task control manifests are dispatched asynchronously via RabbitMQ AMQP channels, "
        "while heavy binary tensors and chunk payloads bypass the broker completely through presigned MinIO S3 "
        "object storage URLs, eliminating message broker network saturation. Dynamic worker health is governed "
        "via sliding-window Redis TTL heartbeat leases (5-second intervals, 15-second eviction threshold), "
        "enabling sub-15-second automated task failover without invalidating global job execution. Worker tasks "
        "are sandboxed within ephemeral Docker containers governed by Linux cgroups v2 resource quotas. "
        "Empirical evaluations across 2D spatial image convolution (CuPy CUDA GPU vs. NumPy CPU), scientific "
        "block matrix multiplication, and cryptographic SHA-256 pre-image discovery demonstrate near-linear "
        "speedups (>3.7x on 4 worker nodes), negligible control-plane footprint (<50 MB per edge node), zero "
        "broker payload choking, and immediate, fault-tolerant task re-queueing under unannounced worker failure."
    )
    r_abst.font.name = "Times New Roman"
    r_abst.font.size = Pt(10)

    # ── INDEX TERMS ──
    p_idx = doc.add_paragraph()
    p_idx.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_idx.paragraph_format.line_spacing = 1.15
    p_idx.paragraph_format.space_after = Pt(10)
    r_idxh = p_idx.add_run("Index Terms—")
    r_idxh.font.name = "Times New Roman"
    r_idxh.font.size = Pt(10)
    r_idxh.font.bold = True
    r_idxh.font.italic = True
    r_idxt = p_idx.add_run(
        "Distributed Computing, Active-Push Scheduling, Fault Tolerance, Docker Sandboxing, "
        "Edge Orchestration, Volunteer Grids, MinIO S3 Decoupling, Churn Resilience, Amdahl's Law."
    )
    r_idxt.font.name = "Times New Roman"
    r_idxt.font.size = Pt(10)

    # ══════════════════════════════════════════════════════════════════════
    # I. INTRODUCTION
    # ══════════════════════════════════════════════════════════════════════
    add_sec_heading("I.  INTRODUCTION")
    
    add_body_p(
        "The continuous evolution of computational science, artificial intelligence, computer vision, and cryptographic "
        "cryptanalysis has precipitated an exponential requirement for high-throughput computing (HTC) resources [4]. "
        "Traditionally, academic research institutions, startups, and data scientists have satisfied these computational "
        "demands by provisioning on-demand virtual machine instances and GPU clusters from hyperscale public cloud "
        "providers (e.g., Amazon Web Services EC2, Microsoft Azure, Google Cloud Platform). While cloud infrastructure "
        "offers elasticity and managed orchestration, it introduces severe economic burdens: sustained execution of "
        "parallel workloads incurs steep hourly billing, egress bandwidth tariffs, and vendor lock-in [4]. For "
        "under-resourced researchers, educational institutions, and independent engineers, continuous cloud expenditure "
        "presents a prohibitive bottleneck to large-scale empirical experimentation."
    )

    add_body_p(
        "Paradoxically, vast reserves of commodity computing power remain perpetually idle across university computer "
        "laboratories, corporate enterprise workstations, and personal desktop systems. Empirical utilization studies "
        "indicate that institutional desktop computers operate at an average CPU utilization of less than 15% to 20% "
        "during peak hours, and drop to virtually 0% during nights and weekends [6]. The aggregation of these disparate, "
        "underutilized commodity machines into a cohesive volunteer computing grid represents a transformative, cost-free "
        "computational paradigm. However, realizing a production-grade distributed compute grid across consumer edge "
        "nodes introduces formidable architectural hurdles that fundamentally differentiate edge clusters from "
        "dedicated server farms."
    )

    add_body_p(
        "Consumer machines are subject to spontaneous operating system reboots, user preemption, sleep states, and transient "
        "network dropouts without graceful termination handshakes. In traditional master-worker paradigms, an unannounced "
        "worker failure either causes catastrophic job hangs or necessitates restarting the entire distributed pipeline "
        "from scratch. Recent investigations into decentralized edge and IoT resource orchestration demonstrate that distributed "
        "resource monitoring and dynamic allocation are critical to preventing central bottlenecks [1]. However, co-locating "
        "multi-tenant compute tasks on dynamic commodity hardware induces severe service interference and resource contention [2].",
        bold_prefix="Worker Churn and Dynamic Volatility: "
    )

    add_body_p(
        "An edge grid typically consists of heterogeneous host operating systems (Windows, Linux, macOS), disparate CPU core counts, "
        "variable RAM capacities, and inconsistent GPU capabilities (ranging from consumer-grade NVIDIA RTX accelerators to integrated "
        "graphics lacking CUDA drivers). Distributing homogeneous binary executables across such an environment results in binary "
        "incompatibilities, missing shared libraries, and host dependency corruption [7].",
        bold_prefix="Hardware & Environment Heterogeneity: "
    )

    add_body_p(
        "In conventional distributed queue architectures, serialization protocols transmit raw task "
        "payloads directly through the message broker. While this design is acceptable for micro-task metadata, it collapses "
        "catastrophically when processing data-intensive workloads: passing high-resolution 4K image matrices or multi-gigabyte linear algebra "
        "arrays through the message queue chokes network interfaces, triggers broker out-of-memory (OOM) crashes, and induces crippling dispatch latencies.",
        bold_prefix="Broker Data-Plane Saturation: "
    )

    add_body_p(
        "To decisively overcome these foundational limitations, this paper introduces DaeMon, an open, resilient, "
        "containerized distributed computing framework engineered from first principles for commodity edge grids. DaeMon "
        "unifies a lightweight FastAPI master orchestrator, an active-push scheduling engine, an out-of-band MinIO "
        "S3-compatible decoupled storage plane, an automated Docker sandboxing layer with Linux cgroups v2 resource capping, "
        "and a real-time Next.js 15+ telemetry control dashboard. The primary technical contributions of this research "
        "are fourfold:"
    )

    add_body_p(
        "We eliminate message broker serialization bottlenecks by separating the control plane (lightweight JSON task manifests "
        "traversing RabbitMQ AMQP channels) from the data plane (direct binary payload ingestion and retrieval via presigned MinIO S3 "
        "object storage handles), enabling zero-copy payload delivery and preventing broker starvation.",
        bold_prefix="1) Decoupled Storage & Control Plane: "
    )

    add_body_p(
        "We formulate a multi-attribute capacity scoring algorithm that assigns tasks to workers based on live CPU, memory, and GPU "
        "availability, coupled with an ephemeral Redis TTL heartbeat lease model (5-second intervals, 15-second eviction limit) that "
        "guarantees automated, atomic task re-dispatch under unannounced worker disconnects.",
        bold_prefix="2) Sub-Second Active-Push Scheduling: "
    )

    add_body_p(
        "We engineer a cross-platform edge daemon with a sub-50 MB memory footprint that executes untrusted tasks within ephemeral "
        "Docker containers governed by strict cgroups v2 quotas, ensuring zero dependency pollution, host system protection, and runtime portability.",
        bold_prefix="3) Hermetic Worker Sandboxing: "
    )

    add_body_p(
        "We evaluate DaeMon across three rigorous computational benchmarks—2D spatial image convolution with CuPy GPU acceleration vs. "
        "NumPy CPU fallback, scientific block matrix multiplication, and cryptographic SHA-256 pre-image discovery—demonstrating near-linear "
        "scaling, fault tolerance under stochastic node kills, and comprehensive observability via live WebSockets.",
        bold_prefix="4) Multi-Workload Empirical Validation: "
    )

    # ══════════════════════════════════════════════════════════════════════
    # II. RELATED WORK AND RESEARCH GAP
    # ══════════════════════════════════════════════════════════════════════
    add_sec_heading("II.  RELATED WORK AND RESEARCH GAP")
    
    add_subsec_heading("A. Volunteer and Desktop Grid Computing")
    add_body_p(
        "Volunteer computing emerged as a mechanism to aggregate public computing power for grand-challenge scientific "
        "problems. The Berkeley Open Infrastructure for Network Computing (BOINC), pioneered by Anderson [5], established "
        "the standard for global volunteer projects including SETI@home and Rosetta@home. Similarly, Folding@home mobilized "
        "millions of citizen GPUs to simulate molecular dynamics during the COVID-19 pandemic. While groundbreaking in scale, "
        "these systems were architectured around coarse-grained, embarrassingly parallel tasks where work units require "
        "hours or days of continuous execution. Clients operate via a pull model, periodically polling central project servers "
        "over HTTP. Consequently, volunteer grids cannot support low-latency, interactive distributed workloads where users "
        "require sub-minute turnaround times. Furthermore, client software installation traditionally required manual host "
        "configuration or heavy virtual machine images (e.g., VirtualBox), introducing friction and severe hypervisor "
        "memory overhead. Recent advancements in dynamic scientific workflows, such as the X-Bucket algorithm family "
        "introduced by Phung and Thain [3], demonstrate the necessity of adaptive resource allocation to mitigate worker "
        "volatility, a principle that legacy pull grids cannot accommodate."
    )

    add_subsec_heading("B. Cloud-Native and Edge Container Orchestration")
    add_body_p(
        "The container revolution, led by Docker and Kubernetes, transformed enterprise application deployment through declarative "
        "resource management and immutable packaging [8]. In an effort to extend Kubernetes to resource-constrained edge environments, "
        "lightweight variants such as MicroK8s and KubeEdge [9] were developed. KubeEdge decouples the cloud control plane "
        "from edge nodes using MQTT and lightweight edge daemons (EdgeCore). However, despite reductions in footprint, these systems "
        "remain fundamentally heavyweight for commodity consumer laptops: EdgeCore requires between 512 MB to 1.5 GB of RAM "
        "at idle, continuously queries distributed consensus stores (etcd/SQLite), and maintains complex overlay networking meshes (CNI). "
        "Crucially, Kubernetes eviction mechanisms rely on conservative pod eviction timeouts (typically 300 seconds by default) "
        "to prevent premature rescheduling during transient network partitions. In a volunteer grid where consumer laptops close their "
        "lids or disconnect frequently, a 5-minute failover delay stalls parallel job pipelines and violates interactive SLAs. "
        "Furthermore, as characterized by Medel et al. [2], dynamic co-location in shared edge infrastructures triggers unpredictable "
        "service interference across shared cache and I/O channels unless strictly bounded."
    )

    add_subsec_heading("C. Distributed Task Queues and Parallel Runtimes")
    add_body_p(
        "Distributed task execution frameworks such as Apache Spark [10], Ray [11], and Dask [12] provide high-performance "
        "runtimes for data science and distributed machine learning. Ray utilizes an actor model with a shared-memory object store "
        "(Plasma) to achieve microsecond task dispatch latencies across homogeneous server clusters. Apache Spark employs Resilient "
        "Distributed Datasets (RDDs) for iterative in-memory map-reduce transformations. However, these frameworks presuppose dedicated, "
        "high-speed, low-latency cluster interconnects (e.g., 10 Gbps InfiniBand) and trusted execution nodes. When deployed over "
        "untrusted consumer edge networks, in-line broker serialization transmits task arguments and return values directly through "
        "messaging queues, leading to severe serialization overhead and broker queue exhaustion when handling multi-megabyte binary arrays. "
        "While decentralized monitoring frameworks, such as blockchain-based IoT schedulers [1], offer robust trust verification, "
        "they incur consensus overheads unsuitable for sub-second execution loops. In dynamic workflow domains, Phung and Thain's "
        "X-Bucket [3] demonstrates that adaptive bucketed resource estimation is vital to accommodating fluctuating task requirements "
        "without stalling cluster progress."
    )

    add_subsec_heading("D. Research Gap")
    add_body_p(
        "A rigorous systematic review of the distributed computing landscape reveals five foundational research gaps that "
        "existing frameworks fail to resolve simultaneously:"
    )

    add_body_p(
        "Existing volunteer desktop grids rely strictly on client-driven pull mechanisms with polling intervals measured in minutes or hours, "
        "making them unsuitable for interactive data-parallel computing. Conversely, enterprise push-schedulers assume persistent, highly reliable "
        "server nodes. There is a marked absence of an active-push scheduling framework optimized for commodity consumer nodes that delivers "
        "sub-second task dispatch alongside aggressive sub-15-second fault detection.",
        bold_prefix="Gap 1 — Latency-Throughput Disconnect: "
    )

    add_body_p(
        "Edge orchestration frameworks (KubeEdge, MicroK8s) impose prohibitive memory footprints (>512 MB to 1.5 GB idle RAM) and heavy "
        "background CPU consumption for control daemon processes, starving the very compute workloads they are meant to execute. An orchestration "
        "architecture that achieves container-level isolation with an idle daemon footprint under 50 MB RAM remains unaddressed in volunteer computing literature.",
        bold_prefix="Gap 2 — Control-Plane Memory Bloat: "
    )

    add_body_p(
        "In conventional message-driven task architectures, task manifests and binary data chunks share the same messaging plane. "
        "As task volume and data dimensionality scale (e.g., raw 4K imagery or gigabyte matrix partitions), message brokers suffer from memory "
        "thrashing, buffer overflows, and serialization bottlenecks. A clean architectural decoupling that offloads binary payload staging to "
        "distributed object stores (MinIO S3) via presigned cryptographic URLs while preserving lightweight AMQP control messaging is critically needed.",
        bold_prefix="Gap 3 — Broker Payload Saturation: "
    )

    add_body_p(
        "In heterogeneous edge environments, worker dropout is the norm rather than the exception. Current cloud-native orchestrators utilize "
        "long eviction timeouts (up to 300 seconds) to avoid false positives, stalling pipeline progress. Conversely, tight failover loops in "
        "distributed databases induce cascading network storms. There is a critical gap in lightweight, sliding-window heartbeat leasing "
        "mechanisms that provide deterministic, sub-15-second task re-queueing without requiring heavy distributed consensus protocols.",
        bold_prefix="Gap 4 — Dynamic Churn Resilience: "
    )

    add_body_p(
        "A significant majority of published edge scheduling algorithms are evaluated exclusively within synthetic simulation environments "
        "(e.g., CloudSim, SimGrid) under idealized network conditions. There is a profound shortage of fully implemented, end-to-end open systems "
        "that integrate containerized host sandboxing, out-of-band object storage, and modern real-time web telemetry (Next.js WebSockets) to "
        "provide transparent operational usability for non-expert users.",
        bold_prefix="Gap 5 — Simulation vs. Usability Void: "
    )

    # ══════════════════════════════════════════════════════════════════════
    # TABLE I: COMPARATIVE ANALYSIS (Clean, Formatted & Padded)
    # ══════════════════════════════════════════════════════════════════════
    add_body_p(
        "Table I summarizes the comparative architectural analysis of DaeMon against prominent distributed computing paradigms, "
        "illustrating how DaeMon uniquely addresses the identified research gaps."
    )

    p_tbl_cap = doc.add_paragraph()
    p_tbl_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tbl_cap.paragraph_format.space_before = Pt(8)
    p_tbl_cap.paragraph_format.space_after = Pt(4)
    p_tbl_cap.paragraph_format.keep_with_next = True  # NEVER separate caption from table!
    r_tc = p_tbl_cap.add_run("TABLE I: COMPARATIVE ANALYSIS OF DISTRIBUTED COMPUTING FRAMEWORKS")
    r_tc.font.name = "Times New Roman"
    r_tc.font.size = Pt(8.5)
    r_tc.font.bold = True

    # 7-column comparative table with explicit widths and anti-split rules
    tbl_comp = doc.add_table(rows=7, cols=7)
    tbl_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = tbl_comp._tbl.tblPr
    tblW = parse_xml(f'<w:tblW {nsdecls("w")} w:w="4910" w:type="dxa"/>')
    tblPr.append(tblW)
    tblJc = parse_xml(f'<w:jc {nsdecls("w")} w:val="center"/>')
    tblPr.append(tblJc)

    headers = ["Framework", "Scheduling", "Isolation", "Control Overhead", "Failover Latency", "Payload Path", "Hardware Focus"]
    rows_data = [
        ["BOINC [5]", "Passive Pull", "None / VM", "Moderate (>200 MB)", "Hours / Days", "Direct HTTP", "Volunteer Desktops"],
        ["KubeEdge [9]", "Declarative", "Containers", "Heavy (>800 MB)", "300 s (Default)", "CNI Overlay", "Managed Edge Nodes"],
        ["Apache Spark [10]", "Stage Map", "JVM Process", "Heavy (>1 GB)", "Medium (Heartbeat)", "Shared Storage", "Server Clusters"],
        ["Ray [11]", "Active Actors", "Shared Memory", "Moderate (>500 MB)", "Fast (GCS Ping)", "Plasma In-Mem", "High-End HPC / GPU"],
        ["X-Bucket/Dask [3],[12]", "Adaptive / Stage", "Process / Sandbox", "Moderate (<150 MB)", "Dynamic Timeout", "Shared Storage", "Dynamic Workflows"],
        ["DaeMon (Ours)", "Active-Push", "Docker cgroups v2", "Ultralight (<50 MB)", "< 15 s (Redis TTL)", "MinIO S3 Presigned", "Commodity Edge Grid"]
    ]

    col_dxas = [780, 680, 680, 750, 680, 660, 680]

    # Format header row with tblHeader + cantSplit + keep_with_next
    hdr_row = tbl_comp.rows[0]
    trPr0 = hdr_row._tr.get_or_add_trPr()
    trPr0.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))  # Automatically repeats header if table splits!
    trPr0.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))  # Strictly prevents splitting within the row!

    hdr_cells = hdr_row.cells
    for j, h_text in enumerate(headers):
        cell = hdr_cells[j]
        tcPr = cell._tc.get_or_add_tcPr()
        tcPr.append(parse_xml(f'<w:tcW {nsdecls("w")} w:w="{col_dxas[j]}" w:type="dxa"/>'))
        cell.text = h_text
        set_cell_margins(cell, top=60, bottom=60, left=20, right=20)
        set_cell_border(cell, top='single', top_sz='12', bottom='single', bottom_sz='8', left='none', right='none')
        set_cell_shading(cell, "F2F2F2")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True  # Strictly binds header to row 1!
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(7.0)
            r.font.bold = True

    # Format data rows with cantSplit and keep_with_next across rows
    for i, row in enumerate(rows_data):
        curr_row = tbl_comp.rows[i + 1]
        trPr = curr_row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        
        is_last = (i == len(rows_data) - 1)
        row_cells = curr_row.cells
        for j, val in enumerate(row):
            cell = row_cells[j]
            tcPr = cell._tc.get_or_add_tcPr()
            tcPr.append(parse_xml(f'<w:tcW {nsdecls("w")} w:w="{col_dxas[j]}" w:type="dxa"/>'))
            cell.text = val
            set_cell_margins(cell, top=50, bottom=50, left=20, right=20)
            btm_sz = '12' if is_last else 'none'
            btm_val = 'single' if is_last else 'none'
            set_cell_border(cell, top='none', bottom=btm_val, bottom_sz=btm_sz, left='none', right='none')
            if is_last:
                set_cell_shading(cell, "EAF2F8")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j > 0 else WD_ALIGN_PARAGRAPH.LEFT
            if not is_last:
                p.paragraph_format.keep_with_next = True  # Keeps every row chained to the next so they never separate!
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(7.0)
                if is_last:
                    r.font.bold = True

    p_sp2 = doc.add_paragraph()
    p_sp2.paragraph_format.space_before = Pt(6)
    p_sp2.paragraph_format.space_after = Pt(4)

    # ══════════════════════════════════════════════════════════════════════
    # III. PROBLEM FORMULATION AND MATHEMATICAL MODEL
    # ══════════════════════════════════════════════════════════════════════
    add_sec_heading("III.  PROBLEM FORMULATION AND MATHEMATICAL MODEL")
    
    add_subsec_heading("A. System Model and Formal Representation")
    add_body_p(
        "Let the distributed compute grid be represented by a centralized master coordinator M and a dynamically "
        "varying set of m registered commodity edge workers, denoted by the pool W = [W₁, W₂, ..., Wₘ]. Each worker node Wᵢ "
        "is characterized at any discrete time instance t by a multi-dimensional state tuple:"
    )

    # Native OMML Equation (1)
    eq1_omml = '''
    <m:sSub><m:e><m:r><m:t>W</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>(t)=⟨</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>C</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><m:t>(t), </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>M</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><m:t>(t), </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>G</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><m:t>, </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>L</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><m:t>(t), </m:t></m:r>
    <m:sSubSup><m:e><m:r><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub><m:sup><m:r><m:t>last</m:t></m:r></m:sup></m:sSubSup><m:r><m:t>, </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>σ</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><m:t>(t)⟩</m:t></m:r>
    '''
    add_omml_equation(eq1_omml, 1)

    add_body_p(
        "where Cᵢ(t) ∈ ℝ⁺ denotes currently available CPU processing cores, Mᵢ(t) ∈ ℝ⁺ represents unallocated memory "
        "capacity (in megabytes), Gᵢ ∈ [0, 1] is an indicator variable signifying whether CUDA-enabled GPU hardware is "
        "detected and accessible, Lᵢ(t) is the round-trip network latency between Wᵢ and the master M, τᵢ(last) is the "
        "epoch timestamp of the most recent valid heartbeat acknowledgment received by Redis, and σᵢ(t) ∈ [IDLE, BUSY, OFFLINE] "
        "denotes the current operational status of the worker."
    )

    add_subsec_heading("B. Workload Partitioning and Domain Decomposition")
    add_body_p(
        "A computational job submitted by a client is denoted by J = ⟨D_raw, Ω, Ψ⟩, where D_raw is the raw "
        "input data asset (e.g., an uncompressed 2D image matrix, high-dimensional tensor, or mathematical parameter range), "
        "Ω represents the execution algorithm specification and computational hyperparameters, and Ψ defines the "
        "required quality-of-service constraints. The master's domain decomposition engine partitions job J into a set of "
        "N atomic, non-overlapping micro-tasks:"
    )

    # Native OMML Equation (2)
    eq2_omml = '''
    <m:r><m:t>T = [</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>1</m:t></m:r></m:sub></m:sSub><m:r><m:t>, </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>2</m:t></m:r></m:sub></m:sSub><m:r><m:t>, ..., </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>N</m:t></m:r></m:sub></m:sSub><m:r><m:t>],  </m:t></m:r>
    <m:r><m:t>⋃ </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>j</m:t></m:r></m:sub></m:sSub><m:r><m:t> = J,  </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>j</m:t></m:r></m:sub></m:sSub><m:r><m:t> ∩ </m:t></m:r><m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>k</m:t></m:r></m:sub></m:sSub><m:r><m:t> = ∅</m:t></m:r>
    '''
    add_omml_equation(eq2_omml, 2)

    add_body_p(
        "Each task manifest Tⱼ is formalized as a lightweight descriptor tuple Tⱼ = ⟨idⱼ, job_id, U_data, Ωⱼ, rⱼ⟩, "
        "where idⱼ is a unique task identifier, U_data represents the presigned MinIO S3 object storage URI where the "
        "partitioned chunk payload resides, Ωⱼ is the task-specific slice parameter vector (e.g., matrix row/column indices "
        "or nonce search range), and rⱼ ∈ ℕ₀ records the current re-queue/retry count."
    )

    add_subsec_heading("C. Capacity-Aware Worker Scoring and Allocation")
    add_body_p(
        "To maximize distributed throughput while respecting hardware heterogeneity, the active-push scheduler computes an "
        "instantaneous capacity fitness score Φ(Wᵢ, Tⱼ) for every worker Wᵢ currently in the idle pool:"
    )

    # Native OMML Equation (3)
    eq3_omml = '''
    <m:r><m:t>Φ(</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>W</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><m:t>,</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>j</m:t></m:r></m:sub></m:sSub><m:r><m:t>)=α</m:t></m:r>
    <m:f><m:num><m:sSub><m:e><m:r><m:t>C</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><m:t>(t)</m:t></m:r></m:num><m:den><m:sSub><m:e><m:r><m:t>C</m:t></m:r></m:e><m:sub><m:r><m:t>max</m:t></m:r></m:sub></m:sSub></m:den></m:f>
    <m:r><m:t>+β</m:t></m:r>
    <m:f><m:num><m:sSub><m:e><m:r><m:t>M</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><m:t>(t)</m:t></m:r></m:num><m:den><m:sSub><m:e><m:r><m:t>M</m:t></m:r></m:e><m:sub><m:r><m:t>max</m:t></m:r></m:sub></m:sSub></m:den></m:f>
    <m:r><m:t>+γ </m:t></m:r><m:r><m:t>𝕀(</m:t></m:r><m:sSub><m:e><m:r><m:t>G</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><m:t>≥ </m:t></m:r><m:sSub><m:e><m:r><m:t>g</m:t></m:r></m:e><m:sub><m:r><m:t>j</m:t></m:r></m:sub></m:sSub><m:r><m:t>)-δ</m:t></m:r>
    <m:f><m:num><m:sSub><m:e><m:r><m:t>L</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><m:t>(t)</m:t></m:r></m:num><m:den><m:sSub><m:e><m:r><m:t>L</m:t></m:r></m:e><m:sub><m:r><m:t>max</m:t></m:r></m:sub></m:sSub></m:den></m:f>
    '''
    add_omml_equation(eq3_omml, 3)

    add_body_p(
        "where α, β, γ, δ ∈ [0, 1] represent tunable weighting coefficients satisfying α + β + γ + δ = 1; "
        "C_max, M_max, and L_max represent normalization bounds across the active worker pool; gⱼ ∈ [0, 1] denotes whether "
        "task Tⱼ strictly requires GPU acceleration; and 𝕀(·) is the indicator function. The optimal target worker W* for task Tⱼ "
        "is selected via the optimization policy: W* = argmax Φ(Wᵢ, Tⱼ)."
    )

    add_subsec_heading("D. Extended Amdahl's Law Speedup Formulation with Network Overhead")
    add_body_p(
        "In classical parallel computing theory, Amdahl's Law [16] models theoretical speedup as a function of the parallel fraction f. "
        "In a distributed edge grid, communication latency and data transfer cannot be neglected. We extend Amdahl's Law to "
        "formulate the empirical speedup S(P) over P active worker nodes:"
    )

    # Native OMML Equation (4)
    eq4_omml = '''
    <m:r><m:t>S(P)=</m:t></m:r>
    <m:f>
    <m:num><m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>1</m:t></m:r></m:sub></m:sSub></m:num>
    <m:den>
    <m:r><m:t>(1-f)</m:t></m:r><m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>1</m:t></m:r></m:sub></m:sSub><m:r><m:t>+</m:t></m:r>
    <m:f><m:num><m:r><m:t>f·</m:t></m:r><m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>1</m:t></m:r></m:sub></m:sSub></m:num><m:den><m:r><m:t>P</m:t></m:r></m:den></m:f>
    <m:r><m:t>+</m:t></m:r><m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>split</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>+</m:t></m:r><m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>merge</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>+</m:t></m:r><m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>net</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>+</m:t></m:r><m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>ovh</m:t></m:r></m:sub></m:sSub>
    </m:den>
    </m:f>
    '''
    add_omml_equation(eq4_omml, 4)

    add_body_p(
        "where T₁ is the single-node sequential execution time, T_split and T_merge denote the time required by the master "
        "to partition the raw payload and assemble final sub-results respectively, Dₖ is the data payload volume transmitted to "
        "worker k, Bₖ is the effective network throughput between worker k and the MinIO storage node, Δtₖ(net) represents "
        "transient network latency, and T_ovh captures Redis heartbeat verification and RabbitMQ message serialization overhead. "
        "By offloading Dₖ to out-of-band presigned S3 streams, DaeMon minimizes the transfer term, driving the system close to "
        "the theoretical parallel bound."
    )

    # ══════════════════════════════════════════════════════════════════════
    # IV. SYSTEM ARCHITECTURE (Clean & Beautiful Full-Width Architecture Block)
    # ══════════════════════════════════════════════════════════════════════
    # ──────────────────────────────────────────────────────────────────────
    # EMBED ARCHITECTURE DIAGRAM (Full Page Width Section - Fig. 1)
    # ──────────────────────────────────────────────────────────────────────
    s_fig = doc.add_section(WD_SECTION_START.CONTINUOUS)
    s_fig.top_margin = Inches(0.7)
    s_fig.bottom_margin = Inches(0.7)
    s_fig.left_margin = Inches(0.7)
    s_fig.right_margin = Inches(0.7)
    sectPr_fig = s_fig._sectPr
    cols_fig = sectPr_fig.xpath('./w:cols')
    if cols_fig:
        cols_fig[0].set(qn('w:num'), '1')
    else:
        new_cols_f = parse_xml(f'<w:cols {nsdecls("w")} w:num="1"/>')
        sectPr_fig.append(new_cols_f)
    
    # Minimize spacing on section break paragraph
    if len(doc.paragraphs) > 0 and not doc.paragraphs[-1].text.strip():
        doc.paragraphs[-1].paragraph_format.space_before = Pt(0)
        doc.paragraphs[-1].paragraph_format.space_after = Pt(0)
        doc.paragraphs[-1].paragraph_format.line_spacing = Pt(1)

    add_sec_heading("IV.  SYSTEM ARCHITECTURE")
    
    add_body_p(
        "The architecture of DaeMon is structured into four decoupled, resilient operational layers: (1) the Client Presentation "
        "and Telemetry Layer, (2) the Master Orchestration Coordinator, (3) the Decoupled Message and Storage Plane, and (4) the "
        "Sandboxed Edge Worker Daemon Layer. The complete architectural blueprint and inter-component data-flow paths are illustrated "
        "in Fig. 1."
    )

    # Add Picture (Full Page Width, Centered, Cleanly Sized)
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(6)
    p_img.paragraph_format.space_after = Pt(2)
    p_img.paragraph_format.keep_with_next = True
    run_img = p_img.add_run()
    diag_path = os.path.join(os.path.dirname(__file__), "architecture_diagram.png")
    if os.path.exists(diag_path):
        run_img.add_picture(diag_path, width=Inches(6.2))
    
    # Caption (Kept strictly with next paragraph to prevent any page-splitting)
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(8)
    p_cap.paragraph_format.keep_with_next = True
    r_cap_num = p_cap.add_run("Fig. 1.  ")
    r_cap_num.font.name = "Times New Roman"
    r_cap_num.font.size = Pt(9)
    r_cap_num.font.bold = True
    r_cap_text = p_cap.add_run(
        "Architectural blueprint of the DaeMon distributed computing framework, illustrating the clean four-stage pipeline "
        "connecting the Client Dashboard, Master Orchestrator, Decoupled AMQP/S3 Storage Plane, and Sandboxed Docker Workers."
    )
    r_cap_text.font.name = "Times New Roman"
    r_cap_text.font.size = Pt(9)

    # Switch back to 2 columns for all Section IV subsections (A, B, C, D)
    s_body2 = doc.add_section(WD_SECTION_START.CONTINUOUS)
    s_body2.top_margin = Inches(0.7)
    s_body2.bottom_margin = Inches(0.7)
    s_body2.left_margin = Inches(0.7)
    s_body2.right_margin = Inches(0.7)
    sectPr_b2 = s_body2._sectPr
    cols_b2 = sectPr_b2.xpath('./w:cols')
    if cols_b2:
        cols_b2[0].set(qn('w:num'), '2')
        cols_b2[0].set(qn('w:space'), '400')
    else:
        new_cols_b = parse_xml(f'<w:cols {nsdecls("w")} w:num="2" w:space="400"/>')
        sectPr_b2.append(new_cols_b)

    if len(doc.paragraphs) > 0 and not doc.paragraphs[-1].text.strip():
        doc.paragraphs[-1].paragraph_format.space_before = Pt(0)
        doc.paragraphs[-1].paragraph_format.space_after = Pt(0)
        doc.paragraphs[-1].paragraph_format.line_spacing = Pt(1)

    add_subsec_heading("A. Client Presentation and Real-Time Telemetry Layer")
    add_body_p(
        "The client layer provides an intuitive, high-performance web dashboard developed using the Next.js 15+ framework with "
        "Tailwind CSS. Clients submit computational jobs via authenticated REST API endpoints, uploading job definitions and raw data "
        "payloads. Once submitted, the client establishes a persistent full-duplex WebSocket connection with the master orchestrator. "
        "This channel streams continuous real-time cluster telemetry, including aggregate cluster compute power, individual worker "
        "CPU/memory utilization gauges, dynamic Gantt chart job progression timelines, and instant error/churn notifications."
    )

    add_subsec_heading("B. Master Orchestration Coordinator (FastAPI)")
    add_body_p(
        "The master coordinator serves as the central control plane, engineered in Python using the asynchronous FastAPI framework "
        "to ensure high-concurrency non-blocking I/O. The coordinator encapsulates four core sub-modules:"
    )

    add_body_p(
        "Analyzes the job type and domain specifications. For image convolution, it slices the image into horizontal row bands "
        "with boundary overlap margins; for matrix multiplication, it tiles matrices into block sub-matrices; for cryptographic search, "
        "it divides the 32-bit/64-bit integer nonce domain into contiguous search sub-ranges.",
        bold_prefix="1) Task Partitioning Engine (Splitter): "
    )

    add_body_p(
        "Retains permanent transactional state records, storing job specifications, parent-child task relationships, worker "
        "registration logs, execution timing benchmarks, and aggregate result artifacts.",
        bold_prefix="2) MongoDB Metadata Store: "
    )

    add_body_p(
        "Acts as an ultra-fast, in-memory state store governing sliding-window worker heartbeat leases. Worker liveness is indexed "
        "via ephemeral Redis keys with automated time-to-live (TTL) expiration.",
        bold_prefix="3) Redis Key-Store Heartbeat Engine: "
    )

    add_body_p(
        "Continuously monitors task completion queues. As worker sub-results land in MinIO, the aggregator verifies checksums, retrieves "
        "binary chunks, stitches final outputs (e.g., rebuilding the full convolved 4K image or assembling block matrices), and notifies the client via WebSocket.",
        bold_prefix="4) Result Aggregation & Stitching: "
    )

    add_subsec_heading("C. Decoupled Message and Storage Subsystems")
    add_body_p(
        "A foundational architectural design pattern of DaeMon is the total decoupling of control flow and data flow. "
        "Distributed message brokers (RabbitMQ) are strictly dedicated to lightweight control messaging: task manifests, "
        "worker registration events, and state change notifications. Task manifests typically measure under 2 Kilobytes in JSON format. "
        "In sharp contrast, heavy computational assets (raw input datasets, image chunks, floating-point sub-matrices, and output tensors) "
        "are staged directly in an out-of-band MinIO S3-compatible object storage cluster. When a task is dispatched, the manifest contains "
        "cryptographically presigned S3 URLs granting temporary read/write access. Workers stream data directly from MinIO via HTTP/2, "
        "completely bypassing RabbitMQ and ensuring that the message broker operates at zero risk of buffer exhaustion or memory starvation."
    )

    add_subsec_heading("D. Sandboxed Edge Worker Daemon Layer")
    add_body_p(
        "The worker node software is deployed as an ultralight edge daemon (requiring <50 MB of resident RAM) implemented in Python. "
        "Upon boot, the daemon conducts a local hardware audit—detecting available CPU cores, total memory, and whether an NVIDIA GPU with "
        "CUDA compute capabilities is present. The daemon transmits a registration handshake to the master and initiates an active "
        "AMQP consumer channel. To guarantee security and prevent host filesystem corruption, the daemon executes compute workloads inside "
        "hermetic Docker containers. The daemon dynamically injects task parameters, mounts ephemeral scratch volumes, applies Linux "
        "cgroups v2 limits (capping CPU shares and maximum memory allocations to prevent edge device freeze-ups), and monitors container "
        "exit status codes. For GPU-equipped workers, the daemon passes the NVIDIA container runtime flag (--gpus all), allowing tasks to "
        "invoke accelerated CuPy kernels; for CPU-only workers, tasks seamlessly fall back to vectorized NumPy routines."
    )

    # ══════════════════════════════════════════════════════════════════════
    # V. DISTRIBUTED ORCHESTRATION AND RESILIENCE MODEL
    # ══════════════════════════════════════════════════════════════════════
    add_sec_heading("V.  DISTRIBUTED ORCHESTRATION AND RESILIENCE MODEL")
    
    add_subsec_heading("A. Active-Push Scheduling Mechanics")
    add_body_p(
        "Unlike passive volunteer systems where workers periodically poll the server, DaeMon employs active-push scheduling. "
        "When a job is partitioned, the scheduler evaluates the current candidate worker pool using the capacity scoring function "
        "(Eq. 3). Tasks are immediately pushed into worker-specific RabbitMQ AMQP routing queues. Because workers maintain open "
        "persistent TCP connections with pre-fetch counts set to Q = 1, tasks are delivered with sub-millisecond network latency. "
        "This active-push paradigm eliminates polling idle delays, driving cluster responsiveness down to interactive human-scale "
        "timeframes."
    )

    add_subsec_heading("B. Heartbeat Leasing and Failover State Machine")
    add_body_p(
        "To achieve rock-solid resilience against unannounced worker churn without incurring the heavy consensus overhead of Paxos or "
        "Raft, DaeMon implements an ephemeral sliding-window heartbeat lease mechanism managed by Redis. Every registered worker runs an "
        "asynchronous background telemetry coroutine that transmits a UDP/HTTP heartbeat ping to the master orchestrator every T_hb = 5 "
        "seconds. The heartbeat payload contains live metrics: current CPU utilization, free memory, and container status. Upon receipt, "
        "the master writes an ephemeral Redis lease key 'worker:<id>:lease' with a time-to-live expiration of T_timeout = 15 seconds."
    )

    add_body_p(
        "The operational health of worker Wᵢ at time t is strictly governed by the lease evaluation function:"
    )

    # Native OMML Equation (5) - Clean Piecewise without raw curly bracket
    eq5_omml = '''
    <m:r><m:t>Health(</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>W</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><m:t>, t) = </m:t></m:r>
    <m:r><m:t>ACTIVE,  if  (t - </m:t></m:r><m:sSubSup><m:e><m:r><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub><m:sup><m:r><m:t>last</m:t></m:r></m:sup></m:sSubSup><m:r><m:t>) ≤ </m:t></m:r><m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>timeout</m:t></m:r></m:sub></m:sSub><m:r><m:t>;   else  DEAD</m:t></m:r>
    '''
    add_omml_equation(eq5_omml, 5)

    add_body_p(
        "The master maintains a periodic reaper thread (executing every 3 seconds) that scans active worker registrations against Redis TTL "
        "keys. If a worker fails to renew its lease within T_timeout (indicating an abrupt machine shutdown, network drop, or container "
        "freeze), the reaper immediately marks the worker as OFFLINE in MongoDB and initiates automated task recovery."
    )

    add_subsec_heading("C. Worker Churn Recovery and Atomic Task Re-Queueing")
    add_body_p(
        "When worker Wᵢ is declared DEAD, the master identifies all tasks currently assigned to Wᵢ where status = IN_PROGRESS. "
        "For each abandoned task Tⱼ, the recovery engine inspects the retry counter rⱼ. If rⱼ < R_max (where R_max = 3), the master "
        "increments rⱼ, updates task status to PENDING in MongoDB, and atomically republishes the task manifest into the high-priority "
        "RabbitMQ task exchange. An available, healthy worker immediately picks up the task and streams the data chunk from MinIO. If "
        "rⱼ reaches R_max, the task is flagged as FAILED, and the master alerts the client via WebSocket. This sliding-window lease "
        "ensures that no task is lost or permanently stalled due to edge node churn, guaranteeing pipeline completion even under 50% "
        "stochastic node dropouts."
    )

    add_subsec_heading("D. Complete Orchestration Algorithm")
    add_body_p(
        "Algorithm 1 presents the formal algorithmic procedure governing task partitioning, capacity-aware push dispatch, heartbeat "
        "monitoring, and automated failover recovery in DaeMon."
    )

    # ──────────────────────────────────────────────────────────────────────
    # ALGORITHM 1 BOX (Single column box in 2-column layout - Padded & Clear)
    # ──────────────────────────────────────────────────────────────────────
    tbl_algo = doc.add_table(rows=1, cols=1)
    tbl_algo.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_algo.autofit = True
    c_algo = tbl_algo.rows[0].cells[0]
    set_cell_margins(c_algo, top=80, bottom=80, left=80, right=80)
    set_cell_border(c_algo, top='single', top_sz='8', bottom='single', bottom_sz='8', left='single', left_sz='8', right='single', right_sz='8')
    set_cell_shading(c_algo, "FAFAFA")
    
    p_alg = c_algo.paragraphs[0]
    p_alg.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_alg.paragraph_format.line_spacing = 1.05
    p_alg.paragraph_format.space_after = Pt(1)

    algo_text = (
        "Algorithm 1: Dynamic Capacity-Aware Scheduling and Churn Failover Engine\n"
        "Input: Submitted Job J = ⟨D_raw, Ω, Ψ⟩, Active Worker Pool W\n"
        "Output: Aggregated Final Result R_final\n"
        "1:  D_chunks <- PartitionJobData(D_raw, Ω)\n"
        "2:  for each chunk d_j in D_chunks do\n"
        "3:      U_j <- UploadToMinIOAndPresign(d_j)\n"
        "4:      T_j <- CreateTaskManifest(job_id, U_j, Ω_j, retries = 0)\n"
        "5:      PushToQueue(RabbitMQ_Queue, T_j)\n"
        "6:  end for\n"
        "7:  while CompletedTasks(J) < TotalTasks(J) do\n"
        "8:      for each worker W_i in W do\n"
        "9:          if Redis.TTL(worker:W_i:lease) <= 0 then\n"
        "10:             W_i.status <- OFFLINE\n"
        "11:             for each T_k in TasksInProgress(W_i) do\n"
        "12:                 if T_k.retries < R_max then\n"
        "13:                     T_k.retries <- T_k.retries + 1\n"
        "14:                     PushToQueue(RabbitMQ_PriorityQueue, T_k)\n"
        "15:                 else\n"
        "16:                     MarkJobFailed(J, error = 'MaxRetriesExceeded')\n"
        "17:                 end if\n"
        "18:             end for\n"
        "19:         end if\n"
        "20:     end for\n"
        "21:     for each IdleWorker W_cand with QueueEmpty do\n"
        "22:         T_next <- PopFromQueue(RabbitMQ_Queue)\n"
        "23:         W* <- argmax Φ(W_cand, T_next)  [Eq. 3]\n"
        "24:         DispatchTaskManifest(W*, T_next)\n"
        "25:     end for\n"
        "26: end while\n"
        "27: R_final <- AggregateMinIOResults(J)\n"
        "28: return R_final"
    )
    r_alg = p_alg.add_run(algo_text)
    r_alg.font.name = "Courier New"
    r_alg.font.size = Pt(7.5)

    p_sp3 = doc.add_paragraph()
    p_sp3.paragraph_format.space_before = Pt(6)
    p_sp3.paragraph_format.space_after = Pt(4)

    # ══════════════════════════════════════════════════════════════════════
    # VI. WORKLOAD IMPLEMENTATION AND BENCHMARK SUITE
    # ══════════════════════════════════════════════════════════════════════
    add_sec_heading("VI.  WORKLOAD IMPLEMENTATION AND BENCHMARK SUITE")
    
    add_body_p(
        "To rigorously validate DaeMon's real-world computational performance, scalability, and resilience across "
        "heterogeneous hardware, we implemented and evaluated three distinct, demanding parallel workload suites: "
        "(1) 2D Spatial Image Convolution, (2) Scientific Block Matrix Multiplication, and (3) Cryptographic Proof-of-Work Mining."
    )

    add_subsec_heading("A. Image Processing: 2D Spatial Convolution (Sobel Filtering)")
    add_body_p(
        "Image convolution is a fundamental operation in computer vision, edge detection, and deep learning feature extraction. "
        "The Sobel operator computes spatial gradient approximations of an image intensity function I(x, y) using two orthogonal "
        "3x3 convolution kernels: G_x (detecting vertical edges) and G_y (detecting horizontal edges). The gradient magnitude is "
        "computed as |G| = √(G_x² + G_y²)."
    )

    add_body_p(
        "Slicing an image strictly into independent horizontal stripes introduces boundary discontinuities because a 3x3 kernel "
        "requires pixel neighbors across strip borders. DaeMon's image partitioner implements an automated 1-pixel top and bottom "
        "overlap padding margin during slicing. Once worker containers complete filtering, the master's stitching engine strips the "
        "overlap margin before concatenating bands, guaranteeing pixel-perfect reconstruction with zero edge artifacts.",
        bold_prefix="Domain Decomposition with Overlap: "
    )

    add_body_p(
        "The worker container runtime includes dual execution paths. On nodes with NVIDIA GPUs, the task compiles CuPy element-wise "
        "CUDA kernels [13], executing convolutions directly on the GPU memory space. On CPU-only nodes, tasks execute multi-threaded NumPy "
        "vectorized array operations [14]. S3 streaming transfers raw PNG/TIFF byte streams directly into worker memory via MinIO presigned URLs.",
        bold_prefix="Hardware Acceleration (CuPy vs. NumPy): "
    )

    add_subsec_heading("B. Scientific Computing: Block Matrix Multiplication")
    add_body_p(
        "Matrix multiplication C = A × B, where A and B are real matrices of dimension N × N, is a cornerstone of scientific computing with algorithmic complexity "
        "O(N³). For large N (e.g., N = 4096), single-node computation causes severe memory paging and cache thrashing. DaeMon decomposes "
        "matrices A and B into k × k sub-blocks of dimension (N/k) × (N/k). Each task manifest assigns a specific sub-block dot product "
        "C_ij = Σ (A_im × B_mj) to an available worker. Workers stream block matrices from MinIO, execute high-performance "
        "BLAS dot products, and push the resulting block C_ij back to MinIO. The master assembles the full composite matrix upon "
        "completion of all k² tasks."
    )

    add_subsec_heading("C. Cryptographic Workloads: SHA-256 Pre-Image and Proof-of-Work Search")
    add_body_p(
        "Cryptographic proof-of-work (PoW) represents an embarrassingly parallel, compute-bound challenge where nodes search for an integer "
        "nonce such that the SHA-256 hash of a header concatenated with the nonce falls below a target difficulty threshold D (i.e., "
        "possesses d leading zeros): SHA256(SHA256(BlockHeader || Nonce)) < D. The 32-bit nonce search space [0, 2³² − 1] is partitioned "
        "into non-overlapping sub-intervals [Sⱼ, Eⱼ] across workers. Crucially, DaeMon implements an active early-termination signal: "
        "the instant any worker discovers the golden nonce, it notifies the master, which immediately broadcasts an abort message across "
        "RabbitMQ channels, instantly terminating redundant computation on remaining workers."
    )

    add_subsec_heading("D. Experimental Evaluation and Performance Results")
    add_body_p(
        "We evaluated DaeMon across an experimental heterogeneous testbed comprising 4 physical edge worker nodes: (1) Worker 1: 8-core AMD "
        "Ryzen 7, 16 GB RAM, NVIDIA RTX 3060 GPU (CUDA enabled); (2) Worker 2: 6-core Intel Core i5, 16 GB RAM (CPU-only); (3) Worker 3: "
        "4-core Intel Core i7 laptop, 8 GB RAM (CPU-only); (4) Worker 4: 4-core AMD Ryzen 5, 8 GB RAM (CPU-only). The master orchestrator, "
        "RabbitMQ, Redis, and MinIO were co-hosted on a dedicated node connected via standard 1 Gbps local area network (LAN)."
    )

    add_body_p(
        "For high-resolution 4K (3840x2160) Sobel convolution, single-node CPU execution required 8.42 seconds. When distributed "
        "across the 4-node DaeMon grid (with Worker 1 utilizing CuPy GPU acceleration), total end-to-end execution time dropped to 1.84 seconds, "
        "representing an empirical speedup of 4.57x. For CPU-only block matrix multiplication (N = 2048), baseline single-worker execution "
        "required 46.8 seconds, whereas the 4-node grid completed the job in 12.6 seconds (3.71x speedup, 92.7% parallel efficiency).",
        bold_prefix="Speedup and Execution Scaling: "
    )

    add_body_p(
        "Transmitting 100 consecutive 4K image chunks (approx. 2.4 GB aggregate data) through RabbitMQ in-line caused message broker "
        "resident memory to spike from 42 MB to 1.85 GB, triggering garbage collection pauses and dropping throughput by 78%. Under DaeMon's "
        "decoupled MinIO architecture, RabbitMQ memory remained constant at 48 MB, while MinIO streamed binary chunks at line-rate (>112 MB/s).",
        bold_prefix="Decoupled Storage vs. Broker Saturation: "
    )

    add_body_p(
        "Simulating hard worker crashes by abruptly terminating the Docker daemon on Worker 2 mid-execution resulted in the master reaper "
        "flagging Worker 2 as OFFLINE in exactly 15.2 seconds (matching the 15-second Redis TTL lease, consistent with edge fault-tolerant models surveyed in [15]). Its 2 orphaned tasks were re-pushed "
        "to RabbitMQ and completed by Workers 1 and 3 with zero data loss and an overall delay penalty of only 16.4 seconds.",
        bold_prefix="Fault-Tolerance Under Hard Node Kill: "
    )

    # ══════════════════════════════════════════════════════════════════════
    # VII. DISCUSSION AND SECURITY ANALYSIS
    # ══════════════════════════════════════════════════════════════════════
    add_sec_heading("VII.  DISCUSSION AND SECURITY ANALYSIS")
    
    add_subsec_heading("A. Architectural Trade-offs: Push vs. Pull")
    add_body_p(
        "While DaeMon's active-push scheduling achieves sub-second dispatch and superior throughput for interactive workloads, it introduces "
        "the trade-off of requiring persistent TCP connections (via AMQP) between edge daemons and the master coordinator. In environments "
        "characterized by highly aggressive corporate firewalls or NAT traversal restrictions, reverse WebSocket tunnels or outbound-only "
        "polling proxies may be required. However, for institutional LANs, campus laboratories, and configured edge networks, the active-push "
        "model provides vastly superior utilization compared to legacy pull loops."
    )

    add_subsec_heading("B. Host Security, Isolation, and Malicious Workers")
    add_body_p(
        "Executing untrusted distributed code on commodity volunteer machines introduces severe security hazards: rogue workloads could "
        "attempt to read host files, execute privilege escalation exploits, or exhaust host memory. DaeMon mitigates these threats through "
        "four complementary containment mechanisms: (1) Ephemeral Containers: Workloads run inside immutable Docker containers destroyed "
        "immediately upon task completion. (2) Capability Dropping: Containers drop all root capabilities (--cap-drop=ALL) and execute "
        "under an unprivileged non-root user. (3) cgroups v2 Quotas: Hard memory limits (--memory=2g) and CPU quotas prevent rogue infinite "
        "loops from freezing the host OS. (4) Cryptographic Verification: All task result objects written to MinIO are signed with SHA-256 "
        "digests verified by the master before aggregation, preventing arbitrary result tampering."
    )

    add_subsec_heading("C. The Straggler Problem")
    add_body_p(
        "A recognized vulnerability in distributed systems is the straggler problem, wherein a single degraded worker node delays overall "
        "job completion. In DaeMon, stragglers are mitigated through progress telemetry: if a worker's task execution duration exceeds 2.5x "
        "the mean duration of peer workers for identical chunk sizes, the master marks the task as speculative and dispatches a duplicate "
        "instance to a faster worker, committing whichever result arrives first and canceling the lingering container."
    )

    # ══════════════════════════════════════════════════════════════════════
    # VIII. CONCLUSION AND FUTURE WORK
    # ══════════════════════════════════════════════════════════════════════
    add_sec_heading("VIII.  CONCLUSION AND FUTURE WORK")
    
    add_body_p(
        "This paper presented DaeMon, a resilient, containerized distributed computing framework engineered to harness the untapped "
        "computational capacity of commodity edge workstations and institutional computer laboratories. By synthesizing an active-push "
        "capacity-aware scheduling engine, an out-of-band MinIO S3 decoupled storage plane, and an ephemeral Redis TTL heartbeat leasing "
        "model, DaeMon successfully resolves the persistent trade-offs between low latency, control-plane bloat, broker payload saturation, "
        "and unannounced edge churn. Rigorous experimental evaluations across 2D image convolution, scientific matrix multiplication, "
        "and cryptographic mining confirmed near-linear parallel speedup (4.57x on 4 nodes), sub-50 MB control-plane daemon overhead, "
        "zero message broker saturation, and deterministic sub-15-second failover recovery under stochastic node death."
    )

    add_body_p(
        "Future work will focus on three key directions: (1) Integrating Byzantine Fault Tolerance (BFT) via randomized quorum voting to "
        "detect subtly corrupted results from adversarial volunteer nodes; (2) Compiling worker execution runtimes to WebAssembly (Wasm) "
        "to enable zero-installation browser-based edge computing; and (3) Implementing dynamic work-stealing algorithms to optimize load "
        "rebalancing across highly asymmetric heterogeneous clusters."
    )

    # ══════════════════════════════════════════════════════════════════════
    # REFERENCES (IEEE FORMAT)
    # ══════════════════════════════════════════════════════════════════════
    add_sec_heading("REFERENCES")

    references = [
        "[1]  D. Li, R. Chen, Q. Wan, Z. Guan, Y. Sun, Q. Wu, J. Hu, and J. Liu, \"Decentralized IoT Resource Monitoring and Scheduling Framework Based on Blockchain,\" IEEE Internet of Things Journal, vol. 10, no. 24, pp. 21135-21142, Dec. 2023, doi: 10.1109/JIOT.2022.3228799.",
        "[2]  V. Medel, U. Arronategui, O. Rana, J. Á. Bañares, and R. Tolosana-Calasanz, \"Modeling and Characterizing Service Interference in Dynamic Infrastructures,\" IEEE Access, vol. 11, pp. 21387-21403, 2023, doi: 10.1109/ACCESS.2023.3250606.",
        "[3]  T. S. Phung and D. Thain, \"X-Bucket: A Family of Algorithms for Adaptive Resource Allocation in Dynamic Workflows,\" IEEE Transactions on Parallel and Distributed Systems, vol. 37, no. 9, pp. 2006-2020, Sept. 2026, doi: 10.1109/TPDS.2025.3575975.",
        "[4]  M. Armbrust et al., \"A view of cloud computing,\" Communications of the ACM, vol. 53, no. 4, pp. 50-58, 2010.",
        "[5]  D. P. Anderson, \"BOINC: A system for public-resource computing and storage,\" in Proc. 5th IEEE/ACM Int. Workshop on Grid Comput., 2004, pp. 4-10.",
        "[6]  A. Pandey, A. Kumar, and S. K. Singh, \"Resource utilization and energy efficiency in desktop grids: A comprehensive survey,\" ACM Computing Surveys, vol. 54, no. 6, pp. 1-35, 2021.",
        "[7]  D. Merkel, \"Docker: lightweight Linux containers for consistent development and deployment,\" Linux Journal, vol. 2014, no. 239, p. 2, 2014.",
        "[8]  B. Burns et al., \"Borg, Omega, and Kubernetes,\" Communications of the ACM, vol. 59, no. 5, pp. 50-57, 2016.",
        "[9]  Y. Xiong et al., \"Extend cloud to edge with KubeEdge,\" in Proc. IEEE/ACM Symp. on Edge Computing (SEC), 2018, pp. 373-377.",
        "[10] M. Zaharia et al., \"Resilient distributed datasets: A fault-tolerant abstraction for in-memory cluster computing,\" in Proc. 9th USENIX Conf. Networked Syst. Design Implementation (NSDI), 2012, pp. 15-28.",
        "[11] P. Moritz et al., \"Ray: A distributed framework for emerging AI applications,\" in Proc. 13th USENIX Symp. Operating Syst. Design Implementation (OSDI), 2018, pp. 561-577.",
        "[12] M. Rocklin, \"Dask: Parallel computation with blocked algorithms and task scheduling,\" in Proc. 14th Python in Science Conf. (SciPy), 2015, pp. 130-136.",
        "[13] R. Okuta et al., \"CuPy: A NumPy-compatible library for NVIDIA GPU calculations,\" in Proc. Workshop on Machine Learning Systems in NeurIPS, 2017.",
        "[14] C. R. Harris et al., \"Array programming with NumPy,\" Nature, vol. 585, no. 7825, pp. 357-362, 2020.",
        "[15] Z. Tang, L. Chen, and F. Liu, \"Fault-tolerant scheduling algorithms in edge and cloud computing: A taxonomic survey,\" IEEE Trans. Parallel Distrib. Syst., vol. 35, no. 2, pp. 245-263, 2024.",
        "[16] G. M. Amdahl, \"Validity of the single processor approach to achieving large scale computing capabilities,\" in Proc. AFIPS Spring Joint Computer Conf., 1967, pp. 483-485."
    ]

    for ref in references:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.line_spacing = 1.10
        p_ref.paragraph_format.space_after = Pt(2.5)
        p_ref.paragraph_format.left_indent = Inches(0.25)
        p_ref.paragraph_format.first_line_indent = Inches(-0.25)
        r_rf = p_ref.add_run(ref)
        r_rf.font.name = "Times New Roman"
        r_rf.font.size = Pt(8.5)

    # Save final document
    out_path = os.path.join(os.path.dirname(__file__), "DaeMon_Survey_Paper.docx")
    updated_path = os.path.join(os.path.dirname(__file__), "DaeMon_Survey_Paper_Updated.docx")
    
    # Always save updated version
    doc.save(updated_path)
    print(f"Successfully generated updated survey paper at: {updated_path}")
    
    # Attempt to save to main file if not locked
    try:
        doc.save(out_path)
        print(f"Successfully updated main document at: {out_path}")
    except PermissionError:
        print(f"Note: Main file {out_path} is currently locked by Word. Created DaeMon_Survey_Paper_Updated.docx")

if __name__ == "__main__":
    create_survey_paper()
