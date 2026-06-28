import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.io import to_html

# Load data
df_s = pd.read_csv('data/scenario_output.csv')
df_defense = pd.read_csv('data/defense_exposure.csv')
df_medical = pd.read_csv('data/medical_exposure.csv')

# Chart 1 - Sankey
node_labels = ['Taiwan','Integrated Circuits (8542)','Discrete Semiconductors (8541)','Specialized Elec. Machines (8543)','Defense / HPC','Smartphones','IoT','Automotive','Consumer / Other']
node_colors = ['#ff4444','#ff4444','#ff4444','#ff4444','#4f83ff','#888888','#888888','#888888','#888888']
ic, disc, spec = 8.883, 0.883, 0.674
fig1 = go.Figure(go.Sankey(
    node=dict(pad=20, thickness=20, line=dict(color='black', width=0.5), label=node_labels, color=node_colors),
    link=dict(source=[0,0,0,1,1,1,1,1,2,3], target=[1,2,3,4,5,6,7,8,8,8], value=[ic,disc,spec,ic*0.43,ic*0.38,ic*0.08,ic*0.06,ic*0.05,disc,spec])
))
fig1.update_layout(title_text='Taiwan Semiconductor Dependency: Flow to US End-Use Sectors', font_size=13, paper_bgcolor='#0f1117', font_color='white', height=500)

# Chart 2 - Bar (grouped, correct orientation)
categories = ['Discrete Semiconductors', 'Integrated Circuits', 'Specialized Electrical Machines']
colors = {'30-day': '#4f83ff', '60-day': '#f5a623', '90-day': '#ff6b6b'}
fig2 = go.Figure()
for scenario in ['30-day', '60-day', '90-day']:
    df_sub = df_s[df_s['scenario'] == scenario].copy()
    df_sub = df_sub.set_index('chip_category').reindex(categories).reset_index()
    fig2.add_trace(go.Bar(
        name=scenario,
        x=df_sub['chip_category'],
        y=df_sub['supply_shock_pct'],
        marker_color=colors[scenario],
        hovertemplate='<b>%{x}</b><br>Scenario: ' + scenario + '<br>Supply Shock: %{y:.1f}%<extra></extra>'
    ))
fig2.update_layout(
    barmode='group',
    title='US Semiconductor Supply Shock by Blockade Duration',
    paper_bgcolor='#0f1117',
    plot_bgcolor='#1a1d27',
    font_color='white',
    font_size=13,
    height=550,
    yaxis=dict(gridcolor='#2e3450', title='Supply Shock (%)'),
    xaxis=dict(title='Chip Category'),
    legend_title='Blockade Scenario'
)

# Chart 3 - Treemap (fixed colors and sizing)
df_defense['contract_value_billions'] = (df_defense['contract_value_usd'] / 1e9).round(2)
df_defense['exposure_billions'] = (df_defense['exposure_score'] / 1e9).round(2)
df_defense['taiwan_dependency_pct_display'] = (df_defense['taiwan_dependency_pct'] * 100).round(1)
df_defense = df_defense.sort_values('exposure_score', ascending=False)

fig3 = go.Figure(go.Treemap(
    labels=df_defense['program_name'].tolist(),
    parents=['']*len(df_defense),
    values=df_defense['contract_value_usd'].tolist(),
    marker=dict(
        colors=df_defense['exposure_score'].tolist(),
        colorscale=[[0,'#1a2540'],[0.5,'#4f83ff'],[1,'#ff4444']],
        showscale=True,
        colorbar=dict(title='Exposure Score ($)')
    ),
    customdata=df_defense[['contract_value_billions','exposure_billions','taiwan_dependency_pct_display','naics_description']].values,
    texttemplate='<b>%{label}</b><br>$%{customdata[0]}B',
    hovertemplate='<b>%{label}</b><br>Contract Value: $%{customdata[0]}B<br>Exposure Score: $%{customdata[1]}B<br>Taiwan Dependency: %{customdata[2]}%<br>NAICS: %{customdata[3]}<extra></extra>',
    textfont=dict(size=13)
))
fig3.update_layout(
    title='DoD Defense Contractor Taiwan Exposure — FY2024 Contract Value',
    paper_bgcolor='#0f1117',
    font_color='white',
    font_size=13,
    height=600
)

# Chart 4 - Heatmap
scenarios_list = ['30-day', '60-day', '90-day']
disruption_rates = [0.40, 0.65, 0.85]
buffer_factors = [0.50, 0.25, 0.00]
heatmap_data = []
annotations = []
for i, (scenario, dr, bf) in enumerate(zip(scenarios_list, disruption_rates, buffer_factors)):
    row = []
    for _, dev in df_medical.iterrows():
        shock = dev['taiwan_dependency_pct'] * dr * (1 - bf) * 100
        onset = int(90 * (1 - dev['taiwan_dependency_pct'] * dr * (1 - bf)))
        row.append(round(shock, 1))
        annotations.append(dict(x=dev['device_category'], y=scenario, text=f"{round(shock,1)}%<br>{onset}d", showarrow=False, font=dict(color='white', size=11)))
    heatmap_data.append(row)
