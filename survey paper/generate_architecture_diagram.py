import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

def create_simplified_bw_architecture_diagram():
    # Crisp, well-proportioned canvas (12 x 6.5 inches at 300 DPI)
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.5)
    ax.axis('off')

    c_white = "#FFFFFF"
    c_black = "#000000"
    c_gray_bg = "#F9F9F9"

    # Helper: Draw clean rounded block
    def draw_card(x, y, w, h, title, subtitle, bullets):
        # Outer box
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                              facecolor=c_white, edgecolor=c_black, linewidth=1.5)
        ax.add_patch(rect)
        
        # Header banner fill (subtle clean accent line)
        ax.plot([x + 0.15, x + w - 0.15], [y + h - 0.68, y + h - 0.68], color=c_black, lw=0.8)

        # Title & Subtitle
        ax.text(x + w / 2, y + h - 0.28, title, ha='center', va='center',
                fontsize=11, fontweight='bold', color=c_black)
        ax.text(x + w / 2, y + h - 0.50, subtitle, ha='center', va='center',
                fontsize=8.5, fontstyle='italic', color=c_black)

        # Bullet points
        y_text = y + h - 0.95
        for b in bullets:
            ax.text(x + 0.2, y_text, b, ha='left', va='center',
                    fontsize=8.2, color=c_black)
            y_text -= 0.30

    # Helper: Draw clean label badge
    def draw_badge(x, y, text, fontsize=7.8, bold=True):
        ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
                fontweight='bold' if bold else 'normal', color=c_black,
                bbox=dict(boxstyle="round,pad=0.25,rounding_size=0.05",
                          facecolor=c_white, edgecolor=c_black, linewidth=0.7))

    # ══════════════════════════════════════════════════════════════════════
    # 4 CORE ARCHITECTURAL BLOCKS (Spacious, Minimalist, Easy to Understand)
    # ══════════════════════════════════════════════════════════════════════

    # 1. Client Layer (Left)
    draw_card(
        x=0.6, y=1.6, w=2.7, h=3.4,
        title="Client Layer",
        subtitle="Next.js 15+ Telemetry Dashboard",
        bullets=[
            "• REST API: Job submission & config",
            "• WebSockets: Real-time live metrics",
            "• Dynamic Gantt progress charts",
            "• Instant error & churn notifications"
        ]
    )

    # 2. Master Orchestrator (Center Top)
    draw_card(
        x=4.3, y=3.5, w=3.4, h=2.6,
        title="Master Orchestrator",
        subtitle="FastAPI Coordinator & Schedulers",
        bullets=[
            "• Task Partitioning (Splitter Engine)",
            "• Capacity-Aware Push Scheduler",
            "• Redis TTL Heartbeat Leases (15s)",
            "• MongoDB Job & Task Metadata Store",
            "• Result Aggregation & Output Stitching"
        ]
    )

    # 3. Decoupled Storage & Message Plane (Center Bottom)
    draw_card(
        x=4.3, y=0.5, w=3.4, h=2.5,
        title="Decoupled Storage Plane",
        subtitle="RabbitMQ AMQP + MinIO S3",
        bullets=[
            "• RabbitMQ: Lightweight tasks (<2 KB)",
            "• MinIO S3: Large binary data chunks",
            "• Presigned URLs for zero-copy streaming",
            "• Zero message broker memory bloat",
            "• Line-rate network transfer (>112 MB/s)"
        ]
    )

    # 4. Heterogeneous Edge Workers (Right)
    draw_card(
        x=8.7, y=0.5, w=2.7, h=5.6,
        title="Edge Workers",
        subtitle="Containerized Volunteer Grid",
        bullets=[
            "• Ultralight Daemon (<50 MB RAM)",
            "• Ephemeral Docker Sandbox (cgroups v2)",
            "",
            "Worker 1: GPU Accelerated",
            "  - NVIDIA CUDA / CuPy Acceleration",
            "  - 2D Sobel Image Convolution (4.57x)",
            "",
            "Worker 2: Multi-Core CPU",
            "  - Vectorized NumPy / BLAS",
            "  - Block Matrix Math (92.7% scaling)",
            "",
            "Worker 3: Edge Volunteer Laptop",
            "  - SHA-256 Proof-of-Work Mining",
            "  - Dropped Privileges (--cap-drop=ALL)",
            "  - Sub-15s Automated Churn Recovery"
        ]
    )

    # ══════════════════════════════════════════════════════════════════════
    # ARROW DATAFLOW CONNECTORS (Simple, Direct, Uncluttered)
    # ══════════════════════════════════════════════════════════════════════

    # Arrow 1: Client -> Master (Job Submit)
    ax.annotate("", xy=(4.3, 4.3), xytext=(3.3, 4.3),
                arrowprops=dict(arrowstyle="-|>", color=c_black, lw=1.6, mutation_scale=14))
    draw_badge(3.8, 4.3, "Submit Job\n(REST API)")

    # Arrow 2: Master -> Client (Live Telemetry)
    ax.annotate("", xy=(3.3, 2.7), xytext=(4.3, 2.7),
                arrowprops=dict(arrowstyle="-|>", color=c_black, lw=1.6, mutation_scale=14))
    draw_badge(3.8, 2.7, "Live Progress\n(WebSockets)")

    # Arrow 3: Master -> Storage Plane (Enqueue Tasks & Upload Payloads)
    ax.annotate("", xy=(6.0, 3.0), xytext=(6.0, 3.5),
                arrowprops=dict(arrowstyle="-|>", color=c_black, lw=1.6, mutation_scale=14))
    draw_badge(6.0, 3.25, "Enqueue Tasks (AMQP) & Stage Payloads (S3)", fontsize=7.2)

    # Arrow 4: Storage Plane -> Workers (Active-Push Tasks & S3 Stream)
    ax.annotate("", xy=(8.7, 1.7), xytext=(7.7, 1.7),
                arrowprops=dict(arrowstyle="<|-|>", color=c_black, lw=1.8, mutation_scale=14))
    draw_badge(8.2, 1.7, "Active-Push Tasks &\nDirect S3 Streaming")

    # Arrow 5: Workers -> Master (Heartbeat Leases)
    ax.annotate("", xy=(7.7, 4.8), xytext=(8.7, 4.8),
                arrowprops=dict(arrowstyle="-|>", color=c_black, lw=1.6, linestyle='dashed', mutation_scale=14))
    draw_badge(8.2, 4.8, "Heartbeat Leases\n(TTL = 15s)")

    # Save cleanly
    plt.tight_layout()
    output_path = r'c:\Users\VICTUS\OneDrive\Desktop\4th Year Project\DaeMon\survey paper\architecture_diagram.png'
    plt.savefig(output_path, bbox_inches='tight', dpi=300, facecolor=c_white)
    plt.close()
    print(f"Simplified architecture diagram saved to: {output_path}")

if __name__ == "__main__":
    create_simplified_bw_architecture_diagram()
