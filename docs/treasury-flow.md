# 💰 Treasury Flow Diagrams

This document provides detailed visualizations of how funds move through the Ram Strategy ecosystem.

---

## 📊 High-Level Treasury Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         INFLOWS                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   DEX Trading│      │  RAM Sales   │      │   Donations  │  │
│  │  Creator Fees│      │   Revenue    │      │  (Optional)  │  │
│  │              │      │              │      │              │  │
│  │   0.5% fee   │      │  Arbitrage   │      │  Community   │  │
│  │   per trade  │      │   Profit     │      │  Support     │  │
│  └──────┬───────┘      └──────┬───────┘      └──────┬───────┘  │
│         │                     │                     │           │
│         └─────────────────────┼─────────────────────┘           │
│                               ▼                                 │
│                    ┌────────────────────┐                       │
│                    │  Treasury Wallet   │                       │
│                    │   (Solana)         │                       │
│                    │                    │                       │
│                    │  Multi-sig 3-of-5  │                       │
│                    │  Address: [PUBKEY] │                       │
│                    └──────────┬─────────┘                       │
│                               │                                 │
└───────────────────────────────┼─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ALLOCATION                                │
├─────────────────────────────────────────────────────────────────┤
│                               │                                 │
│         ┌─────────────────────┼─────────────────────┐           │
│         │                     │                     │           │
│         ▼                     ▼                     ▼           │
│  ┌────────────┐        ┌────────────┐       ┌────────────┐     │
│  │ Operational│        │   Trading  │       │  Reserve   │     │
│  │   Buffer   │        │   Capital  │       │    Fund    │     │
│  │            │        │            │       │            │     │
│  │    10%     │        │     70%    │       │     20%    │     │
│  └────────────┘        └─────┬──────┘       └────────────┘     │
│                              │                                 │
└──────────────────────────────┼─────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         EXECUTION                               │
├─────────────────────────────────────────────────────────────────┤
│                               │                                 │
│                ┌──────────────┴──────────────┐                  │
│                ▼                             ▼                  │
│     ┌────────────────────┐         ┌────────────────────┐      │
│     │  Purchase RAM      │         │   Hold Cash for    │      │
│     │  from Marketplaces │         │   Opportunities    │      │
│     │                    │         │                    │      │
│     │  AI Agent Decides  │         │   Earn Yield on    │      │
│     │  What/When to Buy  │         │   DeFi (Future)    │      │
│     └─────────┬──────────┘         └────────────────────┘      │
│               │                                                 │
│               ▼                                                 │
│     ┌────────────────────┐                                      │
│     │  RAM Inventory     │                                      │
│     │  Storage           │                                      │
│     │                    │                                      │
│     │  - Warehouse       │                                      │
│     │  - Tracking DB     │                                      │
│     └─────────┬──────────┘                                      │
│               │                                                 │
│               ▼                                                 │
│     ┌────────────────────┐                                      │
│     │  Resell RAM        │                                      │
│     │  at Higher Price   │                                      │
│     │                    │                                      │
│     │  Target: 15-30%    │                                      │
│     │  Profit Margin     │                                      │
│     └─────────┬──────────┘                                      │
│               │                                                 │
└───────────────┼─────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         OUTFLOWS                                │
├─────────────────────────────────────────────────────────────────┤
│                               │                                 │
│         ┌─────────────────────┴─────────────────────┐           │
│         ▼                                           ▼           │
│  ┌────────────────┐                         ┌────────────────┐  │
│  │ Reinvest in    │                         │  Token Buyback │  │
│  │ More RAM       │                         │   & Burn       │  │
│  │                │                         │                │  │
│  │ 50% of profit  │                         │ 50% of profit  │  │
│  │                │                         │                │  │
│  │ Compounds      │                         │ Price Support  │  │
│  │ Inventory      │                         │ for $RAM       │  │
│  └────────────────┘                         └────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Detailed Transaction Flow

### 1. Fee Collection Process

