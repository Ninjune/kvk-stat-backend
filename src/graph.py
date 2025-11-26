from pathlib import Path
import plotly.graph_objects as go
from rank_percentiles.generator import RankCount
from util import log
import plotly.io as pio

pio.get_chrome()  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]

def gen_graphs(data: RankCount):
    for benchmark_name, difficulties in data.items():
        fig = go.Figure()
        
        # Add a bar trace for each difficulty level
        for difficulty_name, ranks in difficulties.items():
            fig.add_trace(go.Bar(
                name=difficulty_name,
                x=list(ranks.keys()),
                y=list(ranks.values()),
                text=list(ranks.values()),
                textposition='auto',
            ))
        
        # Update layout
        fig.update_layout(
            title=f'{benchmark_name} - Rank Distribution',
            xaxis_title='Rank',
            yaxis_title='Count',
            barmode='group',
            height=600,
            width=1200,
            template='plotly_white',
            font=dict(size=12),
            legend=dict(
                title='Difficulty',
                orientation='v',
                x=1.02,
                y=1
            )
        )
        
        # Save as PNG
        filename = Path(f"../data/cached/{benchmark_name.replace(' ', '_')}_bar_graph.png")
        fig.write_image(filename, engine='kaleido')
        log(f"Saved: {filename}")

    log("All graphs generated!")

