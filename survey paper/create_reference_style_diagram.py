import os
import math
from PIL import Image, ImageDraw, ImageFont

def generate_reference_style_diagram():
    # Perfectly framed canvas: 2000 x 1030 px (50px balanced margins on all sides)
    W, H = 2000, 1030
    img = Image.new("RGB", (W, H), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    # ──────────────────────────────────────────────────────────────────────
    # FONTS
    # ──────────────────────────────────────────────────────────────────────
    font_dir = "C:\\Windows\\Fonts"
    f_tier_title = ImageFont.truetype(os.path.join(font_dir, "segoeuib.ttf"), 23)
    f_tier_sub = ImageFont.truetype(os.path.join(font_dir, "segoeui.ttf"), 15)
    
    f_box3_title = ImageFont.truetype(os.path.join(font_dir, "segoeuib.ttf"), 21)
    f_node_title = ImageFont.truetype(os.path.join(font_dir, "segoeuib.ttf"), 18)
    f_node_sub = ImageFont.truetype(os.path.join(font_dir, "segoeui.ttf"), 14)
    
    f_right_title = ImageFont.truetype(os.path.join(font_dir, "segoeuib.ttf"), 21)
    f_right_sub = ImageFont.truetype(os.path.join(font_dir, "segoeui.ttf"), 14)

    # ──────────────────────────────────────────────────────────────────────
    # DRAWING HELPERS
    # ──────────────────────────────────────────────────────────────────────
    def draw_rounded_box(box, fill, border, radius=10, width=2):
        x1, y1, x2, y2 = box
        draw.rounded_rectangle((x1, y1, x2, y2), radius=radius, fill=fill, outline=border, width=width)

    def draw_arrow(start_pt, end_pt, color="#475569", width=2, head_size=11):
        x1, y1 = start_pt
        x2, y2 = end_pt
        draw.line([start_pt, end_pt], fill=color, width=width)
        angle = math.atan2(y2 - y1, x2 - x1)
        p1 = (x2 - head_size * math.cos(angle - math.pi / 6), y2 - head_size * math.sin(angle - math.pi / 6))
        p2 = (x2 - head_size * math.cos(angle + math.pi / 6), y2 - head_size * math.sin(angle + math.pi / 6))
        draw.polygon([end_pt, p1, p2], fill=color)

    # ──────────────────────────────────────────────────────────────────────
    # 1. TOP TIER (Presentation Tier)
    # ──────────────────────────────────────────────────────────────────────
    t1_x1, t1_y1, t1_x2, t1_y2 = 50, 40, 1950, 140
    draw_rounded_box((t1_x1, t1_y1, t1_x2, t1_y2), fill="#EBF3FC", border="#3B82F6", radius=10, width=2)
    draw.text(((t1_x1 + t1_x2) // 2, t1_y1 + 32), "1. Presentation Tier: Client Web Dashboard", font=f_tier_title, fill="#0F172A", anchor="mm")
    draw.text(((t1_x1 + t1_x2) // 2, t1_y1 + 68), "Interactive UI | Real-Time WebSockets | Dynamic Gantt Progress | Cluster Health Gauges", font=f_tier_sub, fill="#475569", anchor="mm")

    # Arrow 1 -> 2
    draw_arrow((1000, 140), (1000, 175))

    # ──────────────────────────────────────────────────────────────────────
    # 2. SECOND TIER (FastAPI Gateway)
    # ──────────────────────────────────────────────────────────────────────
    t2_x1, t2_y1, t2_x2, t2_y2 = 50, 175, 1950, 275
    draw_rounded_box((t2_x1, t2_y1, t2_x2, t2_y2), fill="#F0FDF4", border="#10B981", radius=10, width=2)
    draw.text(((t2_x1 + t2_x2) // 2, t2_y1 + 32), "2. API & Orchestration Gateway: FastAPI (Port 8000)", font=f_tier_title, fill="#0F172A", anchor="mm")
    draw.text(((t2_x1 + t2_x2) // 2, t2_y1 + 68), "REST Job Endpoints | Active-Push Scheduler | Sliding-Window Lease Scanner | WebSocket Lifecycle Broadcaster", font=f_tier_sub, fill="#475569", anchor="mm")

    # Arrow 2 -> Middle
    draw_arrow((1000, 275), (1000, 310))

    # ──────────────────────────────────────────────────────────────────────
    # 3. MIDDLE SECTION (Left: Task Pipeline, Right: Docker Sandbox & Engines)
    # ──────────────────────────────────────────────────────────────────────
    # Left Box 3: Container
    t3_x1, t3_y1, t3_x2, t3_y2 = 50, 310, 1260, 775
    draw_rounded_box((t3_x1, t3_y1, t3_x2, t3_y2), fill="#FFFFFF", border="#64748B", radius=10, width=2)
    draw.text(((t3_x1 + t3_x2) // 2, t3_y1 + 32), "3. Orchestration & Task Partitioning Pipeline", font=f_box3_title, fill="#0F172A", anchor="mm")

    # Sub-nodes inside Box 3 (3 columns x 2 rows, plus wide card at bottom)
    grid_nodes = [
        # Col 0, Row 0
        (t3_x1 + 30, t3_y1 + 65, 360, 85, "Task Splitter", "Domain Decomposition", "#FEF9C3", "#EAB308"),
        # Col 1, Row 0
        (t3_x1 + 420, t3_y1 + 65, 360, 85, "Staging Engine", "Presigned URL Staging", "#DBEAFE", "#3B82F6"),
        # Col 2, Row 0
        (t3_x1 + 810, t3_y1 + 65, 360, 85, "Reaper Scheduler", "Sub-15s Failover", "#EDE9FE", "#8B5CF6"),
        # Col 0, Row 1
        (t3_x1 + 30, t3_y1 + 172, 360, 85, "Quorum Verifier", "Result Consensus", "#FCE7F3", "#EC4899"),
        # Col 1, Row 1
        (t3_x1 + 420, t3_y1 + 172, 360, 85, "Task Re-Queue", "Dead-Letter Handler", "#FFEDD5", "#F97316"),
        # Col 2, Row 1
        (t3_x1 + 810, t3_y1 + 172, 360, 85, "Result Stitcher", "Output Aggregator", "#CCFBF1", "#14B8A6"),
    ]

    for (nx, ny, nw, nh, ntitle, nsub, nfill, nborder) in grid_nodes:
        draw_rounded_box((nx, ny, nx + nw, ny + nh), fill=nfill, border=nborder, radius=8, width=1)
        draw.text((nx + nw // 2, ny + 28), ntitle, font=f_node_title, fill="#0F172A", anchor="mm")
        draw.text((nx + nw // 2, ny + 56), nsub, font=f_node_sub, fill="#475569", anchor="mm")

    # Wide bottom card inside Box 3
    bx1, by1, bx2, by2 = t3_x1 + 30, t3_y1 + 282, t3_x2 - 30, t3_y2 - 25
    draw_rounded_box((bx1, by1, bx2, by2), fill="#F8FAFC", border="#64748B", radius=8, width=1)
    draw.text(((bx1 + bx2) // 2, by1 + 44), "Execution Lifecycle Manager", font=f_tier_title, fill="#0F172A", anchor="mm")
    draw.text(((bx1 + bx2) // 2, by1 + 86), "Async Task Dispatch | Speculative Execution | Status Streaming", font=f_tier_sub, fill="#475569", anchor="mm")

    # ──────────────────────────────────────────────────────────────────────
    # RIGHT SIDE STACKED BOXES (4: Docker Sandbox, 5: Compute Engines)
    # ──────────────────────────────────────────────────────────────────────
    r_x1, r_x2 = 1310, 1950

    # Box 4: Docker Sandbox (Top Right)
    t4_y1, t4_y2 = 310, 525
    draw_rounded_box((r_x1, t4_y1, r_x2, t4_y2), fill="#FEE2E2", border="#EF4444", radius=10, width=2)
    draw.text(((r_x1 + r_x2) // 2, t4_y1 + 46), "4. Isolated Docker Worker Sandbox", font=f_right_title, fill="#0F172A", anchor="mm")
    draw.text(((r_x1 + r_x2) // 2, t4_y1 + 96), "daemon-worker:latest | cgroups v2 Limits | Resource Caps", font=f_right_sub, fill="#475569", anchor="mm")
    draw.text(((r_x1 + r_x2) // 2, t4_y1 + 138), "2GB RAM | 60s Execution Timeout | --cap-drop=ALL | Network: isolated", font=f_right_sub, fill="#475569", anchor="mm")

    # Box 5: Compute Engines (Bottom Right)
    t5_y1, t5_y2 = 560, 775
    draw_rounded_box((r_x1, t5_y1, r_x2, t5_y2), fill="#F3E8FF", border="#A855F7", radius=10, width=2)
    draw.text(((r_x1 + r_x2) // 2, t5_y1 + 40), "5. Heterogeneous Compute Engines", font=f_right_title, fill="#0F172A", anchor="mm")
    draw.text(((r_x1 + r_x2) // 2, t5_y1 + 85), "CuPy CUDA GPU (2D Sobel Image Convolution)", font=f_right_sub, fill="#475569", anchor="mm")
    draw.text(((r_x1 + r_x2) // 2, t5_y1 + 120), "NumPy CPU BLAS (Block Matrix Multiplication)", font=f_right_sub, fill="#475569", anchor="mm")
    draw.text(((r_x1 + r_x2) // 2, t5_y1 + 155), "SHA-256 Volunteer Miner (Proof-of-Work Nonce Search)", font=f_right_sub, fill="#475569", anchor="mm")

    # Horizontal arrows from Box 3 to Right
    draw_arrow((t3_x2, 418), (r_x1, 418))
    draw_arrow((t3_x2, 668), (r_x1, 668))

    # Down arrows from Middle to Bottom Row
    draw_arrow((500, 775), (500, 825))
    draw_arrow((1630, 775), (1630, 825))

    # ──────────────────────────────────────────────────────────────────────
    # 4. BOTTOM ROW (6: State Stores, 7: Storage & Transport)
    # ──────────────────────────────────────────────────────────────────────
    b_y1, b_y2 = 825, 975
    b1_x1, b1_x2 = 50, 985
    b2_x1, b2_x2 = 1015, 1950

    # Box 6 (Bottom Left: Metadata & Leases)
    draw_rounded_box((b1_x1, b_y1, b1_x2, b_y2), fill="#EBF3FC", border="#3B82F6", radius=10, width=2)
    draw.text(((b1_x1 + b1_x2) // 2, b_y1 + 40), "6. Cluster State & Leases: MongoDB & Redis", font=f_tier_title, fill="#0F172A", anchor="mm")
    draw.text(((b1_x1 + b1_x2) // 2, b_y1 + 80), "MongoDB: Transactional Job State, Task Descriptors, Worker Registry", font=f_tier_sub, fill="#475569", anchor="mm")
    draw.text(((b1_x1 + b1_x2) // 2, b_y1 + 112), "Redis: Ephemeral Sliding-Window 15s TTL Heartbeat Leases", font=f_tier_sub, fill="#475569", anchor="mm")

    # Box 7 (Bottom Right: Broker & Object Store)
    draw_rounded_box((b2_x1, b_y1, b2_x2, b_y2), fill="#EBF3FC", border="#3B82F6", radius=10, width=2)
    draw.text(((b2_x1 + b2_x2) // 2, b_y1 + 40), "7. Decoupled Transport & Storage: RabbitMQ & MinIO", font=f_tier_title, fill="#0F172A", anchor="mm")
    draw.text(((b2_x1 + b2_x2) // 2, b_y1 + 80), "RabbitMQ: AMQP Work Queues, Lightweight Task Manifests (<2KB)", font=f_tier_sub, fill="#475569", anchor="mm")
    draw.text(((b2_x1 + b2_x2) // 2, b_y1 + 112), "MinIO S3: Zero-Copy Raw Payloads & Processed Binary Tensor Chunks", font=f_tier_sub, fill="#475569", anchor="mm")

    # ──────────────────────────────────────────────────────────────────────
    # SAVE IMAGE
    # ──────────────────────────────────────────────────────────────────────
    output_path = r"c:\Users\VICTUS\OneDrive\Desktop\4th Year Project\DaeMon\survey paper\architecture_diagram_colorful.png"
    img.save(output_path, "PNG", quality=95)
    print(f"Successfully generated reference-style architecture diagram: {output_path}")

if __name__ == "__main__":
    generate_reference_style_diagram()