```
User trades $RAM on DEX (e.g., Raydium)
    │
    ├─> 99.5% → User receives tokens
    │
    └─> 0.5% → Creator Fee
            │
            ▼
    ┌───────────────────┐
    │ Fee Collector     │
    │ Smart Contract    │
    └─────────┬─────────┘
              │
              │ (Every 1 hour or $100 threshold)
              │
              ▼
    ┌───────────────────┐
    │ Treasury Wallet   │
    │ (Multi-sig)       │
    └───────────────────┘
```

**Smart Contract Pseudocode:**
```solidity
// Simplified example
contract FeeCollector {
    address treasury = 0x...;
    uint256 constant FEE_BPS = 50; // 0.5%
    
    function onTokenTransfer(uint256 amount) external {
        uint256 fee = amount * FEE_BPS / 10000;
        token.transfer(treasury, fee);
        emit FeeCollected(fee, block.timestamp);
    }
}
```

---

### 2. Trade Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Opportunity Detection                              │
└─────────────────────────────────────────────────────────────┘

Price Monitor scans marketplaces every 5 minutes
    │
    ▼
┌─────────────────────────────────────┐
│ Market Data (Example)               │
├─────────────────────────────────────┤
│ Newegg:  32GB DDR5 @ $120           │
│ eBay:    32GB DDR5 @ $165           │
│ Amazon:  32GB DDR5 @ $155           │
└─────────────────────────────────────┘
    │
    ▼
Decision Engine calculates:
    Profit = $165 (eBay sell) - $120 (Newegg buy) = $45
    Costs = $8 (shipping) + $5 (fees) + $2 (tax) = $15
    Net = $45 - $15 = $30 (25% margin) ✅
    
    Confidence Score: 0.85 (based on historical data)
    
    IF net > $20 AND confidence > 0.7:
        RECOMMEND_TRADE()

┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Approval (if > $5k)                                │
└─────────────────────────────────────────────────────────────┘

    Trade Recommendation
        │
        ├─> If amount < $5,000 → Auto-approve
        │
        └─> If amount ≥ $5,000 → Notify multi-sig signers
                │
                ▼
            3 of 5 signers approve via mobile wallet
                │
                ▼
            Trade approved ✅

┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Purchase Execution                                 │
└─────────────────────────────────────────────────────────────┘

    Trade Executor initiates purchase
        │
        ▼
    Transfer USDC from treasury to payment gateway
        │
        ▼
    API call to Newegg:
        POST /api/orders
        {
            "sku": "N82E16820242729",
            "quantity": 1,
            "payment": "USDC"
        }
        │
        ▼
    Order Confirmation
        │
        ▼
    Update inventory database:
        INSERT INTO inventory (sku, cost, date, status)
        VALUES ('N82E16820242729', 120, NOW(), 'pending_delivery')

┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Delivery & Listing                                 │
└─────────────────────────────────────────────────────────────┘

    Wait for shipment (3-7 days)
        │
        ▼
    Tracking API confirms delivery
        │
        ▼
    Update status: 'pending_delivery' → 'in_stock'
        │
        ▼
    Auto-list on eBay:
        POST /api/sell
        {
            "title": "32GB DDR5 RAM (Brand New, Sealed)",
            "price": 165,
            "shipping": "calculated"
        }

┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Sale & Profit Distribution                         │
└─────────────────────────────────────────────────────────────┘

    Item sells on eBay
        │
        ▼
    Funds received: $165
        │
        ▼
    Calculate profit:
        Gross = $165
        Cost = $120
        Fees = $15
        Net Profit = $30
        │
        ▼
    Profit Router executes split:
        ├─> $15 (50%) → RAM Reinvestment Pool
        └─> $15 (50%) → Token Buyback Pool
                │
                ▼
            Buyback $RAM on Raydium
                │
                ▼
            Burn or distribute to treasury
```

---

## 📈 Profit Routing Logic

### Default Split (Configurable via DAO)

```python
# Pseudocode
def route_profit(profit_amount: float):
    """
    Distributes profit according to strategy parameters
    """
    # Get current strategy (can be changed by governance)
    strategy = get_current_strategy()
    
    inventory_pct = strategy.get('inventory_allocation', 0.50)
    buyback_pct = strategy.get('buyback_allocation', 0.50)
    
    assert inventory_pct + buyback_pct == 1.0
    
    # Calculate allocations
    to_inventory = profit_amount * inventory_pct
    to_buyback = profit_amount * buyback_pct
    
    # Execute
    transfer_to_trading_pool(to_inventory)
    execute_buyback(to_buyback)
    
    # Log on-chain
    emit ProfitRouted(
        timestamp=now(),
        total=profit_amount,
        inventory=to_inventory,
        buyback=to_buyback,
        tx_hash=get_tx_hash()
    )