fig4 = go.Figure(go.Heatmap(
    z=heatmap_data,
    x=df_medical['device_category'].tolist(),
    y=scenarios_list,
    colorscale=[[0,'#0d2820'],[0.5,'#f5a623'],[1,'#ff6b6b']],
    hovertemplate='Device: %{x}<br>Scenario: %{y}<br>Supply Shock: %{z}%<extra></extra>',
    showscale=True,
    colorbar=dict(title='Supply Shock (%)')
))
fig4.update_layout(title='Medical Device Supply Shock by Blockade Duration', paper_bgcolor='#0f1117', plot_bgcolor='#1a1d27', font_color='white', font_size=13, height=450, xaxis_title='Device Category', yaxis_title='Blockade Scenario', annotations=annotations)

# Generate divs
c1 = to_html(fig1, full_html=False, include_plotlyjs=False)
c2 = to_html(fig2, full_html=False, include_plotlyjs=False)
c3 = to_html(fig3, full_html=False, include_plotlyjs=False)
c4 = to_html(fig4, full_html=False, include_plotlyjs=False)

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>90-Day PLA Naval Blockade: Supply Chain Cascade Analysis</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
  body { background: #0f1117; color: #e8eaf6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 0; }
  .header { padding: 2rem 2rem 1rem; border-bottom: 1px solid #2e3450; }
  .header h1 { font-size: 20px; font-weight: 600; margin: 0 0 8px 0; color: #e8eaf6; }
  .header p { font-size: 13px; color: #8891b4; margin: 0; max-width: 900px; line-height: 1.6; }
  .tabs { display: flex; gap: 4px; padding: 1rem 2rem 0; border-bottom: 1px solid #2e3450; }
  .tab { padding: 8px 18px; border-radius: 6px 6px 0 0; border: 1px solid #2e3450; border-bottom: none; background: #1a1d27; color: #8891b4; cursor: pointer; font-size: 13px; }
  .tab.active { background: #22263a; color: #e8eaf6; border-color: #3d4466; }
  .tab:hover { background: #22263a; color: #e8eaf6; }
  .chart-panel { display: none; padding: 1.5rem 2rem; }
  .chart-panel.active { display: block; }
  .assumption-box { background: #1a2540; border: 1px solid #2d4080; border-radius: 8px; padding: 1rem 1.5rem; margin-bottom: 1.5rem; font-size: 13px; color: #7ea6ff; line-height: 1.7; }
  .assumption-box strong { color: #e8eaf6; }
</style>
</head>
<body>
<div class="header">
  <h1>90-Day PLA Naval Blockade: Cascade Effects on US Semiconductor-Dependent Defense and Medical Device Procurement</h1>
  <p>This dashboard models a People's Liberation Army naval blockade of the Taiwan Strait across three durations (30, 60, and 90 days), quantifying supply chain disruption across US semiconductor imports, defense procurement contracts, and medical device categories. All assumptions are explicitly documented. Analysis by Tyler Brown, Penn State University BS Security and Risk Analysis 2026.</p>
</div>
<div class="tabs">
  <div class="tab active" onclick="showTab('t1', this)">Taiwan Dependency Flow</div>
  <div class="tab" onclick="showTab('t2', this)">Blockade Scenarios</div>
  <div class="tab" onclick="showTab('t3', this)">Defense Exposure</div>
  <div class="tab" onclick="showTab('t4', this)">Medical Devices</div>
</div>
<div id="t1" class="chart-panel active">
  <div class="assumption-box"><strong>Methodology:</strong> Flow values represent average annual US imports from Taiwan (2022-2024), sourced from US Census Bureau HTS Chapter 85 data. End-use sector allocation based on TSMC 2023 Annual Report platform revenue breakdown (HPC 43%, Smartphone 38%, IoT 8%, Automotive 6%, Other 5%).</div>
  """ + c1 + """
</div>
<div id="t2" class="chart-panel">
  <div class="assumption-box"><strong>Assumptions:</strong> Supply shock formula: taiwan_import_share x disruption_rate x (1 - inventory_buffer_factor). Disruption rates: 30-day = 40%, 60-day = 65%, 90-day = 85%. Inventory buffer factors: 30-day = 0.50, 60-day = 0.25, 90-day = 0.00. Industry standard semiconductor inventory buffer: 60-90 days (SIA Factbook; chipmaker earnings calls).</div>
  """ + c2 + """
</div>
<div id="t3" class="chart-panel">
  <div class="assumption-box"><strong>Methodology:</strong> Exposure score = contract_value_usd x taiwan_dependency_pct. Taiwan dependency assigned by NAICS code based on semiconductor intensity: NAICS 334511 (navigation/guidance) and 334111 (computers) assigned 23.3% matching 8542 integrated circuit import share. Contract data: USASpending.gov FY2024 DoD contracts, NAICS 334xx.</div>
  """ + c3 + """
</div>
<div id="t4" class="chart-panel">
  <div class="assumption-box"><strong>Methodology:</strong> Medical device semiconductor dependency scored 1-5 by category based on Medtronic and Abbott 10-K supply chain disclosures (SEC EDGAR). Shortage onset = days until supply shock exceeds device inventory buffer. Patient impact severity based on device criticality and availability of manual alternatives.</div>
  """ + c4 + """
</div>
<script>
function showTab(id, el) {
  document.querySelectorAll('.chart-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  el.classList.add('active');
}
</script>
</body>
</html>"""

with open('output/taiwan_blockade_dashboard.html', 'w') as f:
    f.write(html)

print("Done. Size:", len(html), "chars")
