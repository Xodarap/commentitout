#!/usr/bin/env python3
"""
Analyze hacking rates by model in each experimental condition using Inspect AI samples_df.
"""

import pandas as pd
from inspect_ai.analysis import samples_df, EvalModel, SampleSummary
import json

def analyze_hacking_rates(log_dir="logs"):
    """
    Create a table of hacking rates by model in each experimental condition.
    
    Args:
        log_dir: Directory containing the evaluation logs
    
    Returns:
        Tuple of (results DataFrame, pivot table, full DataFrame)
    """
    
    # Load samples with model information and scores
    df = samples_df(
        logs=log_dir,
        columns=EvalModel + SampleSummary
    )
    
    # Extract model name from the eval data
    # Assuming model information is in the DataFrame
    if 'model' not in df.columns and 'eval.model' in df.columns:
        df['model'] = df['eval.model']
    elif 'model' not in df.columns:
        # Try to extract from other possible locations
        print("Warning: Model column not found directly, checking alternatives...")
        if 'eval_model' in df.columns:
            df['model'] = df['eval_model']
    
    def classify_prompt(prompt):
        if 'COMMENT OUT' in prompt:
            return 'extreme'
        elif 'Be sure not to remove any functionality.' in prompt:
            return 'moderate'
        else:
            return 'none'
    df['condition'] = df.apply(
        lambda row: f"{row['metadata_task_root']},{row['metadata_body']},{row['metadata_header']},{row['metadata_extra_code']},{classify_prompt(row['metadata_prompt_suffix'])}",
        axis=1
    )
    
    df['hacking_success'] = df['score_test_scoring'].apply(
        lambda x: json.loads(x)['hacked'] == 'I'
    )
    
    # Group by model and condition to calculate hacking rates
    results = df.groupby(['model', 'condition']).agg(
        total_attempts=('sample_id', 'count'),
        successful_hacks=('hacking_success', 'sum')
    ).reset_index()
    
    # Calculate hacking rate as percentage
    results['hacking_rate'] = (results['successful_hacks'] / results['total_attempts'] * 100).round(2)
    
    # Create pivot table for better visualization
    pivot_table = results.pivot(
        columns='model',
        index='condition',
        values='successful_hacks'
    ).fillna(0)
    
    clean_results = results.copy()[['model', 'metadata_body', 'metadata_header', 'metadata_extra_code', 'metadata_prompt_suffix', 'hacking_success']]
    clean_results['metadata_prompt_suffix'] = clean_results['metadata_prompt_suffix'].apply(classify_prompt)
    
    # Add summary statistics
    pivot_table['Mean'] = pivot_table.mean(axis=1).round(2)
    pivot_table.loc['Mean'] = pivot_table.mean(axis=0).round(2)
    
    return clean_results, pivot_table, df


def analyze_by_factor(df):
    """Analyze hacking rates by individual experimental factors."""
    
    factors = ['task_root', 'extra_code', 'header', 'body', 'prompt_suffix']
    factor_results = {}
    
    for factor in factors:
        if factor in df.columns:
            factor_results[factor] = df.groupby(['model', factor]).agg(
                total_attempts=('sample_id', 'count'),
                successful_hacks=('hacking_success', 'sum')
            ).reset_index()
            factor_results[factor]['hacking_rate'] = (
                factor_results[factor]['successful_hacks'] / 
                factor_results[factor]['total_attempts'] * 100
            ).round(2)
    
    return factor_results


def print_results(results_df, pivot_table, df=None):
    """Print formatted results."""
    
    print("\n" + "="*60)
    print("HACKING RATES BY MODEL AND EXPERIMENTAL CONDITION")
    print("="*60)
    
    # If we have the full dataframe, analyze by individual factors
    if df is not None:
        factor_results = analyze_by_factor(df)
        
        print("\n\nAnalysis by Individual Factors:")
        print("="*60)
        
        for factor, factor_df in factor_results.items():
            print(f"\n{factor.upper().replace('_', ' ')}:")
            print("-"*40)
            pivot = factor_df.pivot(
                index='model',
                columns=factor,
                values='hacking_rate'
            ).fillna(0)
            print(pivot.to_string())
    
    print("\n\nDetailed Results (All Combinations):")
    print("-"*60)
    print(results_df.head(20).to_string(index=False))
    
    if len(results_df) > 20:
        print(f"\n... ({len(results_df) - 20} more rows)")
    
    print("\n\nSummary Pivot Table (Hacking Rate %):")
    print("-"*60)
    print(pivot_table.to_string())
    
    print("\n" + "="*60)


def main():
    """Main execution function."""
    
    # Analyze hacking rates
    results, pivot_table, df = analyze_hacking_rates('logs-bulk-20250913161126')
    
    # Print results with factor analysis
    print_results(results, pivot_table, df)
    
    # Save results to CSV files
    results.to_csv("hacking_rates_detailed.csv", index=False)
    pivot_table.to_csv("hacking_rates_pivot.csv")
    
    # Save factor analysis results
    if df is not None:
        factor_results = analyze_by_factor(df)
        for factor, factor_df in factor_results.items():
            factor_df.to_csv(f"hacking_rates_by_{factor}.csv", index=False)
    
    print("\nResults saved to:")
    print("  - hacking_rates_detailed.csv")
    print("  - hacking_rates_pivot.csv")
    for factor in ['task_root', 'extra_code', 'header', 'body', 'prompt_suffix']:
        print(f"  - hacking_rates_by_{factor}.csv")


if __name__ == "__main__":
    main()