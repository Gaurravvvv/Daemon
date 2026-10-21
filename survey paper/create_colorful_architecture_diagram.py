import os
import math
from PIL import Image, ImageDraw, ImageFont

def generate_clean_simplified_architecture_diagram():
    # Beautiful, balanced canvas (2700 x 1320 px)
    W, H = 2700, 1320
    img = Image.new("RGB", (W, H), "#F8FAFC")
    draw = ImageDraw.Draw(img)

    # ──────────────────────────────────────────────────────────────────────
    # TYPOGRAPHY
    # ──────────────────────────────────────────────────────────────────────
    font_dir = "C:\\Windows\\Fonts"
    f_title = ImageFont.truetype(os.path.join(font_dir, "segoeuib.ttf"), 44)
    f_subtitle = ImageFont.truetype(os.path.join(font_dir, "segoeui.ttf"), 22)
    
    f_tier_hdr = ImageFont.truetype(os.path.join(font_dir, "segoeuib.ttf"), 24)
    f_tier_sub = ImageFont.truetype(os.path.join(font_dir, "segoeui.ttf"), 17)
    
    f_card_hdr = ImageFont.truetype(os.path.join(font_dir, "segoeuib.ttf"), 20)
    f_card_sub = ImageFont.truetype(os.path.join(font_dir, "segoeuib.ttf"), 16)
    f_pill_txt = ImageFont.truetype(os.path.join(font_dir, "segoeui.ttf"), 15)
    
    f_arrow_num = ImageFont.truetype(os.path.join(font_dir, "segoeuib.ttf"), 15)
    f_arrow_sub = ImageFont.truetype(os.path.join(font_dir, "segoeui.ttf"), 13)

    # ──────────────────────────────────────────────────────────────────────
    # COLOR PALETTE
    # ──────────────────────────────────────────────────────────────────────
    c_dark = "#0F172A"
    c_white = "#FFFFFF"

    # Tier 1: Client (Sky Blue)
    t1_bg = "#F0F9FF"
    t1_border = "#0284C7"
    t1_hdr = "#0369A1"

    # Tier 2: Master Control (Indigo)
    t2_bg = "#F5F3FF"
    t2_border = "#6366F1"
    t2_hdr = "#4338CA"

    # Tier 3: Storage & Broker (Warm Amber / Teal)
    t3_bg = "#FFFBEB"
    t3_border = "#D97706"
    t3_hdr = "#B45309"

    # Tier 4: Edge Worker Grid (Emerald)
    t4_bg = "#ECFDF5"
    t4_border = "#059669"
    t4_hdr = "#047857"

    # ──────────────────────────────────────────────────────────────────────
    # DRAWING HELPERS
    # ──────────────────────────────────────────────────────────────────────
    def draw_card(box, fill_color, border_color, radius=16, width=3):
        x1, y1, x2, y2 = box
        draw.rounded_rectangle((x1, y1, x2, y2), radius=radius, fill=fill_color, outline=border_color, width=width)

    def draw_badge(cx, cy, text, bg_color, text_color=c_white, font=f_arrow_num, px=14, py=5, border=None):
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x1 = cx - tw // 2 - px
        y1 = cy - th // 2 - py
        x2 = cx + tw // 2 + px
        y2 = cy + th // 2 + py
        if border:
            draw.rounded_rectangle((x1, y1, x2, y2), radius=8, fill=bg_color, outline=border, width=2)
        else:
            draw.rounded_rectangle((x1, y1, x2, y2), radius=8, fill=bg_color)
        draw.text((cx, cy), text, font=font, fill=text_color, anchor="mm")

    def draw_arrow(start_pt, end_pt, color, width=4, head_size=15, bidirectional=False):
        x1, y1 = start_pt
        x2, y2 = end_pt
        draw.line([start_pt, end_pt], fill=color, width=width)
        
        # End arrowhead
        angle = math.atan2(y2 - y1, x2 - x1)
        p1 = (x2 - head_size * math.cos(angle - math.pi / 6), y2 - head_size * math.sin(angle - math.pi / 6))
        p2 = (x2 - head_size * math.cos(angle + math.pi / 6), y2 - head_size * math.sin(angle + math.pi / 6))
        draw.polygon([end_pt, p1, p2], fill=color)

        if bidirectional:
            p3 = (x1 + head_size * math.cos(angle - math.pi / 6), y1 + head_size * math.sin(angle - math.pi / 6))
            p4 = (x1 + head_size * math.cos(angle + math.pi / 6), y1 + head_size * math.sin(angle + math.pi / 6))
            draw.polygon([start_pt, p3, p4], fill=color)

    # ──────────────────────────────────────────────────────────────────────
    # TOP TITLE
    # ──────────────────────────────────────────────────────────────────────
    draw.text((W // 2, 52), "DaeMon: Distributed Autonomous Edge Matrix Orchestration Network", font=f_title, fill=c_dark, anchor="mm")
    draw_badge(W // 2, 98, "High-Level Distributed System Architecture", "#1E293B", c_white, f_subtitle, px=22, py=5)

    # ──────────────────────────────────────────────────────────────────────
    # 4 EQUAL-HEIGHT COLUMNS (Spacious, Perfectly Aligned)
    # ──────────────────────────────────────────────────────────────────────
    y_top = 150
    y_bot = 1260

    t1_x1, t1_x2 = 60, 540        # Width 480
    # Corridor 1: 540 to 710 (170 px)
    t2_x1, t2_x2 = 710, 1310      # Width 600
    # Corridor 2: 1310 to 1480 (170 px)
    t3_x1, t3_x2 = 1480, 2060     # Width 580
    # Corridor 3: 2060 to 2230 (170 px)
    t4_x1, t4_x2 = 2230, 2640     # Width 410

    # Draw Column Containers
    draw_card((t1_x1, y_top, t1_x2, y_bot), t1_bg, t1_border, radius=18)
    draw_card((t2_x1, y_top, t2_x2, y_bot), t2_bg, t2_border, radius=18)
    draw_card((t3_x1, y_top, t3_x2, y_bot), t3_bg, t3_border, radius=18)
    draw_card((t4_x1, y_top, t4_x2, y_bot), t4_bg, t4_border, radius=18)

    # Column Headers
    draw_badge((t1_x1 + t1_x2) // 2, y_top + 38, "1. Client Layer", t1_hdr, c_white, f_tier_hdr, px=20, py=7)
    draw.text(((t1_x1 + t1_x2) // 2, y_top + 76), "Web & API Access", font=f_tier_sub, fill=t1_hdr, anchor="mm")

    draw_badge((t2_x1 + t2_x2) // 2, y_top + 38, "2. Master Orchestrator", t2_hdr, c_white, f_tier_hdr, px=20, py=7)
    draw.text(((t2_x1 + t2_x2) // 2, y_top + 76), "FastAPI Control Plane", font=f_tier_sub, fill=t2_hdr, anchor="mm")

    draw_badge((t3_x1 + t3_x2) // 2, y_top + 38, "3. Transport & Storage", t3_hdr, c_white, f_tier_hdr, px=20, py=7)
    draw.text(((t3_x1 + t3_x2) // 2, y_top + 76), "Decoupled Data Plane", font=f_tier_sub, fill=t3_hdr, anchor="mm")

    draw_badge((t4_x1 + t4_x2) // 2, y_top + 38, "4. Edge Worker Grid", t4_hdr, c_white, f_tier_hdr, px=20, py=7)
    draw.text(((t4_x1 + t4_x2) // 2, y_top + 76), "Heterogeneous Nodes", font=f_tier_sub, fill=t4_hdr, anchor="mm")

    # ──────────────────────────────────────────────────────────────────────
    # 1. CLIENT LAYER BLOCKS
    # ──────────────────────────────────────────────────────────────────────
    w1 = 400
    x1 = (t1_x1 + t1_x2 - w1) // 2

    c_cards = [
        (
            240, 270,
            "Next.js Dashboard",
            "#0284C7", "#F0F9FF", "#BAE6FD",
            "Real-Time Web UI",
            [("Real-Time Telemetry", "#0369A1"), ("Dynamic Gantt Chart", "#0369A1")]
        ),
        (
            540, 270,
            "REST API Client",
            "#2563EB", "#EFF6FF", "#BFDBFE",
            "Job Submission",
            [("Job Parameter Form", "#1D4ED8"), ("Payload Slicing Setup", "#1D4ED8")]
        ),
        (
            840, 360,
            "WebSocket Stream",
            "#4F46E5", "#EEF2FF", "#C7D2FE",
            "Duplex Live Channel",
            [("Live Cluster Metrics", "#4338CA"), ("Instant Churn Alerts", "#4338CA"), ("Output Downloader", "#4338CA")]
        )
    ]

    for (cy, ch, c_title, c_accent, c_bg_c, c_border_c, c_badge_t, c_pills) in c_cards:
        draw.rounded_rectangle((x1, cy, x1 + w1, cy + ch), radius=12, fill="#FFFFFF", outline=c_border_c, width=2)
        draw.rounded_rectangle((x1, cy, x1 + 8, cy + ch), radius=3, fill=c_accent)
        draw.text((x1 + 24, cy + 32), c_title, font=f_card_hdr, fill=c_dark, anchor="lm")
        draw_badge(x1 + w1 - 100, cy + 32, c_badge_t, c_accent, c_white, f_arrow_sub, px=8, py=3)

        for pi, (ptxt, pcol) in enumerate(c_pills):
            py = cy + 70 + pi * 80
            draw.rounded_rectangle((x1 + 20, py, x1 + w1 - 20, py + 65), radius=8, fill=c_bg_c, outline=c_border_c, width=1)
            draw.text((x1 + 35, py + 32), ptxt, font=f_card_sub, fill=pcol, anchor="lm")

    # ──────────────────────────────────────────────────────────────────────
    # 2. MASTER ORCHESTRATOR BLOCKS
    # ──────────────────────────────────────────────────────────────────────
    w2 = 520
    x2 = (t2_x1 + t2_x2 - w2) // 2

    # Top Engines Panel
    draw.rounded_rectangle((x2, 240, x2 + w2, 690), radius=12, fill="#FFFFFF", outline="#DDD6FE", width=2)
    draw.rounded_rectangle((x2, 240, x2 + 8, 690), radius=3, fill="#6366F1")
    draw.text((x2 + 25, 275), "FastAPI Orchestration Core", font=f_card_hdr, fill="#4338CA", anchor="lm")
    draw_badge(x2 + w2 - 100, 275, "Control Plane", "#6366F1", c_white, f_arrow_sub, px=8, py=3)

    engines = [
        ("FastAPI Gateway", "Async Router Engine", "#6366F1"),
        ("Task Splitter", "Domain Decomposition", "#8B5CF6"),
        ("Reaper Scheduler", "Sub-15s Failover Recovery", "#7C3AED"),
        ("Result Aggregator", "Checksum & Output Stitcher", "#4338CA")
    ]
    for ei, (etitle, esub, eaccent) in enumerate(engines):
        ey = 315 + ei * 88
        draw.rounded_rectangle((x2 + 20, ey, x2 + w2 - 20, ey + 75), radius=8, fill="#F5F3FF", outline="#EDE9FE", width=1)
        draw.rounded_rectangle((x2 + 20, ey, x2 + 26, ey + 75), radius=2, fill=eaccent)
        draw.text((x2 + 40, ey + 25), etitle, font=f_card_hdr, fill=c_dark, anchor="lm")
        draw.text((x2 + 40, ey + 52), esub, font=f_pill_txt, fill=eaccent, anchor="lm")

    # Bottom State Panel (Datastores)
    draw.rounded_rectangle((x2, 720, x2 + w2, 1220), radius=12, fill="#FFFFFF", outline="#DDD6FE", width=2)
    draw.rounded_rectangle((x2, 720, x2 + 8, 1220), radius=3, fill="#4338CA")
    draw.text((x2 + 25, 755), "Cluster State Subsystem", font=f_card_hdr, fill="#4338CA", anchor="lm")
    draw_badge(x2 + w2 - 100, 755, "Data Stores", "#4338CA", c_white, f_arrow_sub, px=8, py=3)

    # MongoDB
    draw.rounded_rectangle((x2 + 20, 795, x2 + w2 - 20, 980), radius=10, fill="#ECFDF5", outline="#A7F3D0", width=2)
    draw.rounded_rectangle((x2 + 20, 795, x2 + 28, 980), radius=3, fill="#059669")
    draw.text((x2 + 42, 830), "MongoDB Database", font=f_card_hdr, fill="#065F46", anchor="lm")
    draw_badge(x2 + w2 - 110, 830, "Persistent Store", "#059669", c_white, f_arrow_sub, px=8, py=3)
    draw.text((x2 + 42, 880), "• Transactional Job State", font=f_card_sub, fill="#047857", anchor="lm")
    draw.text((x2 + 42, 925), "• Worker Registration Logs", font=f_card_sub, fill="#047857", anchor="lm")

    # Redis
    draw.rounded_rectangle((x2 + 20, 1010, x2 + w2 - 20, 1195), radius=10, fill="#FEF2F2", outline="#FECDD3", width=2)
    draw.rounded_rectangle((x2 + 20, 1010, x2 + 28, 1195), radius=3, fill="#DC2626")
    draw.text((x2 + 42, 1045), "Redis Key-Store", font=f_card_hdr, fill="#991B1B", anchor="lm")
    draw_badge(x2 + w2 - 110, 1045, "In-Memory Lease", "#DC2626", c_white, f_arrow_sub, px=8, py=3)
    draw.text((x2 + 42, 1095), "• Sliding Heartbeat Leases", font=f_card_sub, fill="#B91C1C", anchor="lm")
    draw.text((x2 + 42, 1140), "• Sub-15s TTL Expiration Keys", font=f_card_sub, fill="#B91C1C", anchor="lm")

    # ──────────────────────────────────────────────────────────────────────
    # 3. TRANSPORT & STORAGE BLOCKS
    # ──────────────────────────────────────────────────────────────────────
    w3 = 500
    x3 = (t3_x1 + t3_x2 - w3) // 2

    # RabbitMQ Card (Control Plane)
    draw.rounded_rectangle((x3, 240, x3 + w3, 690), radius=12, fill="#FFFFFF", outline="#FED7AA", width=2)
    draw.rounded_rectangle((x3, 240, x3 + 8, 690), radius=3, fill="#EA580C")
    draw.text((x3 + 25, 275), "RabbitMQ Broker", font=f_card_hdr, fill="#9A3412", anchor="lm")
    draw_badge(x3 + w3 - 100, 275, "AMQP Broker", "#EA580C", c_white, f_arrow_sub, px=8, py=3)

    rmq_blocks = [
        ("AMQP Work Queues", "Direct Work Queue Routing", "#EA580C"),
        ("Task Manifests", "Lightweight JSON Manifests <2KB", "#EA580C"),
        ("Dead-Letter Exchange", "Poison Task Poison Protection", "#EA580C")
    ]
    for ri, (rtitle, rsub, raccent) in enumerate(rmq_blocks):
        ry = 320 + ri * 115
        draw.rounded_rectangle((x3 + 20, ry, x3 + w3 - 20, ry + 95), radius=8, fill="#FFF7ED", outline="#FFEDD5", width=1)
        draw.text((x3 + 35, ry + 32), rtitle, font=f_card_hdr, fill="#9A3412", anchor="lm")
        draw.text((x3 + 35, ry + 68), rsub, font=f_pill_txt, fill="#C2410C", anchor="lm")

    # MinIO S3 Card (Data Plane)
    draw.rounded_rectangle((x3, 720, x3 + w3, 1220), radius=12, fill="#FFFFFF", outline="#99F6E4", width=2)
    draw.rounded_rectangle((x3, 720, x3 + 8, 1220), radius=3, fill="#0D9488")
    draw.text((x3 + 25, 755), "MinIO S3 Cluster", font=f_card_hdr, fill="#115E59", anchor="lm")
    draw_badge(x3 + w3 - 100, 755, "Object Store", "#0D9488", c_white, f_arrow_sub, px=8, py=3)

    minio_blocks = [
        ("Raw Input Chunks", "Partitioned Task Payloads", "#0D9488"),
        ("Result Output Tensors", "Processed Output Arrays", "#0D9488"),
        ("Presigned Direct URIs", "Zero-Broker Line-Rate HTTP/2", "#0D9488")
    ]
    for mi, (mtitle, msub, maccent) in enumerate(minio_blocks):
        my = 800 + mi * 130
        draw.rounded_rectangle((x3 + 20, my, x3 + w3 - 20, my + 110), radius=8, fill="#F0FDFA", outline="#CCFBF1", width=1)
        draw.text((x3 + 35, my + 38), mtitle, font=f_card_hdr, fill="#115E59", anchor="lm")
        draw.text((x3 + 35, my + 78), msub, font=f_pill_txt, fill="#0D9488", anchor="lm")

    # ──────────────────────────────────────────────────────────────────────
    # 4. EDGE WORKER GRID BLOCKS
    # ──────────────────────────────────────────────────────────────────────
    w4 = 350
    x4 = (t4_x1 + t4_x2 - w4) // 2

    workers = [
        (
            240, 290,
            "GPU Worker Node",
            "#16A34A", "#F0FDF4", "#BBF7D0", "#166534",
            "NVIDIA CUDA Acceleration",
            "• CuPy CUDA Kernels",
            "• 2D Sobel Convolution",
            "• Docker Container Sandbox"
        ),
        (
            560, 290,
            "CPU Worker Node",
            "#2563EB", "#EFF6FF", "#BFDBFE", "#1E40AF",
            "Vectorized Multi-Threading",
            "• NumPy BLAS Optimization",
            "• Block Matrix Multiplication",
            "• Docker Container Sandbox"
        ),
        (
            880, 340,
            "Volunteer Edge Laptop",
            "#D97706", "#FFFBEB", "#FDE68A", "#92400E",
            "Dynamic High-Churn Grid",
            "• SHA-256 Hash Mining",
            "• 5s Heartbeat Lease Agent",
            "• Sub-15s Auto Recovery",
            "• Dropped Host Privileges"
        )
    ]

    for (wy, wh, w_title, w_accent, w_bg_c, w_border_c, w_text, w_sub_h, *w_bullets) in workers:
        draw.rounded_rectangle((x4, wy, x4 + w4, wy + wh), radius=12, fill=w_bg_c, outline=w_border_c, width=2)
        draw.rounded_rectangle((x4, wy, x4 + 8, wy + wh), radius=3, fill=w_accent)
        draw.text((x4 + 20, wy + 30), w_title, font=f_card_hdr, fill=w_text, anchor="lm")
        draw.text((x4 + 20, wy + 58), w_sub_h, font=f_arrow_sub, fill=w_accent, anchor="lm")
        
        for bi, bullet in enumerate(w_bullets):
            by = wy + 94 + bi * 38
            draw.text((x4 + 20, by), bullet, font=f_card_sub, fill="#334155", anchor="lm")

    # ──────────────────────────────────────────────────────────────────────
    # NUMBERED INTER-TIER DATAFLOW ARROWS & BADGES (Clean, Spacious)
    # ──────────────────────────────────────────────────────────────────────

    # Flow 1: Client -> Master (Submit Job)
    c1_x = (t1_x2 + t2_x1) // 2
    y_f1 = 400
    draw_arrow((t1_x2 + 8, y_f1), (t2_x1 - 8, y_f1), "#2563EB", width=4, head_size=15)
    draw_badge(c1_x, y_f1 - 22, "1. Submit Job", "#2563EB", c_white, f_arrow_num, px=14, py=5)
    draw_badge(c1_x, y_f1 + 20, "REST API", "#EFF6FF", "#1D4ED8", f_arrow_sub, px=10, py=2, border="#BFDBFE")

    # Flow 7: Master -> Client (Live Progress)
    y_f7 = 620
    draw_arrow((t2_x1 - 8, y_f7), (t1_x2 + 8, y_f7), "#4F46E5", width=4, head_size=15)
    draw_badge(c1_x, y_f7 - 22, "7. Live Telemetry", "#4F46E5", c_white, f_arrow_num, px=14, py=5)
    draw_badge(c1_x, y_f7 + 20, "WebSockets", "#EEF2FF", "#4338CA", f_arrow_sub, px=10, py=2, border="#C7D2FE")

    # Flow 3: Master -> RabbitMQ (Enqueue Manifests)
    c2_x = (t2_x2 + t3_x1) // 2
    y_f3 = 400
    draw_arrow((t2_x2 + 8, y_f3), (t3_x1 - 8, y_f3), "#EA580C", width=4, head_size=15)
    draw_badge(c2_x, y_f3 - 22, "3. Enqueue Tasks", "#EA580C", c_white, f_arrow_num, px=14, py=5)
    draw_badge(c2_x, y_f3 + 20, "Manifests <2KB", "#FFF7ED", "#C2410C", f_arrow_sub, px=10, py=2, border="#FED7AA")

    # Flow 2: Master -> MinIO S3 (Stage Payloads)
    y_f2 = 860
    draw_arrow((t2_x2 + 8, y_f2), (t3_x1 - 8, y_f2), "#0D9488", width=4, head_size=15)
    draw_badge(c2_x, y_f2 - 22, "2. Stage Payloads", "#0D9488", c_white, f_arrow_num, px=14, py=5)
    draw_badge(c2_x, y_f2 + 20, "MinIO PUT", "#F0FDFA", "#0F766E", f_arrow_sub, px=10, py=2, border="#99F6E4")

    # Flow 4: RabbitMQ -> Workers (Pull Tasks)
    c3_x = (t3_x2 + t4_x1) // 2
    y_f4 = 400
    draw_arrow((t3_x2 + 8, y_f4), (t4_x1 - 8, y_f4), "#EA580C", width=4, head_size=15)
    draw_badge(c3_x, y_f4 - 22, "4. Pull Task", "#EA580C", c_white, f_arrow_num, px=14, py=5)
    draw_badge(c3_x, y_f4 + 20, "QoS Prefetch 1", "#FFF7ED", "#C2410C", f_arrow_sub, px=10, py=2, border="#FED7AA")

    # Flow 5: MinIO <-> Workers (Direct Stream)
    y_f5 = 920
    draw_arrow((t3_x2 + 8, y_f5), (t4_x1 - 8, y_f5), "#0D9488", width=4, head_size=15, bidirectional=True)
    draw_badge(c3_x, y_f5 - 22, "5. Direct S3 Stream", "#0D9488", c_white, f_arrow_num, px=14, py=5)
    draw_badge(c3_x, y_f5 + 20, "Zero-Copy HTTP/2", "#F0FDFA", "#0F766E", f_arrow_sub, px=10, py=2, border="#99F6E4")

    # Flow 6: Workers -> Master Redis (Heartbeat Lease)
    y_f6 = 1110
    draw_arrow((t4_x1 - 8, y_f6), (t3_x2 + 8, y_f6), "#DC2626", width=4, head_size=14)
    draw_badge(c3_x, y_f6 - 22, "6. Heartbeat Ping", "#DC2626", c_white, f_arrow_num, px=14, py=5)
    draw_badge(c3_x, y_f6 + 20, "5s Cadence", "#FEF2F2", "#B91C1C", f_arrow_sub, px=10, py=2, border="#FECDD3")

    draw_arrow((t3_x1 - 8, y_f6), (t2_x2 + 8, y_f6), "#DC2626", width=4, head_size=14)
    draw_badge(c2_x, y_f6 - 22, "Lease Check", "#DC2626", c_white, f_arrow_num, px=14, py=5)
    draw_badge(c2_x, y_f6 + 20, "TTL 15s", "#FEF2F2", "#B91C1C", f_arrow_sub, px=10, py=2, border="#FECDD3")

    # ──────────────────────────────────────────────────────────────────────
    # SAVE CLEAN IMAGE
    # ──────────────────────────────────────────────────────────────────────
    output_path = r"c:\Users\VICTUS\OneDrive\Desktop\4th Year Project\DaeMon\survey paper\architecture_diagram_colorful.png"
    img.save(output_path, "PNG", quality=95)
    print(f"Successfully generated clean simplified architecture diagram: {output_path}")

if __name__ == "__main__":
    generate_clean_simplified_architecture_diagram()
