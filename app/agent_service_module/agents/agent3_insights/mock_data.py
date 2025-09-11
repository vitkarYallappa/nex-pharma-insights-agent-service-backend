"""
Mock data for Agent 3 Insights - HTML formatted pharmaceutical market insights
"""

def get_mock_html_insight(content_context="pharmaceutical market"):
    """
    Generate a single comprehensive HTML formatted mock insight
    """
    
    html_insight = """
<div>
  <h3>Pharmaceutical Market Intelligence Analysis</h3>
  <ul>
    <li><strong>Market Expansion Accelerating</strong>: The global pharmaceutical market is experiencing unprecedented growth, with GLP-1 receptor agonists leading the obesity and diabetes treatment segments at $15.2B annually.</li>
    <li><strong>Regulatory Pathway Favorable</strong>: FDA approvals for new indications are expanding market opportunities, with expedited review processes supporting faster time-to-market for innovative therapies.</li>
    <li><strong>Patient Access Challenges</strong>: Despite clinical efficacy, high treatment costs ($1,200/month average) and limited insurance coverage create significant barriers to patient access and market penetration.</li>
    <li><strong>Competitive Landscape Intensifying</strong>: Market leaders like Novo Nordisk (Ozempic/Wegovy) and Eli Lilly (Mounjaro) face increasing competition from biosimilars expected by 2026.</li>
    <li><strong>Innovation Pipeline Strong</strong>: Next-generation combination therapies and novel delivery mechanisms show promise for improved efficacy and reduced side effects in clinical trials.</li>
  </ul>
  <p><em>Strategic Recommendation: Accelerate market entry while developing comprehensive patient access programs to address affordability concerns and maximize market penetration opportunities.</em></p>
</div>
"""
    
    return html_insight.strip()

def get_mock_insights_data(content: str, request_id: str):
    """
    Generate simple mock insights data with just HTML content for MVP
    """
    
    # Generate the HTML insight
    html_insight = get_mock_html_insight()
    
    # Return simplified structure with just HTML content for MVP
    return {
        "html_content": html_insight
    } 