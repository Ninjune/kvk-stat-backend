from pathlib import Path
import plotly.graph_objects as go
from rank_percentiles.generator import RankCount
from util import log
import plotly.io as pio

pio.get_chrome()  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]

COUNT_BAR_PATH = "../data/cached/graphs/count_bar/"
CUMULATIVE_BAR_PATH = "../data/cached/graphs/cumulative_bar/"
PERCENTILE_BAR_PATH = "../data/cached/graphs/cumulative_percentile_bm_bar/" 
DIFFICULTY_PERCENTILE_BAR_PATH = "../data/cached/graphs/cumulative_percentile_difficulty" 

def gen_graphs(data: RankCount):
    Path(COUNT_BAR_PATH).mkdir(parents=True, exist_ok=True)
    Path(CUMULATIVE_BAR_PATH).mkdir(parents=True, exist_ok=True)
    Path(PERCENTILE_BAR_PATH).mkdir(parents=True, exist_ok=True)
    Path(DIFFICULTY_PERCENTILE_BAR_PATH).mkdir(parents=True, exist_ok=True)

    # count_bar graphs
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

        save_graph(fig, COUNT_BAR_PATH, f"{benchmark_name.replace(' ', '_')}_bar_graph.png")

    # cumulative graphs
    for benchmark_name, difficulties in data.items():
        fig = go.Figure()
        
        # Add a bar trace for each difficulty level
        for difficulty_name, ranks in difficulties.items():
            cumulative = _generate_cumulative_count(data, benchmark_name, difficulty_name)
            if cumulative is None:
                continue

            fig.add_trace(go.Bar(
                name=difficulty_name,
                x=list(cumulative.keys()),
                y=list(cumulative.values()),
                text=list(cumulative.values()),
                textposition='auto',
            ))
        
        # Update layout
        fig.update_layout(
            title=f'{benchmark_name} - Cumulative Rank Distribution (>= highest rank)',
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

        save_graph(fig, CUMULATIVE_BAR_PATH, f"{benchmark_name.replace(' ', '_')}_bar_graph.png")

    # percentile graphs
    for benchmark_name, difficulties in data.items():
        fig = go.Figure()
        
        # Add a bar trace for each difficulty level
        for difficulty_name, ranks in difficulties.items():
            cumulative = _generate_cumulative_percentages_benchmark(data, benchmark_name, difficulty_name)
            if cumulative is None:
                continue

            fig.add_trace(go.Bar(
                name=difficulty_name,
                x=list(cumulative.keys()),
                y=list(cumulative.values()),
                text=list(cumulative.values()),
                textposition='auto',
            ))
        
        # Update layout
        fig.update_layout(
            title=f'{benchmark_name} - Cumulative Rank Distribution (>= highest rank)',
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

        save_graph(fig, PERCENTILE_BAR_PATH, f"{benchmark_name.replace(' ', '_')}_bar_graph.png")


    log("All graphs generated!")

def save_graph(fig: go.Figure, path: str, name: str):
        # Save as PNG
        filename = Path(path + name)
        fig.write_image(filename, engine='kaleido')
        log(f"Saved: {filename}")

def _generate_cumulative_count(data: RankCount, benchmark_name: str, difficulty_name: str) -> dict[str, int]|None:
    """
    Generate cumulative player counts (>= each rank).
    Each rank shows count of players at that rank or higher.
    
    Args:
        data: The rank count dictionary
        benchmark_name: Name of benchmark
        difficulty_name: Name of difficulty
    
    Returns:
        dict: {rank: cumulative_count} where cumulative_count is players >= that rank
    """
    if benchmark_name not in data or difficulty_name not in data[benchmark_name]:
        return None
    
    ranks = data[benchmark_name][difficulty_name]
    rank_names = list(ranks.keys())
    
    # Calculate cumulative counts from right to left (highest ranks first)
    cumulative = {}
    running_total = 0
    
    for rank in reversed(rank_names):
        running_total += ranks[rank]
        cumulative[rank] = running_total
    
    # Return in original order
    return {rank: cumulative[rank] for rank in rank_names}


def _generate_cumulative_percentages_benchmark(data: RankCount, benchmark_name: str, difficulty_name: str) -> dict[str, float]|None:
    """
    Generate cumulative percentages as % of entire benchmark.
    
    Args:
        data: The rank count dictionary
        benchmark_name: Name of benchmark
        difficulty_name: Name of difficulty
    
    Returns:
        dict: {rank: percentage} where percentage is % of total benchmark players >= that rank
    """
    if benchmark_name not in data:
        return None
    
    # Calculate total players across all difficulties
    total_benchmark_players = sum(
        count for diff_ranks in data[benchmark_name].values() 
        for count in diff_ranks.values()
    )
    
    if total_benchmark_players == 0:
        return None
    
    cumulative_counts = _generate_cumulative_count(data, benchmark_name, difficulty_name)
    if cumulative_counts is None:
        return None
    
    return {
        rank: (count / total_benchmark_players) * 100 
        for rank, count in cumulative_counts.items()
    }


def _generate_cumulative_percentages_difficulty(data: RankCount, benchmark_name: str, difficulty_name: str) -> dict[str, float]|None:
    """
    Generate cumulative percentages as % of players in that difficulty.
    
    Args:
        data: The rank count dictionary
        benchmark_name: Name of benchmark
        difficulty_name: Name of difficulty
    
    Returns:
        dict: {rank: percentage} where percentage is % of difficulty players >= that rank
    """
    if benchmark_name not in data or difficulty_name not in data[benchmark_name]:
        return None
    
    ranks = data[benchmark_name][difficulty_name]
    total_difficulty_players = sum(ranks.values())
    
    if total_difficulty_players == 0:
        return None
    
    cumulative_counts = _generate_cumulative_count(data, benchmark_name, difficulty_name)
    if cumulative_counts is None:
        return None
    
    return {
        rank: (count / total_difficulty_players) * 100 
        for rank, count in cumulative_counts.items()
    }
