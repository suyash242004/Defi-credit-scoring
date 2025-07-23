#!/usr/bin/env python3
"""
DeFi Credit Scoring System for Aave V2 Protocol
Assigns credit scores (0-1000) to wallets based on transaction behavior
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

import os
os.makedirs("Output Files", exist_ok=True)


class DeFiCreditScorer:
    def __init__(self):
        self.raw_data = None
        self.wallet_features = None
        self.wallet_scores = None
        
    def load_data(self, json_file_path):
        """Load transaction data from JSON file"""
        print("Loading transaction data...")
        with open(json_file_path, 'r') as f:
            self.raw_data = json.load(f)
        print(f"Loaded {len(self.raw_data)} transactions")
        
    def extract_features(self):
        """Extract comprehensive features for each wallet"""
        print("Extracting wallet features...")
        
        wallet_data = defaultdict(lambda: {
            'transactions': [],
            'deposits': [],
            'borrows': [],
            'repays': [],
            'redeems': [],
            'liquidations': []
        })
        
        # Group transactions by wallet
        for tx in self.raw_data:
            wallet = tx['userWallet']
            action = tx['action']
            
            wallet_data[wallet]['transactions'].append(tx)
            
            if action == 'deposit':
                wallet_data[wallet]['deposits'].append(tx)
            elif action == 'borrow':
                wallet_data[wallet]['borrows'].append(tx)
            elif action == 'repay':
                wallet_data[wallet]['repays'].append(tx)
            elif action == 'redeemunderlying':
                wallet_data[wallet]['redeems'].append(tx)
            elif action == 'liquidationcall':
                wallet_data[wallet]['liquidations'].append(tx)
        
        # Calculate features for each wallet
        features = []
        
        for wallet, data in wallet_data.items():
            feature_dict = self._calculate_wallet_features(wallet, data)
            features.append(feature_dict)
        
        self.wallet_features = pd.DataFrame(features)
        print(f"Extracted features for {len(self.wallet_features)} wallets")
        
    def _calculate_wallet_features(self, wallet, data):
        """Calculate comprehensive features for a single wallet"""
        transactions = data['transactions']
        deposits = data['deposits']
        borrows = data['borrows']
        repays = data['repays']
        redeems = data['redeems']
        liquidations = data['liquidations']
        
        # Basic activity metrics
        total_txs = len(transactions)
        deposit_count = len(deposits)
        borrow_count = len(borrows)
        repay_count = len(repays)
        redeem_count = len(redeems)
        liquidation_count = len(liquidations)
        
        # Calculate volumes (handle missing actionData gracefully)
        def safe_amount(tx_list):
            amounts = []
            for tx in tx_list:
                if 'actionData' in tx and 'amount' in tx['actionData']:
                    try:
                        amount = float(tx['actionData']['amount'])
                        if 'assetPriceUSD' in tx['actionData']:
                            price = float(tx['actionData']['assetPriceUSD'])
                            amounts.append(amount * price / 1e6)  # Normalize to USD
                        else:
                            amounts.append(amount / 1e6)  # Assume USD if price missing
                    except (ValueError, TypeError):
                        continue
            return amounts
        
        deposit_amounts = safe_amount(deposits)
        borrow_amounts = safe_amount(borrows)
        repay_amounts = safe_amount(repays)
        
        total_deposit_volume = sum(deposit_amounts) if deposit_amounts else 0
        total_borrow_volume = sum(borrow_amounts) if borrow_amounts else 0
        total_repay_volume = sum(repay_amounts) if repay_amounts else 0
        
        # Time-based features
        timestamps = [tx['timestamp'] for tx in transactions if 'timestamp' in tx]
        if timestamps:
            timestamps.sort()
            account_age_days = (max(timestamps) - min(timestamps)) / 86400
            avg_tx_interval = account_age_days / max(1, total_txs - 1) if total_txs > 1 else 0
        else:
            account_age_days = 0
            avg_tx_interval = 0
        
        # Risk indicators
        liquidation_ratio = liquidation_count / max(1, total_txs)
        
        # Repayment behavior
        if total_borrow_volume > 0:
            repayment_ratio = total_repay_volume / total_borrow_volume
        else:
            repayment_ratio = 1.0 if total_repay_volume > 0 else 0.0
        
        # Utilization patterns
        if deposit_count > 0:
            borrow_utilization = total_borrow_volume / max(1, total_deposit_volume)
        else:
            borrow_utilization = 0
        
        # Diversity metrics
        assets_used = set()
        for tx in transactions:
            if 'actionData' in tx and 'assetSymbol' in tx['actionData']:
                assets_used.add(tx['actionData']['assetSymbol'])
        asset_diversity = len(assets_used)
        
        # Behavioral patterns
        action_diversity = len(set(tx['action'] for tx in transactions))
        
        # Bot-like behavior detection
        if timestamps and len(timestamps) > 2:
            time_diffs = np.diff(timestamps)
            time_regularity = np.std(time_diffs) / (np.mean(time_diffs) + 1e-6)
        else:
            time_regularity = 0
        
        # Average transaction size patterns
        if deposit_amounts:
            deposit_size_consistency = np.std(deposit_amounts) / (np.mean(deposit_amounts) + 1e-6)
        else:
            deposit_size_consistency = 0
            
        return {
            'wallet': wallet,
            'total_transactions': total_txs,
            'deposit_count': deposit_count,
            'borrow_count': borrow_count,
            'repay_count': repay_count,
            'redeem_count': redeem_count,
            'liquidation_count': liquidation_count,
            'total_deposit_volume': total_deposit_volume,
            'total_borrow_volume': total_borrow_volume,
            'total_repay_volume': total_repay_volume,
            'account_age_days': account_age_days,
            'avg_tx_interval': avg_tx_interval,
            'liquidation_ratio': liquidation_ratio,
            'repayment_ratio': repayment_ratio,
            'borrow_utilization': borrow_utilization,
            'asset_diversity': asset_diversity,
            'action_diversity': action_diversity,
            'time_regularity': time_regularity,
            'deposit_size_consistency': deposit_size_consistency
        }
    
    def calculate_credit_scores(self):
        """Calculate credit scores using a weighted scoring system"""
        print("Calculating credit scores...")
        
        df = self.wallet_features.copy()
        
        # Normalize features to 0-1 scale
        def normalize_feature(series, higher_is_better=True):
            if series.max() == series.min():
                return pd.Series([0.5] * len(series), index=series.index)
            
            normalized = (series - series.min()) / (series.max() - series.min())
            return normalized if higher_is_better else (1 - normalized)
        
        # Calculate component scores
        scores = pd.DataFrame(index=df.index)
        
        # 1. Activity Score (25% weight) - Consistent, meaningful activity
        scores['activity_score'] = (
            normalize_feature(df['total_transactions']) * 0.4 +
            normalize_feature(df['account_age_days']) * 0.3 +
            normalize_feature(df['action_diversity']) * 0.3
        )
        
        # 2. Risk Management Score (30% weight) - Low risk, responsible behavior
        scores['risk_score'] = (
            normalize_feature(df['liquidation_ratio'], False) * 0.4 +
            normalize_feature(df['repayment_ratio']) * 0.4 +
            normalize_feature(df['borrow_utilization'].clip(0, 2), False) * 0.2
        )
        
        # 3. Reliability Score (25% weight) - Consistent patterns, not bot-like
        scores['reliability_score'] = (
            normalize_feature(df['time_regularity'], False) * 0.4 +
            normalize_feature(df['deposit_size_consistency'], False) * 0.3 +
            normalize_feature(df['avg_tx_interval'].clip(0, 30)) * 0.3
        )
        
        # 4. Portfolio Sophistication Score (20% weight) - Diverse usage
        scores['sophistication_score'] = (
            normalize_feature(df['asset_diversity']) * 0.6 +
            normalize_feature(df['total_deposit_volume'].clip(0, 100000)) * 0.4
        )
        
        # Combine scores with weights
        final_scores = (
            scores['activity_score'] * 0.25 +
            scores['risk_score'] * 0.30 +
            scores['reliability_score'] * 0.25 +
            scores['sophistication_score'] * 0.20
        )
        
        # Scale to 0-1000 and add some randomness to break ties
        final_scores = final_scores * 1000
        
        # Apply penalties for high-risk behaviors
        penalties = pd.Series(0, index=df.index)
        penalties += df['liquidation_count'] * 50  # Heavy penalty for liquidations
        penalties += np.where(df['repayment_ratio'] < 0.5, 100, 0)  # Poor repayment
        penalties += np.where(df['total_transactions'] < 3, 50, 0)  # Very low activity
        
        final_scores = np.maximum(0, final_scores - penalties)
        
        # Store results
        self.wallet_scores = pd.DataFrame({
            'wallet': df['wallet'],
            'credit_score': final_scores.round().astype(int),
            'activity_score': (scores['activity_score'] * 250).round().astype(int),
            'risk_score': (scores['risk_score'] * 300).round().astype(int),
            'reliability_score': (scores['reliability_score'] * 250).round().astype(int),
            'sophistication_score': (scores['sophistication_score'] * 200).round().astype(int)
        })
        
        print(f"Calculated scores for {len(self.wallet_scores)} wallets")
        
    def generate_analysis(self):
        """Generate comprehensive analysis and visualizations"""
        print("Generating analysis...")
        
        # Create score distribution
        plt.figure(figsize=(15, 10))
        
        # Score distribution histogram
        plt.subplot(2, 3, 1)
        plt.hist(self.wallet_scores['credit_score'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('Credit Score Distribution')
        plt.xlabel('Credit Score')
        plt.ylabel('Number of Wallets')
        
        # Score ranges analysis
        score_ranges = pd.cut(self.wallet_scores['credit_score'], 
                             bins=[0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
                             labels=['0-100', '100-200', '200-300', '300-400', '400-500',
                                   '500-600', '600-700', '700-800', '800-900', '900-1000'])
        
        plt.subplot(2, 3, 2)
        range_counts = score_ranges.value_counts().sort_index()
        range_counts.plot(kind='bar', color='lightcoral', alpha=0.7)
        plt.title('Wallets by Score Range')
        plt.xlabel('Score Range')
        plt.ylabel('Number of Wallets')
        plt.xticks(rotation=45)
        
        # Component scores comparison
        plt.subplot(2, 3, 3)
        component_scores = self.wallet_scores[['activity_score', 'risk_score', 
                                             'reliability_score', 'sophistication_score']]
        component_scores.boxplot()
        plt.title('Component Scores Distribution')
        plt.xticks(rotation=45)
        
        # Score vs features correlation
        merged_data = self.wallet_features.merge(self.wallet_scores, on='wallet')
        
        plt.subplot(2, 3, 4)
        plt.scatter(merged_data['total_transactions'], merged_data['credit_score'], alpha=0.6)
        plt.xlabel('Total Transactions')
        plt.ylabel('Credit Score')
        plt.title('Score vs Transaction Count')
        
        plt.subplot(2, 3, 5)
        plt.scatter(merged_data['repayment_ratio'], merged_data['credit_score'], alpha=0.6)
        plt.xlabel('Repayment Ratio')
        plt.ylabel('Credit Score')
        plt.title('Score vs Repayment Behavior')
        
        plt.subplot(2, 3, 6)
        plt.scatter(merged_data['liquidation_count'], merged_data['credit_score'], alpha=0.6)
        plt.xlabel('Liquidation Count')
        plt.ylabel('Credit Score')
        plt.title('Score vs Liquidations')
        
        plt.tight_layout()
        plt.savefig('Output Files/score_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Generate analysis statistics
        analysis_stats = {
            'total_wallets': len(self.wallet_scores),
            'score_distribution': {
                'mean': self.wallet_scores['credit_score'].mean(),
                'median': self.wallet_scores['credit_score'].median(),
                'std': self.wallet_scores['credit_score'].std(),
                'min': self.wallet_scores['credit_score'].min(),
                'max': self.wallet_scores['credit_score'].max()
            },
            'range_distribution': range_counts.to_dict(),
            'high_score_behavior': self._analyze_score_group(merged_data, 'high'),
            'low_score_behavior': self._analyze_score_group(merged_data, 'low')
        }
        
        return analysis_stats
    
    def _analyze_score_group(self, data, group_type):
        """Analyze behavior patterns for high/low scoring wallets"""
        if group_type == 'high':
            group_data = data[data['credit_score'] >= 700]
        else:
            group_data = data[data['credit_score'] <= 300]
        
        if len(group_data) == 0:
            return {"count": 0, "characteristics": "No wallets in this range"}
        
        return {
            "count": len(group_data),
            "avg_transactions": group_data['total_transactions'].mean(),
            "avg_repayment_ratio": group_data['repayment_ratio'].mean(),
            "avg_liquidation_ratio": group_data['liquidation_ratio'].mean(),
            "avg_asset_diversity": group_data['asset_diversity'].mean(),
            "avg_deposit_volume": group_data['total_deposit_volume'].mean()
        }
    
    def save_results(self):
        """Save wallet scores to CSV"""
        output_file = 'Output Files/wallet_credit_scores.csv'
        self.wallet_scores.to_csv(output_file, index=False)
        print(f"Saved results to {output_file}")
        
        # Also save detailed features for analysis
        detailed_results = self.wallet_features.merge(self.wallet_scores, on='wallet')
        detailed_results.to_csv('Output Files/detailed_wallet_analysis.csv', index=False)
        print("Saved detailed analysis to detailed_wallet_analysis.csv")
    
    def run_complete_analysis(self, json_file_path):
        """Run the complete credit scoring pipeline"""
        self.load_data(json_file_path)
        self.extract_features()
        self.calculate_credit_scores()
        analysis_stats = self.generate_analysis()
        self.save_results()
        
        return analysis_stats

def main():
    """Main execution function"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python defi_credit_scorer.py <json_file_path>")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    # json_file_path = "Input_File/user-wallet-transactions.json"
    
    # Initialize and run the credit scorer
    scorer = DeFiCreditScorer()
    analysis_stats = scorer.run_complete_analysis(json_file_path)
    
    print("\n" + "="*50)
    print("ANALYSIS COMPLETE")
    print("="*50)
    print(f"Total wallets analyzed: {analysis_stats['total_wallets']}")
    print(f"Average credit score: {analysis_stats['score_distribution']['mean']:.1f}")
    print(f"Score range: {analysis_stats['score_distribution']['min']} - {analysis_stats['score_distribution']['max']}")
    print("\nFiles generated:")
    print("- wallet_credit_scores.csv")
    print("- detailed_wallet_analysis.csv")
    print("- score_analysis.png")
    print("- analysis.md (run generate_analysis_md.py)")

if __name__ == "__main__":
    main()