```

### Dynamic Rebalancing (Advanced)

**Scenario:** Market conditions change

```python
def dynamic_rebalancing():
    """
    Adjust split based on market conditions
    """
    ram_market_volatility = get_volatility('RAM')
    token_price_trend = get_price_trend('$RAM')
    
    if ram_market_volatility > 0.3:
        # High volatility → reduce inventory exposure
        return {'inventory': 0.30, 'buyback': 0.70}
    
    elif token_price_trend < -0.2:
        # Token price falling → more buybacks for support
        return {'inventory': 0.40, 'buyback': 0.60}
    
    else:
        # Normal conditions
        return {'inventory': 0.50, 'buyback': 0.50}
```

---

## 💳 Buyback Mechanism

```
┌─────────────────────────────────────────────────────────────┐
│ Token Buyback Process                                      │
└─────────────────────────────────────────────────────────────┘

    Buyback Pool reaches threshold ($500)
        │
        ▼
    ┌───────────────────────┐
    │ Calculate optimal     │
    │ execution strategy    │
    │                       │
    │ - Check liquidity     │
    │ - Minimize slippage   │
    │ - Avoid front-running │
    └───────┬───────────────┘
            │
            ▼
    ┌───────────────────────┐
    │ Execute buy order     │
    │ on Raydium DEX        │
    │                       │
    │ USDC → $RAM           │
    └───────┬───────────────┘
            │
            ▼
    ┌───────────────────────┐
    │ Tokens acquired       │
    │                       │
    │ Option A: Burn        │
    │ Option B: Treasury    │
    └───────┬───────────────┘
            │
            ├─> Option A: Send to burn address (0x000...dead)
            │       │
            │       ▼
            │   Reduces circulating supply permanently
            │
            └─> Option B: Hold in treasury
                    │
                    ▼
                Can be used for:
                - Liquidity provision
                - Future distribution
                - Governance incentives
```

**Buyback Smart Contract:**
```solidity
contract BuybackEngine {
    using SafeMath for uint256;
    
    address constant BURN_ADDRESS = 0x000000000000000000000000000000000000dEaD;
    address ramToken = 0x...;
    address usdcToken = 0x...;
    
    uint256 public buybackThreshold = 500 * 1e6; // $500 USDC
    
    function executeBuyback() external {
        uint256 balance = IERC20(usdcToken).balanceOf(address(this));
        require(balance >= buybackThreshold, "Below threshold");
        
        // Swap USDC for $RAM via DEX router
        uint256 ramReceived = swapUSDCForRAM(balance);
        
        // Option 1: Burn
        IERC20(ramToken).transfer(BURN_ADDRESS, ramReceived);
        
        emit Buyback(balance, ramReceived, block.timestamp);
    }
}
```

---

## 📊 Treasury Accounting

### Double-Entry Ledger Example

| Date | Description | Debit | Credit | Balance |
|------|-------------|-------|--------|---------|
| 1/1  | Initial deposit | $10,000 | - | $10,000 |
| 1/5  | Purchase RAM | - | $1,200 | $8,800 |
| 1/5  | Inventory (asset) | $1,200 | - | - |
| 1/10 | Sell RAM | $1,650 | - | $10,450 |
| 1/10 | Remove inventory | - | $1,200 | - |
| 1/10 | **Realized Profit** | - | - | **$450** |
| 1/10 | Buyback allocation | - | $225 | $10,225 |
| 1/10 | Execute buyback | - | $225 | $10,000 |
| 1/10 | Reinvest allocation | - | $225 | $9,775 |
| 1/15 | Creator fees collected | $350 | - | $10,125 |

**Net Position:**
- Cash: $9,775
- Inventory: $225 (reinvested)
- Total: $10,000 + $450 profit - $450 distributed = $10,000

---

## 🔒 Security Controls

### Multi-Signature Approval Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Transaction Proposal                                        │
└─────────────────────────────────────────────────────────────┘

    Agent proposes trade > $5,000
        │
        ▼
    ┌───────────────────────┐
    │ Multi-sig Wallet      │
    │ 3-of-5 required       │
    └───────┬───────────────┘
            │
            ├─> Signer 1: ✅ Approved (mobile wallet)
            ├─> Signer 2: ✅ Approved (hardware wallet)
            ├─> Signer 3: ✅ Approved (mobile wallet)
            ├─> Signer 4: ⏸️  No response (optional)
            └─> Signer 5: ⏸️  No response (optional)
                │
                ▼
            Threshold reached (3/5) ✅
                │
                ▼
            Transaction executes
                │
                ▼
            All signers notified of execution
```

