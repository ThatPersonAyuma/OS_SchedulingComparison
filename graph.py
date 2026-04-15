import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def plot_advanced_gantt(processes):
    """
    processes: list of dict
    {
        "pid": int,
        "arrival": int,
        "start": int,
        "finish": int,
        "deadline": int
    }
    """
    # Warna berbeda per proses (run bar)
    RUN_COLORS = [
        "#7fc97f", "#beaed4", "#fdc086",
        "#386cb0", "#f0027f", "#bf5b17",
    ]
    WAIT_COLOR    = "#a8d5f5"
    WAIT_EDGE     = "#378ADD"
    MISS_COLOR    = "#f09595"
    MISS_EDGE     = "#E24B4A"
    DEADLINE_COLOR = "#E24B4A"

    fig, ax = plt.subplots(figsize=(12, len(processes) * 1.2 + 1.5))

    for i, p in enumerate(processes):
        pid      = p["pid"]
        arrival  = p["arrival"]
        start    = p["start"]
        finish   = p["finish"]
        deadline = p["deadline"]
        missed   = finish > deadline

        run_color  = RUN_COLORS[i % len(RUN_COLORS)]
        run_edge   = "#333"

        # Waiting bar (arrival → start)
        if start > arrival:
            ax.broken_barh(
                [(arrival, start - arrival)], (i - 0.4, 0.8),
                facecolors=WAIT_COLOR,
                edgecolors=WAIT_EDGE,
                linewidth=0.8,
            )
            ax.text(
                (arrival + start) / 2, i, "wait",
                va="center", ha="center", fontsize=8, color=WAIT_EDGE,
            )

        # Running bar (start → finish)
        face = MISS_COLOR if missed else run_color
        edge = MISS_EDGE  if missed else run_edge
        ax.broken_barh(
            [(start, finish - start)], (i - 0.4, 0.8),
            facecolors=face,
            edgecolors=edge,
            linewidth=1,
        )
        ax.text(
            (start + finish) / 2, i, f"P{pid}",
            va="center", ha="center", fontsize=9, fontweight="bold",
            color="#333",
        )

        # Deadline line (dashed + triangle marker)
        ax.plot(
            [deadline, deadline], [i - 0.48, i + 0.48],
            color=DEADLINE_COLOR, linewidth=1.5, linestyle="--",
        )
        ax.plot(deadline, i + 0.52, marker="v", color=DEADLINE_COLOR, markersize=5)

        # Deadline miss badge
        if missed:
            ax.text(
                finish + 0.1, i + 0.3, "MISS",
                va="center", ha="left", fontsize=7, fontweight="bold",
                color="#791F1F",
                bbox=dict(boxstyle="round,pad=0.2", fc=MISS_COLOR, ec=MISS_EDGE, lw=0.8),
            )

        # Labels: Arrival, Start, Finish
        ax.text(arrival - 0.1, i + 0.45, f"A:{arrival}",
                va="bottom", ha="right", fontsize=7, color="#555")
        ax.text(start + 0.1,   i + 0.45, f"S:{start}",
                va="bottom", ha="left",  fontsize=7, color="#333")
        ax.text(finish + 0.1,  i + 0.45, f"F:{finish}",
                va="bottom", ha="left",  fontsize=7, color="#333")

    # Axes
    ax.set_yticks(range(len(processes)))
    ax.set_yticklabels([f"P{p['pid']}" for p in processes], fontsize=10)
    ax.set_xlabel("Time", fontsize=11)
    ax.set_title("Advanced Gantt Chart — Scheduling Algorithm", fontsize=12, pad=12)
    ax.grid(axis="x", linestyle=":", linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)

    # Legend
    legend_handles = [
        mpatches.Patch(fc=WAIT_COLOR, ec=WAIT_EDGE, label="Waiting"),
        mpatches.Patch(fc=RUN_COLORS[0], ec="#333", label="Running (warna per proses)"),
        mpatches.Patch(fc=MISS_COLOR, ec=MISS_EDGE, label="Deadline miss"),
        plt.Line2D([0], [0], color=DEADLINE_COLOR, linewidth=1.5,
                   linestyle="--", label="Deadline"),
    ]
    ax.legend(handles=legend_handles, loc="upper left",
              fontsize=8, framealpha=0.9, ncol=2)

    plt.tight_layout()
    plt.show()