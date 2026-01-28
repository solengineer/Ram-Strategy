"""
Decision Engine for RAM Arbitrage Trading
Uses AI to evaluate opportunities and make trading decisions
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)


@dataclass
class TradeRecommendation:
    """AI-generated trade recommendation"""
    action: str  # "BUY", "PASS", "WAIT"
    product_sku: str
    marketplace: str
    reasoning: str
    confidence_score: float  # 0.0 to 1.0
    expected_profit: float
    risk_assessment: str
    timestamp: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'action': self.action,
            'product_sku': self.product_sku,
            'marketplace': self.marketplace,
            'reasoning': self.reasoning,
            'confidence_score': self.confidence_score,
            'expected_profit': self.expected_profit,
            'risk_assessment': self.risk_assessment,
            'timestamp': self.timestamp.isoformat()
        }


class DecisionEngine:
    """
    AI-powered decision engine for evaluating trade opportunities
    Uses Claude API for complex decision-making
    """
    
    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        min_profit_threshold: float = 20.0,
        min_confidence_threshold: float = 0.70,
        max_trade_amount: float = 5000.0
    ):
        self.api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None
        
        self.min_profit_threshold = min_profit_threshold
        self.min_confidence_threshold = min_confidence_threshold
        self.max_trade_amount = max_trade_amount
        
        logger.info(f"Decision engine initialized (AI: {'enabled' if self.client else 'disabled'})")
    
    def evaluate_opportunity(
        self,
        opportunity: Dict,
        treasury_balance: float,
        current_inventory: List[Dict]
    ) -> TradeRecommendation:
        """
        Evaluate a single arbitrage opportunity
        
        Args:
            opportunity: Arbitrage opportunity data
            treasury_balance: Available capital
            current_inventory: Current RAM inventory
        
        Returns:
            TradeRecommendation with action and reasoning
        """
        # Basic checks first
        if opportunity['buy_cost'] > treasury_balance:
            return TradeRecommendation(
                action="PASS",
                product_sku=opportunity['buy_sku'],
                marketplace=opportunity['buy_from'],
                reasoning="Insufficient treasury balance",
                confidence_score=1.0,
                expected_profit=0.0,
                risk_assessment="N/A - funding constraint",
                timestamp=datetime.now()
            )
        
        if opportunity['buy_cost'] > self.max_trade_amount:
            return TradeRecommendation(
                action="PASS",
                product_sku=opportunity['buy_sku'],
                marketplace=opportunity['buy_from'],
                reasoning=f"Trade amount exceeds limit (${self.max_trade_amount})",
                confidence_score=1.0,
                expected_profit=0.0,
                risk_assessment="N/A - position limit",
                timestamp=datetime.now()
            )
        
        if opportunity['net_profit'] < self.min_profit_threshold:
            return TradeRecommendation(
                action="PASS",
                product_sku=opportunity['buy_sku'],
                marketplace=opportunity['buy_from'],
                reasoning=f"Profit below threshold (${self.min_profit_threshold})",
                confidence_score=1.0,
                expected_profit=opportunity['net_profit'],
                risk_assessment="Low reward",
                timestamp=datetime.now()
            )
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(opportunity, current_inventory)
        
        # Use AI for complex evaluation if available
        if self.client:
            return self._ai_evaluation(opportunity, treasury_balance, risk_score)
        else:
            return self._rule_based_evaluation(opportunity, risk_score)
    
    def _calculate_risk_score(
        self,
        opportunity: Dict,
        current_inventory: List[Dict]
    ) -> float:
        """
        Calculate risk score (0.0 = low risk, 1.0 = high risk)
        
        Factors:
        - Concentration risk (too much of one product)
        - Margin thickness
        - Seller reliability
        """
        risk = 0.0
        
        # Concentration risk
        product_type = opportunity['product']['type']
        same_type_count = sum(1 for item in current_inventory if item.get('type') == product_type)
        if same_type_count > 5:
            risk += 0.2  # Already heavy in this type
        
        # Margin thickness (lower margin = higher risk)
        if opportunity['margin_pct'] < 20:
            risk += 0.2
        elif opportunity['margin_pct'] < 30:
            risk += 0.1
        
        # Confidence from price monitor
        if opportunity['confidence'] < 0.7:
            risk += 0.3
        elif opportunity['confidence'] < 0.8:
            risk += 0.2
        
        # Marketplace risk (some platforms more reliable)
        risky_marketplaces = ['aliexpress']
        if opportunity['buy_from'] in risky_marketplaces:
            risk += 0.2
        
        return min(risk, 1.0)
    
    def _rule_based_evaluation(
        self,
        opportunity: Dict,
        risk_score: float
    ) -> TradeRecommendation:
        """
        Simple rule-based decision logic (fallback when AI unavailable)
        """
        # Decision matrix
        if risk_score < 0.3 and opportunity['margin_pct'] > 25:
            action = "BUY"
            reasoning = "Low risk, high margin opportunity"
        elif risk_score < 0.5 and opportunity['margin_pct'] > 20:
            action = "BUY"
            reasoning = "Moderate risk, good margin"
        elif risk_score < 0.6:
            action = "WAIT"
            reasoning = "Elevated risk - monitor for better entry"
        else:
            action = "PASS"
            reasoning = "Risk too high relative to reward"
        
        confidence = 1.0 - risk_score
        
        return TradeRecommendation(
            action=action,
            product_sku=opportunity['buy_sku'],
            marketplace=opportunity['buy_from'],
            reasoning=reasoning,
            confidence_score=confidence,
            expected_profit=opportunity['net_profit'],
            risk_assessment=f"Risk score: {risk_score:.2f}",
            timestamp=datetime.now()
        )
    
    def _ai_evaluation(
        self,
        opportunity: Dict,
        treasury_balance: float,
        risk_score: float
    ) -> TradeRecommendation:
        """
        Use Claude AI for sophisticated trade evaluation
        """
        # Construct prompt
        prompt = f"""You are an AI trading agent for Ram Strategy, a system that arbitrages RAM hardware.

