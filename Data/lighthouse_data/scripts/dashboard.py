import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# --- CONFIGURATION ---
DATA_PATH = Path("data/indicators/indicators_daily.parquet")
if not DATA_PATH.exists():
    DATA_PATH = Path("lighthouse_mega/data/indicators/indicators_daily.parquet")

OUTPUT_PATH = Path("dashboard_advanced.png")

# Lighthouse Institutional Palette
COLORS = {
    'bg': '#0E1117',
    'text': '#E0E0E0',
    'grid': '#252525',
    
    # Macro
    'lci': '#2389BB',       # Ocean Blue
    'mri': '#FF3333',       # Signal Red
    
    # Labor (The Jaws)
    'lfi': '#FF5252',       # Fragility (Red/Orange)
    'ldi': '#448AFF',       # Dynamism (Blue)
    'fill': '#892323',      # Warning Fill
    
    # Crypto
    'stable': '#00C853',    # Growth Green
    'btc': '#FFAB00'        # Bitcoin Gold
}

def generate_chart():
    if not DATA_PATH.exists():
        print(f"Error: Data not found at {DATA_PATH}")
        return

    # 1. Load & Filter Data
    df = pd.read_parquet(DATA_PATH)
    df = df.tail(730)  # Last 2 years

    # 2. Setup Canvas (3 Rows)
    plt.style.use('dark_background')
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 14), sharex=True)
    fig.patch.set_facecolor(COLORS['bg'])
    
    # ==========================================
    # PANEL 1: THE MACRO TRAP (Liquidity vs Risk)
    # ==========================================
    ax1.set_facecolor(COLORS['bg'])
    ax1.grid(color=COLORS['grid'], linestyle=':', linewidth=0.5)
    
    # LCI (Area)
    ax1.fill_between(df.index, df['LCI'], 0, color=COLORS['lci'], alpha=0.2)
    ax1.plot(df.index, df['LCI'], color=COLORS['lci'], linewidth=1.5, label='Liquidity Cushion (LCI)')
    
    # MRI (Line) on Twin Axis
    ax1_twin = ax1.twinx()
    ax1_twin.plot(df.index, df['MRI'], color=COLORS['mri'], linewidth=2, label='Macro Risk Index (MRI)')
    
    ax1.set_title("1. THE MACRO TRAP: Liquidity Starvation vs. Systemic Risk", 
                  fontsize=14, fontweight='bold', color=COLORS['text'], loc='left', pad=10)
    
    # ==========================================
    # PANEL 2: THE LABOR JAWS (Fragility vs Dynamism)
    # ==========================================
    ax2.set_facecolor(COLORS['bg'])
    ax2.grid(color=COLORS['grid'], linestyle=':', linewidth=0.5)
    
    # LFI (Fragility - Bad)
    ax2.plot(df.index, df['LFI'], color=COLORS['lfi'], linewidth=2, label='Labor Fragility (LFI)')
    
    # LDI (Dynamism - Good)
    ax2.plot(df.index, df['LDI'], color=COLORS['ldi'], linewidth=2, linestyle='--', label='Labor Dynamism (LDI)')
    
    # The Recession Signal (Where Fragility > Dynamism)
    ax2.fill_between(df.index, df['LFI'], df['LDI'], 
                     where=(df['LFI'] > df['LDI']), 
                     color=COLORS['fill'], alpha=0.3, interpolate=True, label='RECESSION SIGNAL (The Jaws)')
    
    ax2.set_title("2. THE LABOR JAWS: Structural Rot Beneath the Surface", 
                  fontsize=14, fontweight='bold', color=COLORS['text'], loc='left', pad=10)
    
    # ==========================================
    # PANEL 3: THE CRYPTO ESCAPE (Momentum vs Value)
    # ==========================================
    ax3.set_facecolor(COLORS['bg'])
    ax3.grid(color=COLORS['grid'], linestyle=':', linewidth=0.5)
    
    # Stablecoin Momentum
    ax3.plot(df.index, df['Stablecoin_Momentum'], color=COLORS['stable'], linewidth=2, label='Stablecoin Momentum')
    
    # BTC Valuation on Twin Axis
    ax3_twin = ax3.twinx()
    ax3_twin.plot(df.index, df['BTC_Risk_Premium'], color=COLORS['btc'], linewidth=1.5, linestyle=':', label='BTC Risk Premium')
    
    ax3.set_title("3. THE CRYPTO ESCAPE: Offshore Re-Leveraging", 
                  fontsize=14, fontweight='bold', color=COLORS['text'], loc='left', pad=10)

    # ==========================================
    # FINAL STYLING
    # ==========================================
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))
    
    # Add Legends
    for ax, tw in [(ax1, ax1_twin), (ax3, ax3_twin)]:
        l1, lab1 = ax.get_legend_handles_labels()
        l2, lab2 = tw.get_legend_handles_labels()
        ax.legend(l1+l2, lab1+lab2, loc='upper left', frameon=False, fontsize=9)
        
    # Middle panel legend (single axis)
    ax2.legend(loc='upper left', frameon=False, fontsize=9)

    # IMPORTANT: Reserve bottom 5% of figure for watermark
    plt.tight_layout(rect=[0, 0.05, 1, 1])

    # Watermark (Safe Version)
    fig.text(0.5, 0.02, "LIGHTHOUSE MACRO | MACRO, ILLUMINATED.", 
             ha='center', color=COLORS['text'], alpha=0.4, fontsize=12, weight='bold')

    plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches='tight')
    print(f"Advanced Dashboard generated: {OUTPUT_PATH.resolve()}")

if __name__ == "__main__":
    generate_chart()
