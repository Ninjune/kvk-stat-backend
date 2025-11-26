from pathlib import Path
import plotly.graph_objects as go
from rank_percentiles.generator import RankCount
from util import log
import plotly.io as pio

pio.get_chrome()  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]

COUNT_BAR_PATH = "../data/cached/graphs/count_bar/"
CUMULATIVE_BAR_PATH = "../data/cached/graphs/cumulative_bar/"
PERCENTILE_BAR_PATH = "../data/cached/graphs/cumulative_percentile_bm_bar/" 

def gen_graphs(data: RankCount):
    Path(COUNT_BAR_PATH).mkdir(parents=True, exist_ok=True)
    Path(CUMULATIVE_BAR_PATH).mkdir(parents=True, exist_ok=True)
    Path(PERCENTILE_BAR_PATH).mkdir(parents=True, exist_ok=True)

    gen_graph(data, "Count in Each Rank", COUNT_BAR_PATH)
   
    cumulative = get_cumulative_count(data)
    gen_graph(cumulative, "Cumulative Count (>= rank)", CUMULATIVE_BAR_PATH) 

    # cumulative graphs
    percentile = get_cumulative_percent(data)
    gen_graph(percentile, "Percentiles", PERCENTILE_BAR_PATH)

    log("All graphs generated!")

def gen_graph(data: RankCount, name: str, path: str):
    for benchmark_name, difficulties in data.items():
        fig = go.Figure()
        
        # Add a bar trace for each difficulty level
        for difficulty_name, ranks in difficulties.items():
            fig.add_trace(go.Bar(
                name=difficulty_name,
                x=list(ranks.keys()),
                y=list(ranks.values()),
                text=list(f"{c:.3f}%" for c in ranks.values()),
                textposition='auto',
            ))
        
        # Update layout
        fig.update_layout(
            title=f'{benchmark_name} - {name}',
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

        save_graph(fig, path, f"{benchmark_name.replace(' ', '_')}_bar_graph.png")


def save_graph(fig: go.Figure, path: str, name: str):
        # Save as PNG
        filename = Path(path + name)
        fig.write_image(filename, engine='kaleido')
        log(f"Saved: {filename}")

def get_cumulative_count(data: RankCount) -> RankCount:
    """
    Calculate cumulative count where each rank shows count of players >= that rank.
    Considers difficulty ordering (lower difficulties include all higher difficulties).
    
    Args:
        data: Dictionary with structure {benchmark: {difficulty: {rank: count}}}
    
    Returns:
        RankCount with cumulative counts for each rank
    """
    result = RankCount()
    
    for benchmark_name, difficulties in data.items():
        result[benchmark_name] = {}
        
        # Get ordered list of difficulties
        difficulty_list = list(difficulties.keys())
        
        for diff_idx, (difficulty_name, ranks) in enumerate(difficulties.items()):
            result[benchmark_name][difficulty_name] = {}
            
            # Get ranks in order for this difficulty
            rank_list = list(ranks.keys())
            
            # Calculate cumulative for each rank in current difficulty
            for rank_idx, rank_name in enumerate(rank_list):
                cumulative = 0
                
                # Add all players from higher difficulties
                for higher_diff in difficulty_list[diff_idx + 1:]:
                    cumulative += sum(difficulties[higher_diff].values())
                
                # Add all players from current rank onwards in current difficulty
                for higher_rank in rank_list[rank_idx:]:
                    cumulative += ranks[higher_rank]
                
                result[benchmark_name][difficulty_name][rank_name] = float(cumulative)
    
    return result

def get_cumulative_percent(data: RankCount) -> RankCount:
    """
    Calculate cumulative percentage where each rank shows % of players >= that rank.
    Considers difficulty ordering (lower difficulties include all higher difficulties).
    
    Args:
        data: Dictionary with structure {benchmark: {difficulty: {rank: count}}}
    
    Returns:
        RankCount with cumulative percentages (0-100) for each rank
    """
    # First get the cumulative counts
    cumulative_counts = get_cumulative_count(data)
    
    result = RankCount()
    
    for benchmark_name, difficulties in cumulative_counts.items():
        result[benchmark_name] = {}
        
        # Calculate total players in this benchmark
        total_players = sum(
            sum(ranks.values()) 
            for ranks in data[benchmark_name].values()
        )
        
        for difficulty_name, ranks in difficulties.items():
            result[benchmark_name][difficulty_name] = {}
            
            for rank_name, count in ranks.items():
                # Convert count to percentage
                percentage = (count / total_players) * 100 if total_players > 0 else 0.0
                result[benchmark_name][difficulty_name][rank_name] = round(percentage, 3)
    
    return result