Evaluate this trade opportunity and provide a recommendation:

OPPORTUNITY:
- Product: {opportunity['product']['capacity_gb']}GB {opportunity['product']['type']} @ {opportunity['product']['speed_mhz']}MHz
- Buy from: {opportunity['buy_from']} (SKU: {opportunity['buy_sku']})
- Buy cost: ${opportunity['buy_cost']:.2f}
- Sell on: {opportunity['sell_on']}
- Sell price: ${opportunity['sell_price']:.2f}
- Estimated fees: ${opportunity['estimated_fees']:.2f}
- Net profit: ${opportunity['net_profit']:.2f}
- Margin: {opportunity['margin_pct']:.1f}%
- Confidence: {opportunity['confidence']:.2f}

CONTEXT:
- Treasury balance: ${treasury_balance:.2f}
- Risk score: {risk_score:.2f} (0=low, 1=high)
- Min profit threshold: ${self.min_profit_threshold}
- Max trade amount: ${self.max_trade_amount}

Provide your recommendation in this EXACT JSON format:
{{
    "action": "BUY" or "PASS" or "WAIT",
    "confidence_score": 0.0-1.0,
    "reasoning": "brief explanation",
    "risk_assessment": "key risks identified"
}}

Consider:
1. Profit margin sustainability
2. Seller reliability
3. Market demand trends
4. Resale liquidity
5. Opportunity cost
"""

        try:
            # Call Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse response
            response_text = message.content[0].text
            
            # Extract JSON (Claude might wrap it in markdown)
            if "```json" in response_text:
                json_start = response_text.index("```json") + 7
                json_end = response_text.rindex("```")
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.index("```") + 3
                json_end = response_text.rindex("```")
                response_text = response_text[json_start:json_end].strip()
            
            ai_response = json.loads(response_text)
            
            return TradeRecommendation(
                action=ai_response['action'],
                product_sku=opportunity['buy_sku'],
                marketplace=opportunity['buy_from'],
                reasoning=ai_response['reasoning'],
                confidence_score=ai_response['confidence_score'],
                expected_profit=opportunity['net_profit'],
                risk_assessment=ai_response['risk_assessment'],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"AI evaluation failed: {e}, falling back to rules")
            return self._rule_based_evaluation(opportunity, risk_score)
    
    def batch_evaluate(
        self,
        opportunities: List[Dict],
        treasury_balance: float,
        current_inventory: List[Dict]
    ) -> List[TradeRecommendation]:
        """
        Evaluate multiple opportunities and rank by priority
        """
        recommendations = []
        
        for opp in opportunities:
            rec = self.evaluate_opportunity(opp, treasury_balance, current_inventory)
            recommendations.append(rec)
        
        # Sort: BUY first, then by expected profit
        def sort_key(rec: TradeRecommendation):
            action_priority = {"BUY": 0, "WAIT": 1, "PASS": 2}
            return (action_priority[rec.action], -rec.expected_profit)
        
        recommendations.sort(key=sort_key)
        
        # Filter to only high-confidence BUY recommendations
        buy_recs = [
            r for r in recommendations
            if r.action == "BUY" and r.confidence_score >= self.min_confidence_threshold
        ]
        
        logger.info(f"Evaluated {len(opportunities)} opportunities: {len(buy_recs)} BUY recommendations")
        
        return buy_recs
    
    def generate_trade_plan(
        self,
        recommendations: List[TradeRecommendation],
        available_capital: float
    ) -> List[Dict]:
        """
        Generate executable trade plan within capital constraints
        
        Returns list of trades to execute
        """
        trade_plan = []
        remaining_capital = available_capital
        
        for rec in recommendations:
            if rec.action != "BUY":
                continue
            
            # Find opportunity details (would query from database in production)
            # For now, estimate cost
            estimated_cost = rec.expected_profit * 4  # Rough estimate
            
            if estimated_cost <= remaining_capital:
                trade_plan.append({
                    'sku': rec.product_sku,
                    'marketplace': rec.marketplace,
                    'estimated_cost': estimated_cost,
                    'expected_profit': rec.expected_profit,
                    'confidence': rec.confidence_score,
                    'reasoning': rec.reasoning
                })
                remaining_capital -= estimated_cost
            else:
                logger.info(f"Skipping {rec.product_sku} - insufficient capital")
        
        logger.info(f"Trade plan: {len(trade_plan)} trades, ${available_capital - remaining_capital:.2f} allocated")
        return trade_plan


def simulate_decision_engine():
    """Test the decision engine with mock data"""
    logger.info("=== Decision Engine Simulation ===\n")
    
    # Mock opportunity
    opportunity = {
        'product': {'capacity_gb': 32, 'speed_mhz': 6000, 'type': 'DDR5'},
        'buy_from': 'newegg',
        'buy_sku': 'N82E16820242729',
        'buy_cost': 127.98,
        'sell_on': 'ebay',
        'sell_price': 164.99,
        'estimated_fees': 16.50,
        'net_profit': 20.51,
        'margin_pct': 16.0,
        'confidence': 0.75
    }
    
    engine = DecisionEngine(
        anthropic_api_key=None,  # Will use rule-based
        min_profit_threshold=20.0,
        min_confidence_threshold=0.70
    )
    
    recommendation = engine.evaluate_opportunity(
        opportunity=opportunity,
        treasury_balance=10000.0,
        current_inventory=[]
    )
    
    logger.info(f"Action: {recommendation.action}")
    logger.info(f"Confidence: {recommendation.confidence_score:.2f}")
    logger.info(f"Reasoning: {recommendation.reasoning}")
    logger.info(f"Risk: {recommendation.risk_assessment}")
    logger.info(f"Expected Profit: ${recommendation.expected_profit:.2f}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    simulate_decision_engine()