**Signers:**
1. Core team member (founder)
2. Community representative (elected)
3. Technical advisor
4. Legal counsel
5. Institutional investor (if applicable)

---

## 📉 Risk Mitigation Reserves

### Reserve Fund Allocation

```
Total Treasury: $100,000

├─ Trading Capital: $70,000 (70%)
│   └─> Used for RAM purchases
│
├─ Reserve Fund: $20,000 (20%)
│   ├─> Emergency liquidity: $10,000
│   ├─> Bad trade insurance: $5,000
│   └─> Operating expenses: $5,000
│
└─- Operational Buffer: $10,000 (10%)
    ├─> Gas fees: $2,000
    ├─> Marketplace fees: $3,000
    ├─> Shipping contingency: $3,000
    └─> Miscellaneous: $2,000
```

---

## 🎯 Performance Metrics

### Key Metrics Tracked

```python
class TreasuryMetrics:
    def __init__(self):
        self.total_fees_collected = 0
        self.total_ram_purchased = 0
        self.total_ram_sold = 0
        self.realized_profit = 0
        self.unrealized_profit = 0
        self.buybacks_executed = 0
        self.tokens_burned = 0
        
    def calculate_roi(self):
        """Return on Investment"""
        return (self.realized_profit / self.total_fees_collected) * 100
    
    def calculate_win_rate(self):
        """Percentage of profitable trades"""
        winning_trades = count_winning_trades()
        total_trades = count_total_trades()
        return (winning_trades / total_trades) * 100
    
    def calculate_sharpe_ratio(self):
        """Risk-adjusted returns"""
        avg_return = self.realized_profit / count_total_trades()
        std_dev = calculate_trade_volatility()
        risk_free_rate = 0.04  # 4% annual
        return (avg_return - risk_free_rate) / std_dev
```

---

## 🚨 Emergency Procedures

### Circuit Breaker Triggers

```
IF any of these conditions met:
    ├─ 3 consecutive losing trades → PAUSE_TRADING()
    ├─ Unrealized loss > 30% of inventory → LIQUIDATE_INVENTORY()
    ├─ Treasury balance < $5,000 → STOP_NEW_PURCHASES()
    ├─ Solana network congestion > 5000 TPS → DELAY_TRANSACTIONS()
    └─ Security breach detected → FREEZE_WALLET()
        │
        ▼
    Notify all multi-sig signers immediately
        │
        ▼
    Require unanimous 5-of-5 approval to resume
```

---

## 📄 Audit Trail

Every transaction logged on-chain and in database:

```json
{
  "tx_hash": "5Xn2...",
  "timestamp": "2026-01-28T10:30:00Z",
  "type": "ram_purchase",
  "amount_usd": 1200,
  "marketplace": "newegg",
  "sku": "N82E16820242729",
  "approvers": ["signer1", "signer2", "signer3"],
  "agent_confidence": 0.87,
  "expected_profit": 450,
  "status": "completed"
}
```

**Public Dashboard:** All transactions viewable at `app.ramstrategy.io/transactions`

---

## Conclusion

The treasury flow is designed to be:
- ✅ **Transparent:** All flows visible on-chain
- ✅ **Secure:** Multi-sig protection
- ✅ **Efficient:** Automated where safe
- ✅ **Auditable:** Complete transaction history

For technical implementation, see `/src/treasury/` in the repository.

---

**Last Updated:** January 2026  
**Version:** 1.0
