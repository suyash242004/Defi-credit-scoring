# DeFi Credit Scoring System for Aave V2

A machine learning-based credit scoring system that analyzes DeFi transaction patterns to assign credit scores (0-1000) to wallet addresses based on their Aave V2 protocol interactions.

## Overview

This system evaluates wallet creditworthiness by analyzing historical transaction behavior on the Aave V2 protocol. It considers factors such as repayment history, liquidation events, portfolio diversity, and behavioral patterns to generate comprehensive credit scores.

## Architecture

### Core Components

1. **Data Loader**: Ingests JSON transaction data from Aave V2 protocol
2. **Feature Extractor**: Transforms raw transactions into meaningful wallet-level features
3. **Scoring Engine**: Applies weighted scoring algorithm to generate credit scores
4. **Analysis Generator**: Creates visualizations and statistical analysis

### Processing Flow

```
JSON Data → Feature Extraction → Score Calculation → Analysis & Output
    ↓              ↓                    ↓               ↓
Raw Txns → Wallet Features → Credit Scores → Reports & Viz
```

## Scoring Methodology

### Feature Categories

#### 1. Activity Features (25% weight)

- **Transaction Count**: Total number of interactions
- **Account Age**: Time span of wallet activity
- **Action Diversity**: Variety of operations (deposit, borrow, repay, etc.)

#### 2. Risk Management Features (30% weight)

- **Liquidation Ratio**: Frequency of liquidation events (lower is better)
- **Repayment Ratio**: Proportion of borrowed amount repaid
- **Borrow Utilization**: Borrowing relative to deposits (moderate levels preferred)

#### 3. Reliability Features (25% weight)

- **Time Regularity**: Consistency in transaction timing (detects bot behavior)
- **Transaction Size Consistency**: Variance in transaction amounts
- **Average Transaction Interval**: Spacing between transactions

#### 4. Portfolio Sophistication Features (20% weight)

- **Asset Diversity**: Number of different assets used
- **Total Deposit Volume**: Scale of operations (USD normalized)

### Scoring Algorithm

```python
# Component scores normalized to 0-1
activity_score = 0.4 * tx_count + 0.3 * account_age + 0.3 * action_diversity
risk_score = 0.4 * (1-liquidation_ratio) + 0.4 * repayment_ratio + 0.2 * (1-borrow_util)
reliability_score = 0.4 * (1-time_regularity) + 0.3 * (1-size_consistency) + 0.3 * tx_interval
sophistication_score = 0.6 * asset_diversity + 0.4 * deposit_volume

# Final weighted score
final_score = (activity_score * 0.25 + risk_score * 0.30 +
               reliability_score * 0.25 + sophistication_score * 0.20) * 1000

# Apply penalties
penalties = liquidation_count * 50 + poor_repayment_penalty + low_activity_penalty
credit_score = max(0, final_score - penalties)
```

### Score Interpretation

- **900-1000**: Excellent credit - Consistent, responsible users with strong repayment history
- **700-899**: Good credit - Reliable users with minor risk factors
- **500-699**: Fair credit - Average users with moderate risk
- **300-499**: Poor credit - High-risk users with concerning patterns
- **0-299**: Very poor credit - Highly risky or bot-like behavior

## Usage

### Requirements

```bash
pip install pandas numpy matplotlib seaborn
```

### Basic Usage

```bash
python defi_credit_scorer.py transactions.json
```

### Expected Input Format

JSON file containing transaction records with the following structure:

```json
{
  "userWallet": "0x...",
  "action": "deposit|borrow|repay|redeemunderlying|liquidationcall",
  "timestamp": 1629178166,
  "actionData": {
    "amount": "2000000000",
    "assetSymbol": "USDC",
    "assetPriceUSD": "0.9938..."
  }
}
```

### Output Files

- `wallet_credit_scores.csv`: Final credit scores for each wallet
- `detailed_wallet_analysis.csv`: Complete feature set and scores
- `score_analysis.png`: Visualization dashboard
- `analysis.md`: Detailed statistical analysis

## Key Features

### Robust Data Handling

- Graceful handling of missing or malformed data
- Price normalization for cross-asset comparisons
- Timestamp validation and processing

### Bot Detection

- Identifies regular timing patterns indicative of automated trading
- Flags unusual transaction size patterns
- Detects high-frequency, low-diversity activity

### Risk Assessment

- Heavily weights liquidation history
- Considers repayment behavior patterns
- Evaluates borrowing utilization ratios

### Scalability

- Efficient pandas-based processing
- Memory-optimized feature extraction
- Modular design for easy extension

## Model Validation

### Scoring Logic Validation

1. **Liquidation Impact**: Wallets with liquidations receive significantly lower scores
2. **Repayment Behavior**: Strong correlation between repayment ratio and credit score
3. **Activity Patterns**: Moderate activity levels score higher than extreme low/high activity
4. **Bot Detection**: Regular timing patterns result in lower reliability scores

### Edge Case Handling

- Wallets with only deposits: Moderate scores based on consistency
- Single transaction wallets: Low scores due to insufficient data
- High-frequency traders: Risk assessment based on repayment behavior

## Limitations & Future Enhancements

### Current Limitations

- Limited to Aave V2 protocol data
- No cross-protocol analysis
- Static feature weights (not learned)

### Potential Improvements

- Machine learning-based feature weight optimization
- Cross-protocol transaction analysis
- Real-time score updating
- Advanced anomaly detection algorithms
- Integration with external credit data sources

## Technical Details

### Dependencies

- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computations
- `matplotlib/seaborn`: Visualization
- `json`: Data loading

### Performance

- Processes 100K transactions in ~10-30 seconds
- Memory usage scales linearly with transaction count
- Optimized for batch processing

### Code Structure

```
defi_credit_scorer.py
├── DeFiCreditScorer class
│   ├── load_data()
│   ├── extract_features()
│   ├── calculate_credit_scores()
│   ├── generate_analysis()
│   └── save_results()
└── main() execution function
```

## Contributing

This system is designed for extensibility. Key areas for contribution:

- Additional feature engineering
- Alternative scoring methodologies
- Enhanced visualization capabilities
- Performance optimizations
- Multi-protocol support

## License

Open source - feel free to adapt and extend for your use cases.
